"""
praxis_eval.py
Five-Property Trustworthiness Evaluation. Shared code for the four graded models.
Follows Pre-Specification revision 3 and Chapter 3 of the praxis.

Every model is run and graded by this one file, so the four models get the same 400 cases, the same
388 descriptions, the same five folds, the same confidence definition and the same scoring code.

How to run in Colab (one notebook per model, in any order, in separate sessions if the GPU is small):
    RUN_1_tfidf_retrieval.ipynb
    RUN_2_zeroshot.ipynb
    RUN_3_finetuned_2ep.ipynb
    RUN_4_finetuned_8ep.ipynb
    BUILD_four_model_tables.ipynb          # after all four have finished
Each notebook writes this file to disk and imports it, so all five use the same code.

Put avey_benchmark_MASTER.json and the candidate descriptions JSON in the same folder first.
Each run notebook saves the full similarity matrix for the model (cases x 388 candidates, clean input and
all ten perturbation conditions), then grades the model from that saved file and writes its five-property
table. Running a notebook again re-grades from the saved file without re-running the model.

Parts 1 to 3 below are the scoring, perturbation and model code of FIVE_PROPERTY_EVALUATION.ipynb, unchanged.
Parts 4 to 8 are new in revision 3: saved similarity matrices, out-of-sample recalibration, three-level
grades, three verdicts, and the sensitivity analyses.
"""
import os, sys, re, json, math, random, gc, glob, argparse, warnings
from datetime import datetime, timezone
from collections import Counter, defaultdict
from math import comb, log2, erfc, sqrt
import numpy as np, pandas as pd
from sklearn.isotonic import IsotonicRegression

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*unique classes is greater.*")

CFG = dict(
    ENCODER="pritamdeka/S-PubMedBert-MS-MARCO", MAX_SEQ_LEN=512,
    BATCH=32,            # training batch, committed hyperparameter, do not change
    ENCODE_BATCH=16,     # inference batch, memory only, safe to lower
    EPOCHS=2, LR=2e-5,   # EPOCHS is set per model by MODELS below
    K_REPORT=5, K_RETRIEVE=10, K_CONF=3,
    N_FOLDS=5, SEED_CV=42, SEED_PERT=20261102, SEED_ATTR=20261102, SEED_BOOT=20261102,
    N_BOOT=4000, ALPHA=0.05, N_BINS=10,
    GOLD_FIELD="diagnosis",
    OUTDIR="rev3_out",
)

# ---- the five pass marks, Pre-Specification revision 3 (unchanged from revision 2) ----
MARKS = dict(
    accuracy     = dict(value=0.6200, direction="min", source="Lowest of three physicians on the same 400 cases"),
    robustness   = dict(value=0.7881, direction="min", source="Physician-to-physician agreement on the same 400 cases, short or full name rule"),
    calibration  = dict(value=0.0786, direction="max", source="95th percentile of ECE for a perfectly calibrated system at n=400, 10 bins"),
    abstention   = dict(value=0.5000, direction="min", source="Workload consequence: a tool declining more than half does not reduce intake load"),
    auditability = dict(value=0.5400, direction="min", source="Chance floor: 95th percentile of a rate of one half at n=400"),
)
MATCH_RULE_MARKS = {"short name only": 0.7822, "short or full name (adopted)": 0.7881, "any gold-list entry": 0.8960}
PROPS = ["accuracy", "robustness", "calibration", "abstention", "auditability"]
GRADE_RANK = {"BELOW": 0, "AT": 1, "ABOVE": 2}

# ---- the four graded models ----
MODELS = {
    "tfidf_retrieval": dict(label="TF-IDF retrieval",             kind="tfidf",   epochs=0, attr_seed_name="tfidf_retrieval"),
    "zeroshot":        dict(label="Encoder, no fine-tuning",      kind="encoder", epochs=0, attr_seed_name="zeroshot"),
    "finetuned_2ep":   dict(label="Encoder, fine-tuned 2 epochs", kind="encoder", epochs=2, attr_seed_name="finetuned"),
    "finetuned_8ep":   dict(label="Encoder, fine-tuned 8 epochs", kind="encoder", epochs=8, attr_seed_name="finetuned_8ep"),
}

# ---- recalibration procedures (Section 3.12). The grades use out_of_sample (Section 3.4). ----
ARMS = ["as_first_run", "out_of_sample", "isotonic"]
GRADED_ARM = "out_of_sample"
ARM_LABEL = {"as_first_run": "Temperature fitted on training folds, as first run",
             "out_of_sample": "Temperature fitted out of sample, Section 3.4",
             "isotonic": "Isotonic regression, fitted out of sample"}

# ---- perturbation conditions. All ten are run. Four are registered, six are the severity gradient. ----
REGISTERED = {"remove 2 findings": "removing", "reword 100%": "preserving",
              "fragment complete": "preserving", "vague moderate": "preserving"}
PRESERVING = [c for c, t in REGISTERED.items() if t == "preserving"]
ALL_CONDITIONS = ["original",
                  "remove 1 finding", "remove 2 findings", "remove 3 findings",
                  "reword 25%", "reword 50%", "reword 100%",
                  "fragment partial", "fragment complete",
                  "vague moderate", "vague high"]
FAMILY = {"remove 1 finding": "Removal", "remove 2 findings": "Removal", "remove 3 findings": "Removal",
          "reword 25%": "Rewording", "reword 50%": "Rewording", "reword 100%": "Rewording",
          "fragment partial": "Fragmentation", "fragment complete": "Fragmentation",
          "vague moderate": "Vagueness", "vague high": "Vagueness"}
DOCS = ["MA", "TH", "NJ"]   # the three physicians in the benchmark file
CASES = CASE_INFO = CANDIDATES = CAND_TEXT = CAND_IX = TEXT = HARD = None

# =====================================================================================
# PART 1. Scoring and statistics (unchanged from the notebook)
# =====================================================================================
def norm(s): return " ".join(str(s).lower().strip().split())
def rank_of(r,t):
    try: return r.index(t)+1
    except ValueError: return None
def hit_at_k(r,t,k):
    x = rank_of(r,t); return bool(x is not None and x<=k)

def softmax(s, tau):
    z = np.asarray(s,float)/max(tau,1e-6); z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z); return e/e.sum(axis=-1, keepdims=True)

def topk_conf(S, tau, k=None):
    k = k or CFG["K_CONF"]
    return np.sort(softmax(S,tau), axis=1)[:,-k:].sum(axis=1)

