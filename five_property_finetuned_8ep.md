# Five-property table: Encoder, fine-tuned 8 epochs

Run id 20261117T171931Z. Marks and grading rule from Pre-Specification revision 3. Calibration and abstention use the out-of-sample temperature of Section 3.4.

| Property | Mark | Value | 95% CI | Grade | Detail |
|---|---|---|---|---|---|
| Accuracy | 0.6200 min | 0.6050 | [0.5563, 0.6517] | AT | 242 of 400 cases with the reference diagnosis in the top three |
| Robustness | 0.7881 min | 0.8306 | [0.7782, 0.8726] | AT | 201 of 242 correct answers survive all three information-preserving conditions |
| Calibration | 0.0786 max | 0.0577 | [0.0523, 0.1231] | AT | Brier 0.2120, AUROC 0.6955 |
| Abstention | 0.5000 min | 0.9750 | [0.9546, 0.9864] | ABOVE | answers 390 of 400 cases at M3 of 0.6200 or higher |
| Auditability | 0.5400 min | 0.7950 | [0.7527, 0.8317] | ABOVE | credited finding beats a random one in 318 of 400 cases |

**Verdict: NOT ESTABLISHED.** Properties BELOW: none.

## Calibration and abstention under the three recalibration procedures

| Procedure | ECE | ECE 95% CI | Calibration grade | Noise floor for these confidences, mean and 95th pct | Coverage | Coverage 95% CI | Abstention grade |
|---|---|---|---|---|---|---|---|
| Temperature fitted on training folds, as first run | 0.2219 | [0.1802, 0.2679] | BELOW | 0.0403, 0.0588 | 0.9750 | [0.9546, 0.9864] | ABOVE |
| Temperature fitted out of sample, Section 3.4 (graded) | 0.0577 | [0.0523, 0.1231] | AT | 0.0566, 0.0801 | 0.9750 | [0.9546, 0.9864] | ABOVE |
| Isotonic regression, fitted out of sample | 0.0559 | [0.0512, 0.1233] | AT | 0.0563, 0.0800 | 0.9700 | [0.9483, 0.9828] | ABOVE |

## Grades under degraded input

| Condition | Registered | Accuracy | Calibration | Abstention | Relative Top-3 loss | McNemar p | Grade changes |
|---|---|---|---|---|---|---|---|
| remove 1 finding | gradient | 0.5650 BELOW | 0.0386 AT | 0.8250 ABOVE | 0.0661 | 8.29e-03 | accuracy AT to BELOW |
| remove 2 findings | yes | 0.5525 BELOW | 0.0496 AT | 0.7775 ABOVE | 0.0868 | 1.01e-02 | accuracy AT to BELOW |
| remove 3 findings | gradient | 0.4575 BELOW | 0.1089 BELOW | 0.4675 AT | 0.2438 | 8.49e-09 | accuracy AT to BELOW; calibration AT to BELOW; abstention ABOVE to AT |
| reword 25% | gradient | 0.5875 AT | 0.0479 AT | 0.9150 ABOVE | 0.0289 | 5.92e-02 | none |
| reword 50% | gradient | 0.5775 AT | 0.0660 AT | 0.8750 ABOVE | 0.0455 | 1.73e-02 | none |
| reword 100% | yes | 0.5525 BELOW | 0.0815 AT | 0.7975 ABOVE | 0.0868 | 9.57e-04 | accuracy AT to BELOW |
| fragment partial | gradient | 0.6225 AT | 0.0582 AT | 1.0000 ABOVE | -0.0289 | 9.75e-01 | none |
| fragment complete | yes | 0.6125 AT | 0.0663 AT | 0.9775 ABOVE | -0.0124 | 7.63e-01 | none |
| vague moderate | yes | 0.6050 AT | 0.0688 AT | 0.9750 ABOVE | 0.0000 | 6.56e-01 | none |
| vague high | gradient | 0.5925 AT | 0.0719 AT | 0.9350 ABOVE | 0.0207 | 1.80e-01 | none |

## Sensitivity

No property grades BELOW, so there is no breaking distance to report.

Fixed mark shift of one tenth: accuracy at 0.6820: AT to BELOW; robustness at 0.7093: AT to ABOVE.

Robustness grade by matching rule: short name only (0.7822): AT; short or full name (adopted) (0.7881): AT; any gold-list entry (0.8960): BELOW.

## Difficulty strata

| Physicians correct | Cases | M3 | Mean confidence |
|---|---|---|---|
| 3 of 3 | 171 | 0.6959 | 0.6269 |
| 2 of 3 | 96 | 0.5938 | 0.5712 |
| 1 of 3 | 67 | 0.5373 | 0.5872 |
| 0 of 3 | 66 | 0.4545 | 0.5933 |
