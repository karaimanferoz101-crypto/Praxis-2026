# Five-property table: Encoder, no fine-tuning

Run id 20261117T175654Z. Marks and grading rule from Pre-Specification revision 3. Calibration and abstention use the out-of-sample temperature of Section 3.4.

| Property | Mark | Value | 95% CI | Grade | Detail |
|---|---|---|---|---|---|
| Accuracy | 0.6200 min | 0.2475 | [0.2077, 0.2921] | BELOW | 99 of 400 cases with the reference diagnosis in the top three |
| Robustness | 0.7881 min | 0.7475 | [0.6538, 0.8227] | AT | 74 of 99 correct answers survive all three information-preserving conditions |
| Calibration | 0.0786 max | 0.0422 | [0.0385, 0.1037] | AT | Brier 0.1766, AUROC 0.6527 |
| Abstention | 0.5000 min | 0.0025 | [0.0004, 0.0140] | BELOW | answers 1 of 400 cases at M3 of 0.6200 or higher |
| Auditability | 0.5400 min | 0.8025 | [0.7607, 0.8386] | ABOVE | credited finding beats a random one in 321 of 400 cases |

**Verdict: NOT FIT FOR USE.** Properties BELOW: accuracy, abstention.

## Calibration and abstention under the three recalibration procedures

| Procedure | ECE | ECE 95% CI | Calibration grade | Noise floor for these confidences, mean and 95th pct | Coverage | Coverage 95% CI | Abstention grade |
|---|---|---|---|---|---|---|---|
| Temperature fitted on training folds, as first run | 0.0869 | [0.0625, 0.1347] | AT | 0.0452, 0.0635 | 0.0000 | [0.0000, 0.0095] | BELOW |
| Temperature fitted out of sample, Section 3.4 (graded) | 0.0422 | [0.0385, 0.1037] | AT | 0.0524, 0.0739 | 0.0025 | [0.0004, 0.0140] | BELOW |
| Isotonic regression, fitted out of sample | 0.0439 | [0.0428, 0.1086] | AT | 0.0511, 0.0729 | 0.0000 | [0.0000, 0.0095] | BELOW |

## Grades under degraded input

| Condition | Registered | Accuracy | Calibration | Abstention | Relative Top-3 loss | McNemar p | Grade changes |
|---|---|---|---|---|---|---|---|
| remove 1 finding | gradient | 0.2325 BELOW | 0.0757 AT | 0.0025 BELOW | 0.0606 | 8.98e-02 | none |
| remove 2 findings | yes | 0.2200 BELOW | 0.0469 AT | 0.0075 BELOW | 0.1111 | 3.07e-02 | none |
| remove 3 findings | gradient | 0.1950 BELOW | 0.0620 AT | 0.0075 BELOW | 0.2121 | 1.54e-03 | none |
| reword 25% | gradient | 0.2300 BELOW | 0.0465 AT | 0.0025 BELOW | 0.0707 | 1.95e-02 | none |
| reword 50% | gradient | 0.2200 BELOW | 0.0601 AT | 0.0025 BELOW | 0.1111 | 3.69e-03 | none |
| reword 100% | yes | 0.2025 BELOW | 0.0405 AT | 0.0000 BELOW | 0.1818 | 2.67e-04 | none |
| fragment partial | gradient | 0.2300 BELOW | 0.0549 AT | 0.0025 BELOW | 0.0707 | 3.27e-02 | none |
| fragment complete | yes | 0.2375 BELOW | 0.0450 AT | 0.0025 BELOW | 0.0404 | 2.40e-01 | none |
| vague moderate | yes | 0.2425 BELOW | 0.0564 AT | 0.0000 BELOW | 0.0202 | 3.87e-01 | none |
| vague high | gradient | 0.2300 BELOW | 0.0400 AT | 0.0000 BELOW | 0.0707 | 9.46e-02 | none |

## Sensitivity

| BELOW property | Mark | Mark must become | Move required |
|---|---|---|---|
| accuracy | 0.6200 | 0.2921 | 52.9% down |
| abstention | 0.5000 | 0.0140 | 97.2% down |

Fixed mark shift of one tenth: robustness at 0.8669: AT to BELOW.

Robustness grade by matching rule: short name only (0.7822): AT; short or full name (adopted) (0.7881): AT; any gold-list entry (0.8960): BELOW.

## Difficulty strata

| Physicians correct | Cases | M3 | Mean confidence |
|---|---|---|---|
| 3 of 3 | 171 | 0.2924 | 0.2571 |
| 2 of 3 | 96 | 0.2292 | 0.2550 |
| 1 of 3 | 67 | 0.2388 | 0.2402 |
| 0 of 3 | 66 | 0.1667 | 0.2091 |