def fit_temperature(S, gold_idx, lo=0.001, hi=10.0, iters=120):
    """Golden-section search on tau, minimising NLL of the true class on TRAINING cases."""
    S = np.asarray(S,float); gold_idx = np.asarray(gold_idx,int)
    ok = gold_idx>=0; S = S[ok]; gold_idx = gold_idx[ok]
    if len(S)==0: return 1.0
    def nll(tau):
        P = softmax(S,tau)
        return float(-np.mean(np.log(np.clip(P[np.arange(len(P)),gold_idx],1e-12,None))))
    gr=(sqrt(5)-1)/2; a,b=lo,hi; c,d=b-gr*(b-a), a+gr*(b-a)
    for _ in range(iters):
        if nll(c)<nll(d): b=d
        else: a=c
        c,d = b-gr*(b-a), a+gr*(b-a)
        if abs(b-a)<1e-5: break
    tau=float((a+b)/2)
    if tau<=lo*1.01 or tau>=hi*0.99:
        print(f"   WARNING: fitted tau = {tau:.5f} sits on the search boundary.")
    return tau

def ece_bins(conf, correct, n_bins=None):
    n_bins = n_bins or CFG["N_BINS"]
    conf=np.asarray(conf,float); y=np.asarray(correct,float)
    o=np.argsort(conf); conf,y = conf[o], y[o]
    e=0.0; rows=[]
    for b in np.array_split(np.arange(len(conf)), n_bins):
        if len(b)==0: continue
        c=conf[b].mean(); a=y[b].mean(); w=len(b)/len(conf)
        e += w*abs(a-c)
        rows.append(dict(n=len(b), mean_confidence=c, observed_accuracy=a, gap=a-c))
    return float(e), pd.DataFrame(rows)

def auroc(score, correct):
    s=np.asarray(score,float); y=np.asarray(correct,bool)
    n1=int(y.sum()); n0=int(len(y)-n1)
    if n1==0 or n0==0: return float("nan")
    r=pd.Series(s).rank().values
    return float((r[y].sum()-n1*(n1+1)/2)/(n1*n0))

def brier(conf, correct):
    return float(np.mean((np.asarray(conf,float)-np.asarray(correct,float))**2))

def wilson(k, n, alpha=None):
    """Wilson score interval for a proportion. Stable at the extremes, unlike normal approx."""
    alpha = alpha or CFG["ALPHA"]
    if n==0: return (float("nan"), float("nan"))
    from statistics import NormalDist
    z = NormalDist().inv_cdf(1-alpha/2)
    p = k/n; d = 1+z*z/n
    c = (p + z*z/(2*n))/d
    h = z*sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (max(0.0,c-h), min(1.0,c+h))

def boot_ci(x, stat=np.mean, B=None, seed=None):
    x=np.asarray(x,float); B=B or CFG["N_BOOT"]
    rng=np.random.default_rng(seed or CFG["SEED_BOOT"])
    s=[stat(x[rng.integers(0,len(x),len(x))]) for _ in range(B)]
    return float(np.percentile(s,100*CFG["ALPHA"]/2)), float(np.percentile(s,100*(1-CFG["ALPHA"]/2)))

def mcnemar(a, b):
    a,b=np.asarray(a,bool),np.asarray(b,bool)
    bb,cc=int(np.sum(a&~b)),int(np.sum(~a&b)); n=bb+cc
    p=1.0 if n==0 else min(1.0, sum(comb(n,j) for j in range(bb,n+1))*0.5**n)
    return bb,cc,n,p

