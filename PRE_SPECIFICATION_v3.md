# Five-Property Trustworthiness Evaluation Framework

## Pre-Specification, revision 3

Feroz Karaiman. 17 November 2026.

Revision 1 was committed on 15 November 2026. Revision 2 is dated 16 November 2026. This revision was written after four models had been graded under revision 2. It changes how confidence is recalibrated, adds one sensitivity analysis, and requires the full similarity matrix to be saved for every model. It changes no pass mark, no grading rule and no hypothesis. Every change is listed in the revision note at the end, with the reason for it.

All four models are run again after this file is committed. The figures reported in the praxis come from that re-run. No figure from an earlier run is carried forward.

## Contribution

This praxis contributes a five-property evaluation framework for symptom-to-diagnosis decision support. The framework takes a model that returns a ranked differential diagnosis with scores. It applies five tests: accuracy against a physician reference, robustness under controlled degradation of patient-reported input, calibration against observed correctness, abstention under a coverage constraint, and auditability of the evidence credited for each prediction. It returns one of three grades on each property and a single fit-for-use verdict. The framework is tested by grading four models and asking whether the five-property profile tells a reviewer something the accuracy figures do not.

The framework is for a clinical informatics lead or a clinical safety reviewer who is deciding whether to pilot a symptom-intake tool in primary care or triage. It answers one question. Is this model fit for that use, and if not, which property falls short.

## How a property is graded

Each property has one pass mark and one 95 percent confidence interval. The grade is decided by where the interval sits relative to the mark, not by where the point estimate sits.

| Grade | Meaning |
|---|---|
| BELOW | The whole interval is on the wrong side of the mark. The model is shown to fall short of the standard. |
| AT | The interval contains the mark. At this sample size the model cannot be told apart from the standard. |
| ABOVE | The whole interval is on the right side of the mark. The model is shown to clear the standard. |

Three levels are used rather than two because a two-level rule has to report a model whose interval straddles the mark as either a pass or a fail, and neither is true. Reporting it as a fail overstates the evidence, and reporting it as a pass overstates it in the other direction.

## The overall rule

| Verdict | Condition |
|---|---|
| FIT FOR USE | Every property grades ABOVE |
| NOT ESTABLISHED | No property grades BELOW, and at least one grades AT |
| NOT FIT FOR USE | At least one property grades BELOW |

The count of BELOW properties and their names are reported next to the verdict, because a reviewer who has to act on the result needs to know which property to fix.

The rule is combined rather than averaged because a strength in one property does not cover a shortfall in another. A model that is accurate but miscalibrated presents confident wrong answers, and a model that is accurate but not robust gives different answers to different phrasings of the same clinical content.

**The five properties are not independent, and the framework does not claim they are.** Abstention is defined as the coverage at which answered-case accuracy still reaches the accuracy mark, so it is conditional on accuracy by construction. What the framework claims is the weaker and testable property of non-redundancy: no property's grade is determined by another's. The result reports the grade distribution across the four models and how closely accuracy and abstention track each other, so that this can be checked rather than assumed.

## Research questions and hypotheses

There are three research questions and three hypotheses.

**RQ1.** Does five-property evaluation give a reviewer information that accuracy alone does not give?

**H1.** Accuracy is not sufficient. For at least one pair of models, a property other than accuracy will separate the pair, meaning the two models receive different grades on that property and their intervals on it do not overlap, in a case where the accuracy figures do not deliver that separation. Accuracy fails to deliver it in either of two ways: the pair's accuracy intervals overlap, so accuracy reports no difference at all; or the pair's accuracy intervals separate but rank the pair in the opposite direction to the separating property.

H1 is one hypothesis and it receives one verdict. The result lists every pair that satisfies it and says which of the two ways applies to each pair. It is not split into sub-hypotheses. H1 fails if no pair of models in the study is separated by a non-accuracy property in either of those two ways.

**RQ2.** Does a model's five-property profile hold when the patient-reported input is degraded?

**H2.** For at least one model, at least one property will receive a worse grade under degraded input than under clean input. H2 fails if every grade is unchanged or better under every registered degradation condition.

**RQ3.** How far would a pass mark have to move before a verdict changed?

**H3.** For each model graded NOT FIT FOR USE, the result will report the breaking distance of every BELOW property, which is the percentage by which that property's mark would have to move before the grade stopped being BELOW. H3 claims that every breaking distance in the study exceeds 10 percent. H3 fails if any breaking distance is 10 percent or less. If no model grades NOT FIT FOR USE, H3 has nothing to test and is reported as not testable.

