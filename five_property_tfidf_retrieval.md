# Five-property table: TF-IDF retrieval

Run id 20261117T180443Z. Marks and grading rule from Pre-Specification revision 3. Calibration and abstention use the out-of-sample temperature of Section 3.4.

| Property | Mark | Value | 95% CI | Grade | Detail |
|---|---|---|---|---|---|
| Accuracy | 0.6200 min | 0.2450 | [0.2054, 0.2894] | BELOW | 98 of 400 cases with the reference diagnosis in the top three |
| Robustness | 0.7881 min | 0.8571 | [0.7744, 0.9130] | AT | 84 of 98 correct answers survive all three information-preserving conditions |
| Calibration | 0.0786 max | 0.1394 | [0.1033, 0.1792] | BELOW | Brier 0.2017, AUROC 0.6180 |
| Abstention | 0.5000 min | 0.0225 | [0.0119, 0.0422] | BELOW | answers 9 of 400 cases at M3 of 0.6200 or higher |
| Auditability | 0.5400 min | 0.9400 | [0.9123, 0.9594] | ABOVE | credited finding beats a random one in 376 of 400 cases |

**Verdict: NOT FIT FOR USE.** Properties BELOW: accuracy, calibration, abstention.

## Calibration and abstention under the three recalibration procedures

| Procedure | ECE | ECE 95% CI | Calibration grade | Noise floor for these confidences, mean and 95th pct | Coverage | Coverage 95% CI | Abstention grade |
|---|---|---|---|---|---|---|---|
| Temperature fitted on training folds, as first run | 0.1786 | [0.1571, 0.2384] | BELOW | 0.0480, 0.0685 | 0.0200 | [0.0102, 0.0390] | BELOW |
| Temperature fitted out of sample, Section 3.4 (graded) | 0.1394 | [0.1033, 0.1792] | BELOW | 0.0412, 0.0588 | 0.0225 | [0.0119, 0.0422] | BELOW |
| Isotonic regression, fitted out of sample | 0.0749 | [0.0543, 0.1203] | AT | 0.0509, 0.0719 | 0.0350 | [0.0210, 0.0579] | BELOW |

## Grades under degraded input

| Condition | Registered | Accuracy | Calibration | Abstention | Relative Top-3 loss | McNemar p | Grade changes |
|---|---|---|---|---|---|---|---|
| remove 1 finding | gradient | 0.2500 BELOW | 0.1372 BELOW | 0.0225 BELOW | -0.0204 | 7.60e-01 | none |
| remove 2 findings | yes | 0.2025 BELOW | 0.0999 AT | 0.0100 BELOW | 0.1735 | 4.74e-03 | calibration BELOW to AT |
| remove 3 findings | gradient | 0.1725 BELOW | 0.1064 AT | 0.0075 BELOW | 0.2959 | 7.69e-06 | calibration BELOW to AT |
| reword 25% | gradient | 0.2375 BELOW | 0.1325 BELOW | 0.0200 BELOW | 0.0306 | 2.27e-01 | none |
| reword 50% | gradient | 0.2525 BELOW | 0.1422 BELOW | 0.0225 BELOW | -0.0306 | 8.87e-01 | none |
| reword 100% | yes | 0.2450 BELOW | 0.1369 BELOW | 0.0200 BELOW | 0.0000 | 5.88e-01 | none |
| fragment partial | gradient | 0.2450 BELOW | 0.1393 BELOW | 0.0225 BELOW | 0.0000 | 1.00e+00 | none |
| fragment complete | yes | 0.2450 BELOW | 0.1393 BELOW | 0.0225 BELOW | 0.0000 | 1.00e+00 | none |
| vague moderate | yes | 0.2375 BELOW | 0.1274 BELOW | 0.0225 BELOW | 0.0306 | 2.54e-01 | none |
| vague high | gradient | 0.2375 BELOW | 0.1338 BELOW | 0.0225 BELOW | 0.0306 | 2.74e-01 | none |

## Sensitivity

| BELOW property | Mark | Mark must become | Move required |
|---|---|---|---|
| accuracy | 0.6200 | 0.2894 | 53.3% down |
| calibration | 0.0786 | 0.1033 | 31.4% up |
| abstention | 0.5000 | 0.0422 | 91.6% down |

Fixed mark shift of one tenth: robustness at 0.7093: AT to ABOVE.

Robustness grade by matching rule: short name only (0.7822): AT; short or full name (adopted) (0.7881): AT; any gold-list entry (0.8960): AT.

## Difficulty strata

| Physicians correct | Cases | M3 | Mean confidence |
|---|---|---|---|
| 3 of 3 | 171 | 0.3099 | 0.2149 |
| 2 of 3 | 96 | 0.2292 | 0.1615 |
| 1 of 3 | 67 | 0.1791 | 0.2088 |
| 0 of 3 | 66 | 0.1667 | 0.1766 |