# =====================================================================================
# PART 2. The perturbations (unchanged from the notebook)
# =====================================================================================
LAY = {
 "dyspnea":"trouble breathing","dyspnoea":"trouble breathing","shortness of breath":"trouble breathing",
 "dysuria":"burning when passing urine","hematuria":"blood in the urine","haematuria":"blood in the urine",
 "melena":"black tarry stools","haematemesis":"vomiting blood","hematemesis":"vomiting blood",
 "dysphagia":"trouble swallowing","odynophagia":"painful swallowing","arthralgia":"joint pain",
 "myalgia":"muscle aches","myalgias":"muscle aches","cephalgia":"headache",
 "palpitations":"heart racing","palpitation":"heart racing","syncope":"fainting","presyncope":"nearly fainting",
 "erythema":"redness","erythematous":"red","pruritus":"itching","pruritic":"itchy",
 "jaundice":"yellow skin and eyes","icterus":"yellow eyes","pallor":"looking pale",
 "edema":"swelling","oedema":"swelling","diaphoresis":"sweating","diaphoretic":"sweaty",
 "emesis":"vomiting","nausea":"feeling sick","anorexia":"loss of appetite",
 "constipation":"not able to open bowels","diarrhea":"loose stools","diarrhoea":"loose stools",
 "tenderness":"sore to touch","tender":"sore to touch","abdominal":"tummy","abdomen":"tummy",
 "epigastric":"upper tummy","periumbilical":"around the belly button","umbilicus":"belly button",
 "suprapubic":"lower tummy","flank":"side of the back","lumbar":"lower back",
 "thoracic":"chest","sternum":"breastbone","substernal":"behind the breastbone",
 "dizziness":"feeling dizzy","vertigo":"the room spinning","tinnitus":"ringing in the ears",
 "otalgia":"earache","otorrhea":"discharge from the ear","rhinorrhea":"runny nose",
 "rhinorrhoea":"runny nose","nasal congestion":"blocked nose","congestion":"blocked nose",
 "pharyngitis":"sore throat","odontalgia":"toothache","epistaxis":"nosebleed",
 "hemoptysis":"coughing up blood","haemoptysis":"coughing up blood","sputum":"phlegm",
 "productive cough":"cough bringing up phlegm","wheeze":"whistling when breathing",
 "wheezing":"whistling when breathing","orthopnea":"breathless lying flat",
 "paroxysmal nocturnal dyspnea":"waking up breathless at night",
 "claudication":"leg pain when walking","paresthesia":"pins and needles",
 "paraesthesia":"pins and needles","hypoesthesia":"numbness","numbness":"no feeling",
 "weakness":"feeling weak","fatigue":"feeling tired all the time","malaise":"feeling unwell",
 "lethargy":"no energy","pyrexia":"fever","febrile":"feverish","afebrile":"no fever",
 "rigors":"shaking chills","chills":"feeling cold and shivery","night sweats":"sweating at night",
 "polyuria":"passing urine a lot","polydipsia":"feeling very thirsty","nocturia":"getting up at night to pass urine",
 "urinary frequency":"needing to pass urine often","urgency":"needing to rush to the toilet",
 "incontinence":"leaking urine","oliguria":"passing very little urine",
 "menorrhagia":"heavy periods","dysmenorrhea":"painful periods","amenorrhea":"periods stopped",
 "dyspareunia":"pain during sex","vaginal discharge":"discharge from the vagina",
 "lesion":"mark on the skin","lesions":"marks on the skin","macule":"flat spot","papule":"small bump",
 "vesicle":"small blister","pustule":"pus-filled spot","urticaria":"hives","rash":"rash",
 "lymphadenopathy":"swollen glands","hepatomegaly":"enlarged liver","splenomegaly":"enlarged spleen",
 "ascites":"fluid in the tummy","distension":"bloating","distention":"bloating","bloating":"feeling bloated",
 "exacerbated":"made worse","exacerbation":"flare-up","alleviated":"made better","radiating":"spreading",
 "radiates":"spreads","intermittent":"comes and goes","persistent":"keeps going","acute":"sudden",
 "chronic":"long-standing","bilateral":"on both sides","unilateral":"on one side",
 "proximal":"nearer the body","distal":"further from the body","extremities":"arms and legs",
 "lower extremities":"legs","upper extremities":"arms","visual disturbance":"trouble seeing",
 "blurred vision":"blurry sight","diplopia":"double vision","photophobia":"light hurting the eyes",
 "loss of consciousness":"blacking out","consciousness":"being aware","seizure":"a fit",
 "tremor":"shaking","stiffness":"feeling stiff","hypertension":"high blood pressure",
 "hypotension":"low blood pressure","tachycardia":"fast heartbeat","bradycardia":"slow heartbeat",
 "weight loss":"losing weight","weight gain":"putting on weight","dehydration":"being dried out",
 "trauma":"an injury","onset":"when it started","duration":"how long it lasted","severity":"how bad it is",
 "aggravating":"what makes it worse","relieving":"what makes it better","denies":"says no to",
 "complains of":"says they have","presents with":"comes in with","reports":"says",
}
VAGUE_MOD = {
 r"\b\d+\s*(day|days)\b":"a few days", r"\b\d+\s*(week|weeks)\b":"a few weeks",
 r"\b\d+\s*(month|months)\b":"a few months", r"\b\d+\s*(year|years)\b":"a long time",
 r"\b\d+\s*(hour|hours)\b":"a few hours", r"\bsevere\b":"bad", r"\bmoderate\b":"not too bad",
 r"\bmild\b":"a bit", r"\bsharp\b":"bad", r"\bdull\b":"odd", r"\bburning\b":"funny",
 r"\bthrobbing\b":"bad", r"\bconstant\b":"most of the time", r"\bintermittent\b":"on and off",
 r"\bright upper quadrant\b":"up on one side", r"\bleft upper quadrant\b":"up on one side",
 r"\bright lower quadrant\b":"down on one side", r"\bleft lower quadrant\b":"down on one side",
 r"\bepigastri\w*\b":"top of the tummy", r"\bperiumbilical\b":"middle of the tummy",
}
VAGUE_HIGH = dict(VAGUE_MOD); VAGUE_HIGH.update({
 r"\b\d+\b":"some", r"\bmorning\b":"sometimes", r"\bnight\b":"sometimes", r"\bevening\b":"sometimes",
 r"\bchest\b":"up top", r"\babdominal\b":"tummy", r"\babdomen\b":"tummy", r"\bback\b":"behind",
 r"\bradiat\w+\b":"goes somewhere else", r"\bworsening\b":"getting worse",
 r"\bgradual\w*\b":"slowly", r"\bsudden\w*\b":"all at once",
})
FRAG_DROP = set("""a an the is are was were be been being am do does did has have had
he she it they him her them his hers its their there here that this those these
of to in on at by for with from as and or but so then than when while which who whom
i you we us our your my me""".split())

PERTURBABLE = ["chief_complaints","presentation","physical_history","family_history"]
UNTOUCHED   = ["physical_examination","absent_findings"]
PLACEHOLDER = {"", "-", "--", "none", "nil", "n/a"}
FIELDS = ["chief_complaints","presentation","physical_examination",
          "physical_history","family_history","absent_findings"]

def is_blank(t): return str(t or "").strip().lower() in PLACEHOLDER
def split_findings(text):
    if is_blank(text): return []
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", str(text).strip()) if p.strip()]
def enumerate_findings(vig):
    return [(f,i,s) for f in PERTURBABLE for i,s in enumerate(split_findings(vig.get(f)))]
def drop_finding(vig, field, idx):
    out=dict(vig); segs=split_findings(vig.get(field))
    kept=[s for i,s in enumerate(segs) if i!=idx]
    out[field]=" ".join(kept) if kept else "-"
    return out
def build_text(v):
    head=f"{v.get('age')} {v.get('age_format','year')} old {v.get('sex','')}".strip()
    return "  ".join([head]+[str(v.get(f) or "").strip() for f in FIELDS]).strip()
def resolve_gold(c):
    dl=[norm(x) for x in c["gold_standard"]["differential_list"]]
    if not dl: return None,[]
    pr = dl[0] if CFG["GOLD_FIELD"]=="differential_list[0]" else norm(c["diagnosis"])
    return pr, [pr]+[x for x in dl if x!=pr]

def apply_removal(vig, n, rng):
    out=dict(vig)
    pool=[(f,i) for f in PERTURBABLE for i in range(len(split_findings(vig.get(f))))]
    if not pool: return out
    drop=set(rng.sample(pool, min(n,len(pool))))
    for f in PERTURBABLE:
        segs=split_findings(vig.get(f))
        if not segs: continue
        kept=[s for i,s in enumerate(segs) if (f,i) not in drop]
        out[f]=" ".join(kept) if kept else "-"
    return out

_LAY_RE = sorted(LAY.items(), key=lambda kv: -len(kv[0]))
def apply_reword(vig, pct, rng):
    out=dict(vig)
    for f in PERTURBABLE:
        t=str(vig.get(f) or "")
        if is_blank(t): continue
        for term,lay in _LAY_RE:
            t=re.sub(r"\b%s\b"%re.escape(term), lambda m: lay if rng.random()<pct else m.group(0), t, flags=re.I)
        out[f]=t
    return out

def apply_fragment(vig, share, rng):
    out=dict(vig)
    for f in PERTURBABLE:
        segs=split_findings(vig.get(f))
        if not segs: continue
        new=[]
        for s in segs:
            if rng.random()<share:
                new.append(" ".join(w for w in re.findall(r"[A-Za-z0-9'%/.-]+", s)
                                    if w.lower() not in FRAG_DROP).lower())
            else: new.append(s)
        out[f]=" ".join(new)
    return out