A verdict turns on whether any property is BELOW. A model with exactly one BELOW property has its verdict changed at that property's breaking distance. A model with more than one cannot have its verdict changed by moving a single mark.

H2 is evaluated on the three properties that are defined on degraded input, which are accuracy, calibration and abstention. Robustness is the degradation measurement itself, so it has no separate degraded value. Auditability requires the deletion of a credited finding from the clean vignette, so it is recorded on clean input only.

H2 regrades each model on four registered conditions. Three preserve the clinical information and change only how it is told: full rewording, complete fragmentation and moderate vagueness. The fourth removes two findings. The other six conditions (removal of one and three findings, rewording of 25 and 50 percent of terms, partial fragmentation, high vagueness) are run and reported as the severity gradient. They decide no hypothesis.

## The five cards

### 1. Accuracy

| | |
|---|---|
| What goes in | 400 physician-authored vignettes, 388 candidate descriptions, and the model's ranked list |
| What is changed | Nothing |
| What is measured | M3, the share of cases with the reference diagnosis in the top three |
| Pass mark | 0.6200, minimum |
| Where the number comes from | A human reference on the same cases. Three physicians answered the same 400 vignettes with the diagnosis concealed. The lowest of the three scored M3 of 0.6200 as reported in the benchmark study. A tool below the weakest human on the same cases is not fit for the stated use. |
| Interval | Wilson score interval on a proportion, n = 400 |

### 2. Robustness

| | |
|---|---|
| What goes in | The same 400 cases |
| What is changed | The four patient-reported fields. Findings are reworded, fragmented, or made vague. Physical examination and absent findings are not touched. |
| What is measured | Correct-prediction retention. Of the cases answered correctly on clean input, the share still answered correctly after every one of the three information-preserving registered conditions |
| Pass mark | 0.7881, minimum |
| Where the number comes from | Physician-to-physician agreement on the same 400 cases. Of the 1,548 ordered physician pairs in which the first physician placed the reference diagnosis in the top three, the second did so as well in 1,220, a rate of 0.7881 with a 95 percent interval of [0.7671, 0.8077]. |
| How the physician rate is computed | A physician's answer counts as correct when the reference diagnosis, by either its full name or its short name, appears in the first three entries of that physician's recorded differential. The three physicians score M3 of 0.5600, 0.6000 and 0.7750 under this rule. |
| Interval | Wilson score interval on a proportion, n = the count of cases correct on clean input |

The accuracy mark uses the published physician scores (0.6200, 0.6725, 0.8825). The robustness mark has to be computed case by case from the raw differential text, which scores the same physicians lower, because the published study credited free-text answers through clinician adjudication. That adjudication is not reproduced here, because doing it by hand after seeing model results would be an unauditable step.

The mark depends on how a physician's free text is counted as correct. Three rules are reported.

| Rule for counting a physician correct | Mark |
|---|---|
| Reference diagnosis by its short name only | 0.7822 |
| Reference diagnosis by its short or full name (adopted) | 0.7881 |
| Any entry from the case's gold differential list | 0.8960 |

The adopted rule matches the criterion the models are scored under, which is the reference diagnosis in the top three and nothing else. The third rule credits any entry on a list that holds a median of two acceptable answers, so it measures an easier task than the one the models are given.

### 3. Calibration

| | |
|---|---|
| What goes in | The model's similarity scores for all 388 candidates, for each case |
| What is changed | Nothing |
| Case confidence | One temperature is applied to the 388 similarity scores before the softmax. The confidence is the top-three mass of the resulting distribution. |
| How the temperature is fitted | Out of sample. For each fold, the temperature is fitted on the held-out predictions of the other four folds, by minimising the negative log-likelihood of the top-three event. It is then applied unchanged to the fold being scored. |
| What is measured | Expected calibration error over 10 equal-mass bins of 40 cases |
| Pass mark | 0.0786, maximum |
| Where the number comes from | The noise of the measurement. A perfectly calibrated system of this size, with 10 bins of 40 cases, produces a mean expected calibration error of 0.0557 and a 95th percentile of 0.0786. Unchanged from revision 1. |
| Interval | Bootstrap percentile interval over cases, 4,000 resamples, seed 20261102. Each resample draws 400 case indices with replacement and recomputes the error on the paired confidence and outcome. The temperature is not refitted inside the bootstrap. |
| Reported beside the grade | The Brier score, the area under the curve of confidence against correctness, and the noise floor computed from the model's own confidence values (mean and 95th percentile of the error a perfectly calibrated model would show with those same values). |

### 4. Abstention

