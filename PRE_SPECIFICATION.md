# Pre-Specification: Five-Property Trustworthiness Evaluation Framework

This document was committed before any evaluation run. The pass marks below were fixed at this commit date and are not revised after results are seen.

## Contribution

This praxis contributes a five-property evaluation framework for symptom-to-diagnosis decision support. The framework takes a model that returns a ranked differential diagnosis with scores. It applies five tests: accuracy against a physician reference, robustness under controlled degradation of patient-reported input, calibration against observed correctness, abstention under a coverage constraint, and auditability of the evidence credited for each prediction. It returns a pass or fail on each property and a single fit-for-use verdict. The evidence that the framework works is that it grades three models and separates models that accuracy alone does not separate.

The framework is for a clinical informatics lead or a clinical safety reviewer who is deciding whether to pilot a symptom-intake tool in primary care or triage. It answers one question. Is this model fit for that use, and if not, which property fails.

## Research questions and hypotheses

**RQ1.** When two models cannot be separated by accuracy, does five-property evaluation separate them?

**H1.** For at least one pair of models whose M3 confidence intervals overlap, the two models will differ on at least one of robustness, calibration, abstention or auditability by a margin whose confidence interval excludes zero.

**RQ2.** Does the five-property verdict change the deployment decision that accuracy alone would give?

**H2.** At least one model will meet the accuracy mark and fail at least one of the other four marks. Accuracy-only evaluation and five-property evaluation will therefore return different fit-for-use verdicts for that model.

**RQ3.** Are the verdicts stable when the pass marks move?

**H3.** Each model's overall verdict will remain unchanged when each pass mark is moved, one at a time, by the half-width of its 95 percent confidence interval.

Each hypothesis names a quantity that can be counted and each one can fail. H1 fails if no property separates the pair. H2 fails if every model that meets the accuracy mark meets all five. H3 fails if any verdict flips.

## The five cards

### 1. Accuracy

|  |  |
|---|---|
| **What goes in** | 400 physician-authored vignettes, 388 candidate descriptions, and the model's ranked list |
| **What is changed** | Nothing |
| **What is measured** | M3, the share of cases with the reference diagnosis in the top three |
| **Pass mark** | M3 not below 0.6200 |
| **Where the number comes from** | A human reference measured on the same cases. Three physicians answered the same 400 vignettes with the diagnosis concealed. The lowest of the three scored M3 of 0.6200. A decision-support tool that falls below the weakest human on the same cases is not fit for the stated use. |
| **Margin at n = 400** | Plus or minus 0.0476 |
| **How pass is decided** | Pass if the upper bound of the model's 95 percent confidence interval reaches 0.6200 |

### 2. Robustness

|  |  |
|---|---|
| **What goes in** | The same 400 cases |
| **What is changed** | The four patient-reported fields. Findings are removed, reworded, fragmented, or made vague |
| **What is measured** | Correct-prediction retention. Of the cases answered correctly on clean input, the share still answered correctly after perturbation |
| **Pass mark** | Retention of 0.90 or higher under the information-preserving conditions |
| **Where the number comes from** | A published convention. Measures used for individual-level clinical decisions are required to show reliability of at least 0.90 (Nunnally and Bernstein, 1994; Koo and Li, 2016). A patient who retells the same history in different words is a retest of the same measure, so the same convention applies. |
| **Margin at n = 400** | Plus or minus 0.0294 |
| **How pass is decided** | Pass if the lower bound of the 95 percent confidence interval reaches 0.90 |

### 3. Calibration

|  |  |
|---|---|
| **What goes in** | The model's stated confidence for each case |
| **What is changed** | Nothing |
| **What is measured** | Expected calibration error over 10 equal-mass bins |
| **Pass mark** | Expected calibration error of 0.0786 or lower |
| **Where the number comes from** | The noise of the measurement. A perfectly calibrated system of this size, with 10 bins of 40 cases, produces a mean expected calibration error of 0.0557 and a 95th percentile of 0.0786. Any value above 0.0786 cannot be explained by sampling variation alone. |
| **Margin at n = 400** | Reference distribution, 5th to 95th percentile, 0.0348 to 0.0786 |
| **How pass is decided** | Pass if the observed value falls at or below 0.0786 |