def apply_vague(vig, rules, rng):
    out=dict(vig)
    for f in PERTURBABLE:
        t=str(vig.get(f) or "")
        if is_blank(t): continue
        for pat,rep in rules.items(): t=re.sub(pat,rep,t,flags=re.I)
        out[f]=t
    return out

def perturb(vig, condition, case_number):
    rng=random.Random(f"{CFG['SEED_PERT']}|{case_number}|{condition}")
    if condition=="original":          return dict(vig)
    if condition.startswith("remove"): return apply_removal(vig,int(re.search(r"\d+",condition).group()),rng)
    if condition.startswith("reword"): return apply_reword(vig,int(re.search(r"\d+",condition).group())/100,rng)
    if condition=="fragment partial":  return apply_fragment(vig,0.5,rng)
    if condition=="fragment complete": return apply_fragment(vig,1.0,rng)
    if condition=="vague moderate":    return apply_vague(vig,VAGUE_MOD,rng)
    if condition=="vague high":        return apply_vague(vig,VAGUE_HIGH,rng)
    raise ValueError(condition)

# =====================================================================================
# PART 3. The models (unchanged from the notebook)
# =====================================================================================
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.model_selection import StratifiedKFold

def _free():
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache(); torch.cuda.ipc_collect()
    except Exception:
        pass

class TfidfRetrieval:
    """Keyword search. Ranks the same 388 descriptions by TF-IDF cosine similarity."""
    name="tfidf_retrieval"; needs_gpu=False
    def fit(self, fold, texts, labels):
        self.vec = TfidfVectorizer(ngram_range=(1,2), min_df=1, sublinear_tf=True,
                                   stop_words="english").fit(list(texts)+CAND_TEXT)
        self.C = normalize(self.vec.transform(CAND_TEXT))      # 388 x V, sparse
        return self
    def sims(self, texts):
        return (normalize(self.vec.transform(list(texts))) @ self.C.T).toarray()
    def sims_to(self, texts, j):
        return np.asarray((normalize(self.vec.transform(list(texts))) @ self.C[j].T).todense()).ravel()
    def release(self):
        self.vec=None; self.C=None; _free()

class BiEncoder:
    """PubMedBERT bi-encoder. finetune=False is the zero-shot arm."""
    def __init__(self, finetune):
        self.finetune=finetune
        self.name="finetuned" if finetune else "zeroshot"
        self.needs_gpu=True
        self.m=None
    def _load_base(self):
        from sentence_transformers import SentenceTransformer
        m=SentenceTransformer(CFG["ENCODER"]); m.max_seq_length=CFG["MAX_SEQ_LEN"]
        return m
    def fit(self, fold, texts, labels):
        if self.finetune:
            from sentence_transformers import InputExample, losses
            from torch.utils.data import DataLoader
            import torch; torch.manual_seed(CFG["SEED_CV"])
            self.release()
            self.m=self._load_base()
            lut=dict(zip(CANDIDATES,CAND_TEXT))
            ex=[InputExample(texts=[q,lut[y]]) for q,y in zip(texts,labels) if y in lut]
            dl=DataLoader(ex, shuffle=True, batch_size=CFG["BATCH"], drop_last=True)
            self.m.fit(train_objectives=[(dl, losses.MultipleNegativesRankingLoss(self.m))],
                       epochs=CFG["EPOCHS"], warmup_steps=int(0.1*len(dl)*CFG["EPOCHS"]),
                       optimizer_params={"lr":CFG["LR"]}, show_progress_bar=False)
            del ex, dl; _free()
            self.C=self._encode(CAND_TEXT)
        else:
            if self.m is None:                 # load once, reuse for every fold
                self.m=self._load_base()
                self.C=self._encode(CAND_TEXT)
        return self
    def _encode(self, texts):
        import torch
        with torch.inference_mode():
            return self.m.encode(list(texts), normalize_embeddings=True,
                                 batch_size=CFG["ENCODE_BATCH"], show_progress_bar=False)
    def sims(self, texts):   return self._encode(texts) @ self.C.T
    def sims_to(self, texts, j): return self._encode(texts) @ self.C[j]
    def release(self):
        if self.m is not None:
            try: self.m.to("cpu")
            except Exception: pass
        self.m=None; self.C=None; _free()

# =====================================================================================
# PART 4. Data, case table, candidate pool, difficulty labels
# =====================================================================================
def _find(pats, pool, skip=()):
    for f in pool:
        low = os.path.basename(f).lower()
        if f in skip or "provenance" in low: continue
        if any(p in low for p in pats): return f
    return None

def load_data(data_path=None, desc_path=None):
    """Load the benchmark and the 388 descriptions, and build everything the models share."""
    global CASES, CASE_INFO, CANDIDATES, CAND_TEXT, CAND_IX, TEXT, HARD
    pool = sorted(glob.glob("*.json")) + sorted(glob.glob("data/*.json")) + sorted(glob.glob("data/descriptions/*.json"))
    desc_path = desc_path or _find(("descri",), pool)
    data_path = data_path or _find(("avey", "benchmark", "master", "vignette"), pool, skip=(desc_path,) if desc_path else ())
    if not data_path or not desc_path:
        raise FileNotFoundError("Put avey_benchmark_MASTER.json and the candidate descriptions JSON in this folder, "
                                "or pass --data and --descriptions.")
    CASES = json.load(open(data_path, encoding="utf-8"))["cases"]
    descriptions = json.load(open(desc_path, encoding="utf-8"))
    med = int(np.median([len(str(v).split()) for v in descriptions.values()]))
    if med < 8: raise ValueError(f"descriptions look label-only (median {med} words). Wrong file.")
    rows = []
    for c in CASES:
        pr, gold = resolve_gold(c)
        if not gold: continue
        rows.append(dict(case_number=c["case_number"], primary=pr, gold=gold,
                         classification=c["classification"], vignette=c["vignette"]))
    CASE_INFO = pd.DataFrame(rows)
    desc = {norm(k): v for k, v in descriptions.items()}
    CANDIDATES = sorted({d for g in CASE_INFO.gold for d in g})
    CAND_TEXT = [f"{c}. {desc[c]}" if desc.get(c) else c for c in CANDIDATES]
    CAND_IX = {c: i for i, c in enumerate(CANDIDATES)}
    missing = sum(1 for c in CANDIDATES if not desc.get(c))
    TEXT = {}
    for _, r in CASE_INFO.iterrows():
        for cond in ALL_CONDITIONS:
            TEXT[(r.case_number, cond)] = build_text(perturb(r.vignette, cond, r.case_number))
    hard = []
    for c in CASES:
        pr, gold = resolve_gold(c)
        if not gold: continue
        dh = sum(1 for d in DOCS if pr in [norm(x) for x in (c["predictions_normalized"].get(d) or [])][:3])
        hard.append(dict(case_number=c["case_number"], doctors_correct=dh,
                         difficulty={3: "easy (3/3)", 2: "moderate (2/3)", 1: "hard (1/3)", 0: "very hard (0/3)"}[dh]))
    HARD = pd.DataFrame(hard)
    print(f"data: {len(CASE_INFO)} cases, {len(CANDIDATES)} candidates, {missing} without a description, "
          f"{len(ALL_CONDITIONS)} conditions")
    print(f"files: {os.path.basename(data_path)} | {os.path.basename(desc_path)}")
    return data_path, desc_path