| | |
|---|---|
| What goes in | The same confidence values the calibration card measures, pooled across the five folds |
| What is changed | The share of cases the model declines to answer, least confident first |
| What is measured | The largest coverage at which accuracy on the answered cases still reaches the accuracy mark |
| Pass mark | 0.5000, minimum, at an answered-case M3 of 0.6200 or higher |
| Where the number comes from | A consequence for the clinician. A tool that has to decline more than half of presentations to reach human-equivalent accuracy does not reduce workload at intake. Unchanged from revision 1. |
| Interval | Wilson score interval on a proportion, n = 400 |

### 5. Auditability

| | |
|---|---|
| What goes in | One case and the finding the model credits for its top prediction |
| What is changed | That finding is deleted. Separately, a randomly chosen other finding is deleted. |
| What is measured | The share of cases in which deleting the credited finding lowers the top score by strictly more than deleting the random finding |
| Pass mark | 0.5400, minimum |
| Where the number comes from | The chance floor of the measurement. A model whose credited finding carries no more weight than any other wins this comparison at most half the time. At n = 400 the 95th percentile of a rate of one half is 0.5400. A tie is not a win. |
| Interval | Wilson score interval on a proportion, n = 400 |

## Why the recalibration procedure was changed

Revisions 1 and 2 did not say how the temperature is fitted. The code as first run fitted it on each fold's training cases. The method it cites (Guo et al., 2017) fits on data the model did not train on. A fine-tuned encoder is close to certain on the cases it trained on, so a temperature fitted there carries a certainty the model does not have on new cases. The out-of-sample procedure in the calibration card replaces it.

The out-of-sample procedure has one assumption. The predictions used to fit a fold's temperature come from the other four fold models. Those models share the architecture, the settings and most of their training cases with the model being scored, but they are not the same model. The procedure assumes the five fold models scale their scores alike.

The temperature applied to a degraded input is the one fitted on clean held-out predictions. A deployed system cannot refit its confidence to each way a patient phrases a complaint.

## What this instrument cannot do at 400 cases

**FIT FOR USE is not expected in this study.** The top verdict requires every property to grade ABOVE. Robustness is measured only on the cases a model answers correctly on clean input, so its interval rests on a fraction of the 400 cases and is wide. The result reports that count for each model and the number of correct-on-clean cases each would need. The calibration mark is itself a noise floor, so a model with ordinary confidence values will rarely have an interval that sits wholly under it. The realistic verdicts are NOT FIT FOR USE and NOT ESTABLISHED.

**The calibration mark is one fixed value.** How much noise a perfectly calibrated model shows depends on its confidence values. The fixed mark is therefore lenient for a model with low and flat confidence and stricter for a model with confidence near one half. The mark is kept as pre-specified, and each model's own noise floor is reported beside its grade so a reader can see which way the fixed mark leaned.

**Four models is a small basis for a framework claim.** The framework can be shown to separate pairs that accuracy cannot. It cannot be shown to do so at any particular rate.

## How the evaluation is run

Four models are graded.

| Model | What it is |
|---|---|
| TF-IDF retrieval | Term-frequency retrieval over the 388 descriptions, unigrams and bigrams, sublinear term frequency, English stop words removed, cosine similarity. No learning. |
| Encoder, no fine-tuning | pritamdeka/S-PubMedBert-MS-MARCO used as released, maximum sequence length 512, no training on these cases |
| Encoder, fine-tuned 2 epochs | The same encoder with contrastive fine-tuning, multiple-negatives ranking loss, 2 epochs, batch 32, learning rate 2e-5, 10 percent warmup, seed 42 |
| Encoder, fine-tuned 8 epochs | The same encoder and the same settings trained for 8 epochs instead of 2 |

Every model receives the same 400 cases, the same 388 descriptions, the same five stratified folds (seed 42), the same confidence definition, and the same scoring code. One Colab notebook runs each model. Every notebook writes and imports the same shared file, `praxis_eval.py`, so the code is identical across the four.

Each run saves the full similarity matrix, 400 cases by 388 candidates, for the clean input and for all ten perturbation conditions, together with the training-fold similarities. Every table is built from those saved files. No model is re-run to produce a table.

**Disclosure on the 8-epoch model.** The 8-epoch configuration was not named in revision 1. It was first run on 15 November 2026, after the three models of revision 1 had been graded, as a declared exploratory analysis. Revision 2 adopted it as the fourth graded model because three models did not provide a pair whose accuracy separates while another property disagrees. It is named here before the re-run.

## Sensitivity analyses

Four are run and all four are reported in full, including any that weaken a claim. The first three are from revision 2. The fourth is added in this revision.