### 4. Abstention

|  |  |
|---|---|
| **What goes in** | The same confidence values |
| **What is changed** | The share of cases the model declines to answer |
| **What is measured** | The largest coverage at which accuracy on the answered cases reaches the accuracy mark |
| **Pass mark** | Coverage of 0.50 or higher at an answered-case M3 of 0.6200 or higher |
| **Where the number comes from** | A consequence for the clinician. A tool that has to decline more than half of presentations in order to reach human-equivalent accuracy does not reduce workload at intake and is not fit for the stated use. |
| **Margin at n = 400** | Plus or minus 0.0490 |
| **How pass is decided** | Pass if the lower bound of the 95 percent confidence interval on coverage reaches 0.50 |

### 5. Auditability

|  |  |
|---|---|
| **What goes in** | One case and the finding the model credits for its top prediction |
| **What is changed** | That finding is deleted. Separately, a randomly chosen finding is deleted |
| **What is measured** | The share of cases in which deleting the credited finding lowers the top score more than deleting a random finding |
| **Pass mark** | 0.75 of cases or higher |
| **Where the number comes from** | A published convention. Evaluation frameworks for explainability in medical AI state that they set no acceptability threshold, so there is no perturbation-faithfulness criterion to adopt. The mark is anchored instead to the general reliability convention, where 0.75 is the accepted floor for good agreement on a measure that informs a decision rather than determines it (Koo and Li, 2016). The explanation is advisory, so it is held to the advisory level and not to the decisional level of 0.90. |
| **Margin at n = 400** | Plus or minus 0.0424 |
| **How pass is decided** | Pass if the lower bound of the 95 percent confidence interval reaches 0.75 |

## The overall rule

A model is fit for the stated use only if it passes all five properties. The number of properties passed is reported next to the verdict.

The rule is combined because the five properties describe failure modes that are independent of each other. A strength in one does not cover a failure in another. A model that is accurate but miscalibrated presents confident wrong answers, and a model that is accurate but not robust fails to produce consistent predictions across different phrasing of same clinical content.

## How the evaluation is run

Three models are graded. These are TF-IDF retrieval, the encoder without fine-tuning, and the fine-tuned encoder. Every model receives the same 400 cases, the same 388 descriptions, the same folds, and the same scoring code. One set of predictions is saved for each model and every table is built from that file.

## The candidate descriptions

All 388 descriptions are taken verbatim from five versioned public datasets. These are the Mondo Disease Ontology (releases/2026-11-03, CC BY 4.0), MedlinePlus Health Topic XML (generated 13 November 2026, public domain), the NCI Thesaurus OBO Edition (releases/2024-05-07, CC BY 4.0), the Human Phenotype Ontology (hp/releases/2026-09-01), and the Human Disease Ontology (doid/releases/2026-10-29, CC0 1.0). No description is generated, paraphrased, or edited. 337 of them are exact or synonym matches. The remaining 51 use the nearest broader term from the same dataset and are recorded as such. Per-label provenance is in data/descriptions/candidate_descriptions_provenance.json.

| Source | Labels | Version | License |
|---|---|---|---|
| MONDO | 206 | releases/2026-11-03 | CC BY 4.0 |
| MedlinePlus | 119 | generated 13 Nov 2026 | Public domain, NLM |
| NCI Thesaurus | 35 | releases/2024-05-07, EVS 24.04e | CC BY 4.0 |
| Human Phenotype Ontology | 17 | hp/releases/2026-09-01 | HPO license |
| Disease Ontology | 11 | doid/releases/2026-10-29 | CC0 1.0 |

Health information in this corpus is from MedlinePlus.gov.