def folds():
    skf = StratifiedKFold(n_splits=CFG["N_FOLDS"], shuffle=True, random_state=CFG["SEED_CV"])
    return list(skf.split(CASE_INFO, CASE_INFO.classification))

# =====================================================================================
# PART 5. Run one model and save its similarity matrices
# =====================================================================================
def sims_path(model): return os.path.join(CFG["OUTDIR"], f"sims_{model}.npz")
def attr_path(model): return os.path.join(CFG["OUTDIR"], f"attribution_{model}.json")

def run_model(model, force=False):
    """Fit the model on each training fold and save the full similarity matrix (cases x 388 candidates)
    for the clean input and every perturbation condition. Nothing is graded here."""
    spec = MODELS[model]; os.makedirs(CFG["OUTDIR"], exist_ok=True)
    if os.path.exists(sims_path(model)) and os.path.exists(attr_path(model)) and not force:
        print(f"[{model}] saved similarity matrices found. Skipping the run. Use --force to run again."); return
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CFG["EPOCHS"] = spec["epochs"]
    arm = TfidfRetrieval() if spec["kind"] == "tfidf" else BiEncoder(finetune=spec["epochs"] > 0)
    n = len(CASE_INFO); case_numbers = CASE_INFO.case_number.values
    S_all = {c: None for c in ALL_CONDITIONS}; fold_of = np.zeros(n, int); store = {}; attr = {}
    vig = CASE_INFO.set_index("case_number").vignette
    for fold, (tr, te) in enumerate(folds(), start=1):
        ck = os.path.join(CFG["OUTDIR"], f"_ckpt_{model}_fold{fold}.npz")
        cka = os.path.join(CFG["OUTDIR"], f"_ckpt_{model}_fold{fold}.json")
        if os.path.exists(ck) and os.path.exists(cka) and not force:
            z = np.load(ck); part = {k: z[k] for k in z.files}; fattr = json.load(open(cka))
            print(f"   fold {fold}: restored from checkpoint")
        else:
            trd = CASE_INFO.iloc[tr]; ted = CASE_INFO.iloc[te]
            tr_text = [TEXT[(cn, "original")] for cn in trd.case_number]
            arm.fit(fold, tr_text, list(trd.primary))
            part = {"S_train": np.asarray(arm.sims(tr_text))}
            te_cn = list(ted.case_number)
            for cond in ALL_CONDITIONS:
                part["S|" + cond] = np.asarray(arm.sims([TEXT[(cn, cond)] for cn in te_cn]))
            # ---- attribution on the clean text: credited finding against one random finding ----
            S0 = part["S|original"]; pred_ix = np.argsort(-S0, axis=1)[:, 0]
            rng = random.Random(f"{CFG['SEED_ATTR']}|{spec['attr_seed_name']}|fold{fold}")
            fattr = {}
            for i, cn in enumerate(te_cn):
                f = enumerate_findings(vig.loc[cn])
                if len(f) < 2:
                    fattr[str(cn)] = dict(attr_field=None, attr_idx=None, attr_text=None, d_attr=None, d_rand=None,
                                          n_findings=len(f)); continue
                sim = arm.sims_to([s for _, _, s in f], int(pred_ix[i]))
                a = int(np.argmax(sim)); b = rng.choice([j for j in range(len(f)) if j != a])
                fa, ia, ta = f[a]; fb, ib, _ = f[b]
                base = float(S0[i, pred_ix[i]])
                sa = float(arm.sims_to([build_text(drop_finding(vig.loc[cn], fa, ia))], int(pred_ix[i]))[0])
                sb = float(arm.sims_to([build_text(drop_finding(vig.loc[cn], fb, ib))], int(pred_ix[i]))[0])
                fattr[str(cn)] = dict(attr_field=fa, attr_idx=ia, attr_text=str(ta)[:120], d_attr=base - sa,
                                      d_rand=base - sb, n_findings=len(f))
            np.savez_compressed(ck, **part); json.dump(fattr, open(cka, "w"))
            print(f"   fold {fold}: {len(te)} held-out cases x {len(ALL_CONDITIONS)} conditions saved")
        for cond in ALL_CONDITIONS:
            if S_all[cond] is None: S_all[cond] = np.zeros((n, part["S|" + cond].shape[1]), part["S|" + cond].dtype)
            S_all[cond][te] = part["S|" + cond]
        fold_of[te] = fold; store[f"S_train_f{fold}"] = part["S_train"]; store[f"train_idx_f{fold}"] = np.asarray(tr)
        attr.update(fattr)
    arm.release()
    np.savez_compressed(sims_path(model), fold=fold_of, case_number=case_numbers,
                        **{"S|" + c: S_all[c] for c in ALL_CONDITIONS}, **store)
    json.dump(dict(model=model, run_id=run_id, settings={k: str(v) for k, v in CFG.items()}, spec=spec,
                   candidates=CANDIDATES, attribution=attr), open(attr_path(model), "w"))
    print(f"[{model}] run id {run_id}. Saved {os.path.basename(sims_path(model))}")

