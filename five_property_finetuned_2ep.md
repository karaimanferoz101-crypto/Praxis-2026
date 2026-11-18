# Five-property table: Encoder, fine-tuned 2 epochs

Run id 20261117T174337Z. Marks and grading rule from Pre-Specification revision 3. Calibration and abstention use the out-of-sample temperature of Section 3.4.

| Property | Mark | Value | 95% CI | Grade | Detail |
|---|---|---|---|---|---|
| Accuracy | 0.6200 min | 0.4550 | [0.4069, 0.5040] | BELOW | 182 of 400 cases with the reference diagnosis in the top three |
| Robustness | 0.7881 min | 0.8077 | [0.7443, 0.8584] | AT | 147 of 182 correct answers survive all three information-preserving conditions |
| Calibration | 0.0786 max | 0.0634 | [0.0481, 0.1178] | AT | Brier 0.2193, AUROC 0.6990 |
| Abstention | 0.5000 min | 0.5075 | [0.4587, 0.5562] | AT | answers 203 of 400 cases at M3 of 0.6200 or higher |
| Auditability | 0.5400 min | 0.8300 | [0.7901, 0.8636] | ABOVE | credited finding beats a random one in 332 of 400 cases |

**Verdict: NOT FIT FOR USE.** Properties BELOW: accuracy.

## Calibration and abstention under the three recalibration procedures

| Procedure | ECE | ECE 95% CI | Calibration grade | Noise floor for these confidences, mean and 95th pct | Coverage | Coverage 95% CI | Abstention grade |
|---|---|---|---|---|---|---|---|
| Temperature fitted on training folds, as first run | 0.0865 | [0.0604, 0.1371] | AT | 0.0575, 0.0806 | 0.5275 | [0.4785, 0.5759] | AT |
| Temperature fitted out of sample, Section 3.4 (graded) | 0.0634 | [0.0481, 0.1178] | AT | 0.0580, 0.0809 | 0.5075 | [0.4587, 0.5562] | AT |
| Isotonic regression, fitted out of sample | 0.1018 | [0.0667, 0.1439] | AT | 0.0569, 0.0810 | 0.5025 | [0.4537, 0.5512] | AT |

## Grades under degraded input

| Condition | Registered | Accuracy | Calibration | Abstention | Relative Top-3 loss | McNemar p | Grade changes |
|---|---|---|---|---|---|---|---|
| remove 1 finding | gradient | 0.4475 BELOW | 0.0809 AT | 0.3450 BELOW | 0.0165 | 3.64e-01 | abstention AT to BELOW |
| remove 2 findings | yes | 0.4200 BELOW | 0.0880 AT | 0.3900 BELOW | 0.0769 | 3.25e-02 | abstention AT to BELOW |
| remove 3 findings | gradient | 0.3950 BELOW | 0.0773 AT | 0.1550 BELOW | 0.1319 | 3.95e-03 | abstention AT to BELOW |
| reword 25% | gradient | 0.4500 BELOW | 0.0715 AT | 0.3950 BELOW | 0.0110 | 3.44e-01 | abstention AT to BELOW |
| reword 50% | gradient | 0.4550 BELOW | 0.0529 AT | 0.3950 BELOW | 0.0000 | 6.05e-01 | abstention AT to BELOW |
| reword 100% | yes | 0.4300 BELOW | 0.0708 AT | 0.2500 BELOW | 0.0549 | 7.69e-02 | abstention AT to BELOW |
| fragment partial | gradient | 0.4650 BELOW | 0.0471 AT | 0.3900 BELOW | -0.0220 | 8.81e-01 | abstention AT to BELOW |
| fragment complete | yes | 0.4525 BELOW | 0.0492 AT | 0.3100 BELOW | 0.0055 | 5.00e-01 | abstention AT to BELOW |
| vague moderate | yes | 0.4575 BELOW | 0.0588 AT | 0.4100 BELOW | -0.0055 | 7.73e-01 | abstention AT to BELOW |
| vague high | gradient | 0.4600 BELOW | 0.0648 AT | 0.3825 BELOW | -0.0110 | 8.55e-01 | abstention AT to BELOW |

## Sensitivity

| BELOW property | Mark | Mark must become | Move required |
|---|---|---|---|
| accuracy | 0.6200 | 0.5040 | 18.7% down |

Fixed mark shift of one tenth: robustness at 0.7093: AT to ABOVE; robustness at 0.8669: AT to BELOW; abstention at 0.4500: AT to ABOVE.

Robustness grade by matching rule: short name only (0.7822): AT; short or full name (adopted) (0.7881): AT; any gold-list entry (0.8960): BELOW.

## Difficulty strata

| Physicians correct | Cases | M3 | Mean confidence |
|---|---|---|---|
| 3 of 3 | 171 | 0.5556 | 0.4926 |
| 2 of 3 | 96 | 0.3542 | 0.4377 |
| 1 of 3 | 67 | 0.4478 | 0.4561 |
| 0 of 3 | 66 | 0.3485 | 0.4413 |