**1. Breaking distance.** For every property a model grades BELOW, the result reports how far that mark would have to move, as a percentage of its own value, before the grade stopped being BELOW. This is the test of H3.

**2. Fixed mark shift.** Each of the five marks is moved up and down by one tenth of its own value, one mark at a time, and every model is regraded. Every grade that changes is listed.

**3. Robustness matching rule.** The robustness row is regraded under each of the three marks in the robustness card.

**4. Recalibration procedure.** Calibration and abstention are regraded under three procedures: the temperature fitted on each fold's training cases against the reference diagnosis, which is the procedure as first run; the out-of-sample temperature of the calibration card, which is the one the grades use; and isotonic regression of the out-of-sample confidence, fitted on the other four folds. Each result carries its interval. Recalibration never reorders the candidates within a case, so accuracy, robustness and auditability do not change. It can reorder cases by confidence, so abstention is recomputed under each procedure.

## Supporting analyses that are reported

- M1 and M5 for each model.
- The count of cases whose reference diagnosis is absent from their own training fold, and the closed-set ceiling that follows.
- The four difficulty strata, from the number of physicians who placed the reference diagnosis in their top three, with each model's accuracy and mean confidence in each.
- The risk-coverage curve and the ten reliability bins for each model.
- Relative Top-3 loss and a one-sided exact McNemar test for each model under each condition, against clean input.
- A one-sided exact McNemar test between the two fine-tuned models.
- The near-duplicate audit of the 400 vignettes.

## The candidate descriptions

All 388 descriptions are taken verbatim from five versioned public datasets. No description is generated, paraphrased, or edited. 337 are direct matches. The remaining 51 use the nearest broader term from the same dataset and are recorded as such.

| Source | Labels | Version | License |
|---|---|---|---|
| Mondo Disease Ontology | 206 | releases/2026-11-03 | CC BY 4.0 |
| MedlinePlus Health Topic XML | 119 | generated 13 Nov 2026 | Public domain, NLM |
| NCI Thesaurus, OBO Edition | 35 | releases/2024-05-07, EVS 24.04e | CC BY 4.0 |
| Human Phenotype Ontology | 17 | hp/releases/2026-09-01 | HPO license |
| Human Disease Ontology | 11 | doid/releases/2026-10-29 | CC0 1.0 |

Health information in this corpus is from MedlinePlus.gov.

## Repository

All code, data, saved similarity matrices, graded files and every revision of this pre-specification are at https://github.com/karaimanferoz101-crypto/Praxis-2026. This revision is committed before the re-run. Its commit timestamp, set against the run id written into each saved file, is the record of that order.

| What | File |
|---|---|
| Shared scoring, perturbation, model and grading code | `praxis_eval.py`, written by every notebook |
| One run notebook per model | `RUN_1_tfidf_retrieval.ipynb`, `RUN_2_zeroshot.ipynb`, `RUN_3_finetuned_2ep.ipynb`, `RUN_4_finetuned_8ep.ipynb` |
| Four-model tables and hypothesis tests | `BUILD_four_model_tables.ipynb` |

## Revision note, revision 2 to revision 3

The revision 1 to revision 2 changes are listed in revision 2 and are not repeated here.

| What changed | From | To | Why |
|---|---|---|---|
| Recalibration procedure | Not stated. The code fitted the temperature on each fold's training cases, against the reference diagnosis. | Temperature fitted out of sample on the other four folds, against the top-three event | Fitting on training cases departs from the method cited for it. Found by checking the code against Guo et al. (2017) after the four models had been graded. |
| Recalibration sensitivity | Not specified | Calibration and abstention regraded under three procedures, each with its interval | The calibration grade depends on the procedure, so the dependence is reported. |
| Saved output | Top-ten list and one confidence value per case | Full similarity matrix for every condition | Calibration and abstention could not be recomputed from the old files. |
| Conditions run | The four registered conditions | All ten, with six reported as the severity gradient | The severity gradient was promised and had not been run on the current descriptions. |
| H1 reporting | Described as satisfied by two kinds of pair | One hypothesis, one verdict, with every qualifying pair listed | H1 was always a single claim. The result no longer labels two parts. |
| H3 when no model fails | Not stated | Reported as not testable | H3 is defined on models graded NOT FIT FOR USE. |
| Calibration noise floor | One fixed mark | The same fixed mark, with each model's own noise floor reported beside it | The noise a calibrated model shows depends on its confidence values. |
| Bootstrap for calibration | 4,000 resamples, method not stated | 4,000 resamples, method stated in the card | So the interval can be reproduced exactly. |

No pass mark, grading rule, verdict rule or hypothesis is changed by this revision.