# =====================================================================================
# PART 6. Recalibration. Three procedures. The second is the one the grades use (Section 3.4).
# =====================================================================================
def _top3_event_nll(S, y, tau):
    p = np.clip(topk_conf(S, tau), 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

def fit_temperature_top3(S, y, lo=0.001, hi=10.0):
    """One temperature, fitted by minimising the negative log-likelihood of the top-three event.
    A grid in log space finds the region, then a golden-section search refines it."""
    S = np.asarray(S, float); y = np.asarray(y, float)
    grid = np.exp(np.linspace(np.log(lo), np.log(hi), 200))
    vals = [_top3_event_nll(S, y, t) for t in grid]; j = int(np.argmin(vals))
    a, b = grid[max(j - 1, 0)], grid[min(j + 1, len(grid) - 1)]
    gr = (sqrt(5) - 1) / 2; c, d = b - gr * (b - a), a + gr * (b - a)
    for _ in range(80):
        if _top3_event_nll(S, y, c) < _top3_event_nll(S, y, d): b = d
        else: a = c
        c, d = b - gr * (b - a), a + gr * (b - a)
        if abs(b - a) < 1e-7: break
    return float((a + b) / 2)

def confidences(Z, hit3):
    """Case confidence under the three procedures, for every condition.
    as_first_run   : temperature fitted on the fold's own training cases, reference diagnosis
    out_of_sample  : temperature fitted on the held-out predictions of the other four folds, top-three event
    isotonic       : free monotone map of the out-of-sample confidence, fitted on the other four folds"""
    fold = Z["fold"]; y = hit3["original"].astype(float); n = len(fold)
    conf = {a: {c: np.zeros(n) for c in ALL_CONDITIONS} for a in ARMS}; taus = {a: {} for a in ARMS[:2]}
    for k in sorted(set(fold)):
        te = fold == k; other = ~te
        tr_idx = Z[f"train_idx_f{k}"]
        gold_tr = [CAND_IX.get(p, -1) for p in CASE_INFO.primary.values[tr_idx]]
        taus["as_first_run"][k] = fit_temperature(Z[f"S_train_f{k}"], gold_tr)
        taus["out_of_sample"][k] = fit_temperature_top3(Z["S|original"][other], y[other])
        for c in ALL_CONDITIONS:
            for a in ARMS[:2]:
                conf[a][c][te] = topk_conf(Z["S|" + c][te], taus[a][k])
    for k in sorted(set(fold)):
        te = fold == k; other = ~te
        iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip").fit(conf["out_of_sample"]["original"][other], y[other])
        for c in ALL_CONDITIONS:
            conf["isotonic"][c][te] = iso.predict(conf["out_of_sample"][c][te])
    return conf, taus

# =====================================================================================
# PART 7. The five properties, the grades and the verdict
# =====================================================================================
def grade_of(lo, hi, mark, direction):
    """BELOW: whole interval on the wrong side. ABOVE: whole interval on the right side. AT: interval contains the mark."""
    if direction == "min": return "BELOW" if hi < mark else ("ABOVE" if lo > mark else "AT")
    return "BELOW" if lo > mark else ("ABOVE" if hi < mark else "AT")

def verdict_of(grades):
    g = list(grades)
    if "BELOW" in g: return "NOT FIT FOR USE"
    return "FIT FOR USE" if all(x == "ABOVE" for x in g) else "NOT ESTABLISHED"

def ece_ci(conf, y):
    """Bootstrap percentile interval over cases. Each resample draws n case indices with replacement
    and recomputes the expected calibration error on the paired confidence and outcome."""
    conf = np.asarray(conf, float); y = np.asarray(y, float); n = len(y)
    rng = np.random.default_rng(CFG["SEED_BOOT"]); s = np.empty(CFG["N_BOOT"])
    for b in range(CFG["N_BOOT"]):
        i = rng.integers(0, n, n); s[b] = ece_bins(conf[i], y[i])[0]
    return float(np.percentile(s, 100 * CFG["ALPHA"] / 2)), float(np.percentile(s, 100 * (1 - CFG["ALPHA"] / 2)))

def noise_floor(conf, reps=4000):
    """Expected calibration error a perfectly calibrated model would show with these same confidence values.
    Reported beside the grade as a check. It is not the pass mark."""
    conf = np.asarray(conf, float); rng = np.random.default_rng(CFG["SEED_BOOT"]); s = np.empty(reps)
    for b in range(reps): s[b] = ece_bins(conf, (rng.random(len(conf)) < conf).astype(float))[0]
    return float(s.mean()), float(np.percentile(s, 95))

def abstention(conf, y):
    n = len(y); o = np.argsort(-np.asarray(conf, float)); yy = np.asarray(y, bool)[o]
    acc = np.cumsum(yy) / np.arange(1, n + 1); ok = np.where(acc >= MARKS["accuracy"]["value"])[0]
    k = int(ok.max() + 1) if len(ok) else 0
    return k, acc

def prop(value, lo, hi, name, **extra):
    m = MARKS[name]; return dict(value=float(value), lo=float(lo), hi=float(hi), mark=m["value"], direction=m["direction"],
                                 grade=grade_of(lo, hi, m["value"], m["direction"]), **extra)

def sign_test_p(w, m):
    return float(sum(comb(m, j) for j in range(w, m + 1)) / 2 ** m) if m else float("nan")

def need_n(k, n, mark):
    """Smallest count of correct-on-clean cases at which the Wilson lower bound would clear the mark, at the observed rate."""
    r = k / n if n else 0.0
    if r <= mark: return None
    m = n
    while wilson(r * m, m)[0] <= mark and m < 200000: m += 1
    return m

def grade_model(model):
    Z = dict(np.load(sims_path(model))); meta = json.load(open(attr_path(model)))
    assert meta["candidates"] == CANDIDATES, "candidate pool differs from the one this run used"
    n = len(CASE_INFO); prim_ix = np.array([CAND_IX[p] for p in CASE_INFO.primary])
    order = {c: np.argsort(-Z["S|" + c], axis=1) for c in ALL_CONDITIONS}
    rank = {c: np.array([int(np.where(order[c][i] == prim_ix[i])[0][0]) + 1 for i in range(n)]) for c in ALL_CONDITIONS}
    hit = {k: {c: rank[c] <= k for c in ALL_CONDITIONS} for k in (1, 3, 5)}
    y = hit[3]["original"]; conf, taus = confidences(Z, hit[3])
    out = dict(model=model, label=MODELS[model]["label"], run_id=meta["run_id"], n=n,
               temperatures={a: {str(k): v for k, v in t.items()} for a, t in taus.items()})

    # ---- 1 accuracy
    k3 = int(y.sum()); lo, hi = wilson(k3, n)
    P = {"accuracy": prop(k3 / n, lo, hi, "accuracy", count=k3, of=n, M1=float(hit[1]["original"].mean()), M5=float(hit[5]["original"].mean()))}
    # ---- 2 robustness: correct on clean and still correct after every information-preserving condition
    held = int((y & np.all([hit[3][c] for c in PRESERVING], axis=0)).sum()); lo, hi = wilson(held, k3)
    P["robustness"] = prop(held / k3 if k3 else float("nan"), lo, hi, "robustness", count=held, of=k3,
                           cases_needed_to_clear_mark=need_n(held, k3, MARKS["robustness"]["value"]))
    # ---- 3 calibration and 4 abstention, under each recalibration procedure
    arms = {}
    for a in ARMS:
        c0 = conf[a]["original"]; e, bins = ece_bins(c0, y); lo, hi = ece_ci(c0, y); nf = noise_floor(c0)
        cal = prop(e, lo, hi, "calibration", brier=brier(c0, y), auroc=auroc(c0, y), noise_floor_mean=nf[0], noise_floor_p95=nf[1],
                   bins=bins.round(4).to_dict("records"))
        k, acc = abstention(c0, y); lo, hi = wilson(k, n)
        ab = prop(k / n, lo, hi, "abstention", count=k, of=n)
        arms[a] = dict(calibration=cal, abstention=ab, risk_coverage=[round(float(x), 4) for x in acc])
    P["calibration"] = arms[GRADED_ARM]["calibration"]; P["abstention"] = arms[GRADED_ARM]["abstention"]
    # ---- 5 auditability
    A = [meta["attribution"][str(cn)] for cn in CASE_INFO.case_number]
    da = np.array([np.nan if a["d_attr"] is None else a["d_attr"] for a in A]); dr = np.array([np.nan if a["d_rand"] is None else a["d_rand"] for a in A])
    ok = ~np.isnan(da); w = int((da[ok] > dr[ok]).sum()); m = int(ok.sum()); lo, hi = wilson(w, m)
    P["auditability"] = prop(w / m, lo, hi, "auditability", count=w, of=m, ties=int((da[ok] == dr[ok]).sum()), sign_test_p=sign_test_p(w, m))
    out["properties"] = P; out["arms"] = arms
    out["verdict"] = verdict_of(P[p]["grade"] for p in PROPS)
    out["below"] = [p for p in PROPS if P[p]["grade"] == "BELOW"]

    # ---- degraded input: accuracy, calibration and abstention again, with the temperature fitted on clean input
    deg = {}
    for c in ALL_CONDITIONS[1:]:
        yc = hit[3][c]; cc = conf[GRADED_ARM][c]; kc = int(yc.sum()); lo, hi = wilson(kc, n)
        d = {"accuracy": prop(kc / n, lo, hi, "accuracy", count=kc)}
        e, _ = ece_bins(cc, yc); lo, hi = ece_ci(cc, yc); d["calibration"] = prop(e, lo, hi, "calibration")
        k, _ = abstention(cc, yc); lo, hi = wilson(k, n); d["abstention"] = prop(k / n, lo, hi, "abstention", count=k)
        lost, gained, nn, p = mcnemar(y, yc)
        d["top3_loss"] = dict(clean_right_degraded_wrong=lost, clean_wrong_degraded_right=gained, relative_loss=(k3 - kc) / k3 if k3 else None, mcnemar_p=p)
        d["registered"] = c in REGISTERED; d["family"] = FAMILY[c]
        d["changes"] = [dict(property=p, clean=P[p]["grade"], degraded=d[p]["grade"],
                             direction="worse" if GRADE_RANK[d[p]["grade"]] < GRADE_RANK[P[p]["grade"]] else "better")
                        for p in ("accuracy", "calibration", "abstention") if d[p]["grade"] != P[p]["grade"]]
        deg[c] = d
    out["degraded"] = deg

    # ---- sensitivity: breaking distance, fixed mark shift, robustness matching rule
    bd = []
    for p in out["below"]:
        x = P[p]; to = x["hi"] if x["direction"] == "min" else x["lo"]
        bd.append(dict(property=p, mark=x["mark"], mark_must_become=to, move_percent=100 * abs(to - x["mark"]) / x["mark"],
                       direction="down" if x["direction"] == "min" else "up"))
    out["breaking_distance"] = bd
    shift = []
    for p in PROPS:
        x = P[p]
        for f in (0.9, 1.1):
            g = grade_of(x["lo"], x["hi"], x["mark"] * f, x["direction"])
            if g != x["grade"]: shift.append(dict(property=p, mark_moved_to=x["mark"] * f, grade_was=x["grade"], grade_becomes=g))
    out["fixed_mark_shift"] = shift
    r = P["robustness"]; out["robustness_by_matching_rule"] = {name: dict(mark=mk, grade=grade_of(r["lo"], r["hi"], mk, "min"))
                                                              for name, mk in MATCH_RULE_MARKS.items()}
    # ---- difficulty strata, from the three physicians and not from any model
    c0 = conf[GRADED_ARM]["original"]; dc = HARD.set_index("case_number").loc[CASE_INFO.case_number, "doctors_correct"].values
    out["difficulty"] = [dict(physicians_correct=int(d), cases=int((dc == d).sum()), M3=float(y[dc == d].mean()),
                              mean_confidence=float(c0[dc == d].mean())) for d in (3, 2, 1, 0)]
    out["per_case"] = dict(case_number=[int(x) for x in CASE_INFO.case_number], fold=[int(x) for x in Z["fold"]],
                           M3=[bool(x) for x in y], confidence=[float(x) for x in c0])
    json.dump(out, open(os.path.join(CFG["OUTDIR"], f"grades_{model}.json"), "w"), indent=1)

    # ---- saved predictions, one row per case and condition
    rows = []
    for c in ALL_CONDITIONS:
        for i, cn in enumerate(CASE_INFO.case_number):
            rk = [CANDIDATES[j] for j in order[c][i][:CFG["K_RETRIEVE"]]]
            row = dict(model=model, fold=int(Z["fold"][i]), case_number=int(cn), condition=c, primary=CASE_INFO.primary.iloc[i],
                       predicted=rk[0], ranked=rk, M1=bool(hit[1][c][i]), M3=bool(hit[3][c][i]), M5=bool(hit[5][c][i]),
                       sim_top1=float(Z["S|" + c][i, order[c][i][0]]))
            for a in ARMS: row["conf_" + a] = float(conf[a][c][i])
            if c == "original": row.update(A[i])
            rows.append(row)
    df = pd.DataFrame(rows); pth = os.path.join(CFG["OUTDIR"], f"predictions_{model}.parquet")
    try: df.to_parquet(pth, index=False)
    except Exception: pth = pth.replace(".parquet", ".csv"); df.to_csv(pth, index=False)
    return out

# =====================================================================================
# PART 8. The five-property table for one model
# =====================================================================================
def f4(x): return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.4f}"

def five_property_table(g):
    P = g["properties"]; rows = []
    detail = {"accuracy": lambda x: f"{x['count']} of {x['of']} cases with the reference diagnosis in the top three",
              "robustness": lambda x: f"{x['count']} of {x['of']} correct answers survive all three information-preserving conditions",
              "calibration": lambda x: f"Brier {x['brier']:.4f}, AUROC {x['auroc']:.4f}",
              "abstention": lambda x: f"answers {x['count']} of {x['of']} cases at M3 of {MARKS['accuracy']['value']:.4f} or higher",
              "auditability": lambda x: f"credited finding beats a random one in {x['count']} of {x['of']} cases"}
    for p in PROPS:
        x = P[p]
        rows.append({"Property": p.capitalize(), "Mark": f"{x['mark']:.4f} {'min' if x['direction']=='min' else 'max'}",
                     "Value": f4(x["value"]), "95% CI": f"[{f4(x['lo'])}, {f4(x['hi'])}]", "Grade": x["grade"], "Detail": detail[p](x)})
    return pd.DataFrame(rows)

def md_table(df):
    cols = list(df.columns); L = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows(): L.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(L)

def report_model(g):
    t = five_property_table(g); name = g["model"]
    L = [f"# Five-property table: {g['label']}", "",
         f"Run id {g['run_id']}. Marks and grading rule from Pre-Specification revision 3. "
         f"Calibration and abstention use the out-of-sample temperature of Section 3.4.", "", md_table(t), "",
         f"**Verdict: {g['verdict']}.** Properties BELOW: {', '.join(g['below']) if g['below'] else 'none'}.", "",
         "## Calibration and abstention under the three recalibration procedures", ""]
    rows = []
    for a in ARMS:
        c = g["arms"][a]["calibration"]; b = g["arms"][a]["abstention"]
        rows.append({"Procedure": ARM_LABEL[a] + (" (graded)" if a == GRADED_ARM else ""), "ECE": f4(c["value"]),
                     "ECE 95% CI": f"[{f4(c['lo'])}, {f4(c['hi'])}]", "Calibration grade": c["grade"],
                     "Noise floor for these confidences, mean and 95th pct": f"{f4(c['noise_floor_mean'])}, {f4(c['noise_floor_p95'])}",
                     "Coverage": f4(b["value"]), "Coverage 95% CI": f"[{f4(b['lo'])}, {f4(b['hi'])}]", "Abstention grade": b["grade"]})
    L += [md_table(pd.DataFrame(rows)), "", "## Grades under degraded input", ""]
    rows = []
    for c, d in g["degraded"].items():
        rows.append({"Condition": c, "Registered": "yes" if d["registered"] else "gradient",
                     "Accuracy": f"{f4(d['accuracy']['value'])} {d['accuracy']['grade']}",
                     "Calibration": f"{f4(d['calibration']['value'])} {d['calibration']['grade']}",
                     "Abstention": f"{f4(d['abstention']['value'])} {d['abstention']['grade']}",
                     "Relative Top-3 loss": "n/a" if d["top3_loss"]["relative_loss"] is None else f"{d['top3_loss']['relative_loss']:.4f}",
                     "McNemar p": f"{d['top3_loss']['mcnemar_p']:.2e}",
                     "Grade changes": "; ".join(f"{x['property']} {x['clean']} to {x['degraded']}" for x in d["changes"]) or "none"})
    L += [md_table(pd.DataFrame(rows)), "", "## Sensitivity", ""]
    if g["breaking_distance"]:
        L += [md_table(pd.DataFrame([{"BELOW property": b["property"], "Mark": f4(b["mark"]), "Mark must become": f4(b["mark_must_become"]),
                                      "Move required": f"{b['move_percent']:.1f}% {b['direction']}"} for b in g["breaking_distance"]])), ""]
    else: L += ["No property grades BELOW, so there is no breaking distance to report.", ""]
    L += ["Fixed mark shift of one tenth: " + ("; ".join(f"{s['property']} at {s['mark_moved_to']:.4f}: {s['grade_was']} to {s['grade_becomes']}"
                                                         for s in g["fixed_mark_shift"]) or "no grade changes") + ".", "",
          "Robustness grade by matching rule: " + "; ".join(f"{k} ({v['mark']:.4f}): {v['grade']}" for k, v in g["robustness_by_matching_rule"].items()) + ".", "",
          "## Difficulty strata", "",
          md_table(pd.DataFrame([{"Physicians correct": f"{d['physicians_correct']} of 3", "Cases": d["cases"], "M3": f4(d["M3"]),
                                  "Mean confidence": f4(d["mean_confidence"])} for d in g["difficulty"]])), ""]
    open(os.path.join(CFG["OUTDIR"], f"five_property_{name}.md"), "w").write("\n".join(L))
    t.to_csv(os.path.join(CFG["OUTDIR"], f"five_property_{name}.csv"), index=False)
    pd.DataFrame({"cases_answered": np.arange(1, g["n"] + 1), "coverage": np.arange(1, g["n"] + 1) / g["n"],
                  "accuracy_on_answered": g["arms"][GRADED_ARM]["risk_coverage"]}).to_csv(
        os.path.join(CFG["OUTDIR"], f"risk_coverage_{name}.csv"), index=False)
    pd.DataFrame(g["properties"]["calibration"]["bins"]).to_csv(os.path.join(CFG["OUTDIR"], f"reliability_{name}.csv"), index=False)
    print("\n" + f"=== {g['label']} ===" + "\n" + t.to_string(index=False))
    print(f"Verdict: {g['verdict']}. BELOW: {', '.join(g['below']) if g['below'] else 'none'}")
    print(f"Written to {CFG['OUTDIR']}/: five_property_{name}.md and .csv, grades_{name}.json, predictions_{name}.parquet, "
          f"risk_coverage_{name}.csv, reliability_{name}.csv")

def main(model):
    ap = argparse.ArgumentParser(description=f"Run and grade one model: {MODELS[model]['label']}")
    ap.add_argument("--data"); ap.add_argument("--descriptions"); ap.add_argument("--outdir", default=CFG["OUTDIR"])
    ap.add_argument("--force", action="store_true", help="run the model again even if its similarity matrices are saved")
    a = ap.parse_args(); CFG["OUTDIR"] = a.outdir
    random.seed(CFG["SEED_CV"]); np.random.seed(CFG["SEED_CV"])
    load_data(a.data, a.descriptions); run_model(model, force=a.force); report_model(grade_model(model))
