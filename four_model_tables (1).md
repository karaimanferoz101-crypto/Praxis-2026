# Four-model tables, Pre-Specification revision 3

Run ids: TF-IDF retrieval 20261117T180443Z; Encoder, no fine-tuning 20261117T175654Z; Encoder, fine-tuned 2 epochs 20261117T174337Z; Encoder, fine-tuned 8 epochs 20261117T171931Z.

Calibration and abstention use the out-of-sample temperature of Section 3.4. Every number is read from the saved graded files.

## Table 1. Four models, five properties

| Property | Mark | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|---|
| Accuracy | 0.6200 min | 0.2450 BELOW | 0.2475 BELOW | 0.4550 BELOW | 0.6050 AT |
| Robustness | 0.7881 min | 0.8571 AT | 0.7475 AT | 0.8077 AT | 0.8306 AT |
| Calibration | 0.0786 max | 0.1394 BELOW | 0.0422 AT | 0.0634 AT | 0.0577 AT |
| Abstention | 0.5000 min | 0.0225 BELOW | 0.0025 BELOW | 0.5075 AT | 0.9750 ABOVE |
| Auditability | 0.5400 min | 0.9400 ABOVE | 0.8025 ABOVE | 0.8300 ABOVE | 0.7950 ABOVE |
| Properties BELOW |  | 3 | 2 | 1 | 0 |
| Which ones |  | accuracy, calibration, abstention | accuracy, abstention | accuracy | none |
| Verdict |  | NOT FIT FOR USE | NOT FIT FOR USE | NOT FIT FOR USE | NOT ESTABLISHED |

## Table 2. The same values with 95 percent confidence intervals

| Property | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|
| Accuracy | 0.2450 [0.2054, 0.2894] | 0.2475 [0.2077, 0.2921] | 0.4550 [0.4069, 0.5040] | 0.6050 [0.5563, 0.6517] |
| Robustness | 0.8571 [0.7744, 0.9130] | 0.7475 [0.6538, 0.8227] | 0.8077 [0.7443, 0.8584] | 0.8306 [0.7782, 0.8726] |
| Calibration | 0.1394 [0.1033, 0.1792] | 0.0422 [0.0385, 0.1037] | 0.0634 [0.0481, 0.1178] | 0.0577 [0.0523, 0.1231] |
| Abstention | 0.0225 [0.0119, 0.0422] | 0.0025 [0.0004, 0.0140] | 0.5075 [0.4587, 0.5562] | 0.9750 [0.9546, 0.9864] |
| Auditability | 0.9400 [0.9123, 0.9594] | 0.8025 [0.7607, 0.8386] | 0.8300 [0.7901, 0.8636] | 0.7950 [0.7527, 0.8317] |

## Table 3. Counts behind the proportions

| Property | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|
| Accuracy | 98 of 400 | 99 of 400 | 182 of 400 | 242 of 400 |
| Robustness | 84 of 98 | 74 of 99 | 147 of 182 | 201 of 242 |
| Abstention | 9 of 400 | 1 of 400 | 203 of 400 | 390 of 400 |
| Auditability | 376 of 400 | 321 of 400 | 332 of 400 | 318 of 400 |
| M1, M5 | 0.1425, 0.3200 | 0.1350, 0.3150 | 0.2475, 0.5750 | 0.3375, 0.7000 |
| Calibration: Brier, AUROC | 0.2017, 0.6180 | 0.1766, 0.6527 | 0.2193, 0.6990 | 0.2120, 0.6955 |
| Auditability: ties, sign test p | 0, 9.28e-83 | 0, 5.40e-36 | 0, 4.04e-43 | 0, 3.38e-34 |
| Robustness: correct-on-clean cases needed to clear the mark | 135 | rate is below the mark | 1672 | 356 |

## Table 4. Rank by each property

| Property | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Accuracy | Encoder, fine-tuned 8 epochs | Encoder, fine-tuned 2 epochs | Encoder, no fine-tuning | TF-IDF retrieval |
| Robustness | TF-IDF retrieval | Encoder, fine-tuned 8 epochs | Encoder, fine-tuned 2 epochs | Encoder, no fine-tuning |
| Calibration | Encoder, no fine-tuning | Encoder, fine-tuned 8 epochs | Encoder, fine-tuned 2 epochs | TF-IDF retrieval |
| Abstention | Encoder, fine-tuned 8 epochs | Encoder, fine-tuned 2 epochs | TF-IDF retrieval | Encoder, no fine-tuning |
| Auditability | TF-IDF retrieval | Encoder, fine-tuned 2 epochs | Encoder, no fine-tuning | Encoder, fine-tuned 8 epochs |

## H1. Accuracy is not sufficient

NOT SUPPORTED 0 of 6 pairs satisfy the hypothesis.

H1 is one hypothesis. A pair satisfies it when a property other than accuracy gives the two models different grades on intervals that do not overlap, and accuracy does not deliver that separation, either because the accuracy intervals overlap or because accuracy ranks the pair the other way.

| Pair | Accuracy intervals | Properties that separate the pair by grade and by interval | Of those, against the accuracy ranking | Satisfies H1 |
|---|---|---|---|---|
| TF-IDF retrieval and Encoder, no fine-tuning | overlap | none | not applicable | no |
| TF-IDF retrieval and Encoder, fine-tuned 2 epochs | separate | abstention | none | no |
| TF-IDF retrieval and Encoder, fine-tuned 8 epochs | separate | abstention | none | no |
| Encoder, no fine-tuning and Encoder, fine-tuned 2 epochs | separate | abstention | none | no |
| Encoder, no fine-tuning and Encoder, fine-tuned 8 epochs | separate | abstention | none | no |
| Encoder, fine-tuned 2 epochs and Encoder, fine-tuned 8 epochs | separate | abstention | none | no |

## H2. Degraded input

SUPPORTED 6 grades are worse under the four registered conditions, 1 are better.

| Model | Condition | Property | Clean | Degraded | Direction |
|---|---|---|---|---|---|
| TF-IDF retrieval | remove 2 findings | calibration | BELOW, 0.1394 | AT, 0.0999 | better |
| Encoder, fine-tuned 2 epochs | remove 2 findings | abstention | AT, 0.5075 | BELOW, 0.3900 | worse |
| Encoder, fine-tuned 2 epochs | reword 100% | abstention | AT, 0.5075 | BELOW, 0.2500 | worse |
| Encoder, fine-tuned 2 epochs | fragment complete | abstention | AT, 0.5075 | BELOW, 0.3100 | worse |
| Encoder, fine-tuned 2 epochs | vague moderate | abstention | AT, 0.5075 | BELOW, 0.4100 | worse |
| Encoder, fine-tuned 8 epochs | remove 2 findings | accuracy | AT, 0.6050 | BELOW, 0.5525 | worse |
| Encoder, fine-tuned 8 epochs | reword 100% | accuracy | AT, 0.6050 | BELOW, 0.5525 | worse |

Accuracy under every condition, with relative Top-3 loss and the one-sided exact McNemar p against clean input:

| Condition | Family | Registered | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|---|---|
| remove 1 finding | Removal | gradient | 0.2500 BELOW, loss -0.020, p 7.6e-01 | 0.2325 BELOW, loss 0.061, p 9.0e-02 | 0.4475 BELOW, loss 0.016, p 3.6e-01 | 0.5650 BELOW, loss 0.066, p 8.3e-03 |
| remove 2 findings | Removal | yes | 0.2025 BELOW, loss 0.173, p 4.7e-03 | 0.2200 BELOW, loss 0.111, p 3.1e-02 | 0.4200 BELOW, loss 0.077, p 3.2e-02 | 0.5525 BELOW, loss 0.087, p 1.0e-02 |
| remove 3 findings | Removal | gradient | 0.1725 BELOW, loss 0.296, p 7.7e-06 | 0.1950 BELOW, loss 0.212, p 1.5e-03 | 0.3950 BELOW, loss 0.132, p 4.0e-03 | 0.4575 BELOW, loss 0.244, p 8.5e-09 |
| reword 25% | Rewording | gradient | 0.2375 BELOW, loss 0.031, p 2.3e-01 | 0.2300 BELOW, loss 0.071, p 2.0e-02 | 0.4500 BELOW, loss 0.011, p 3.4e-01 | 0.5875 AT, loss 0.029, p 5.9e-02 |
| reword 50% | Rewording | gradient | 0.2525 BELOW, loss -0.031, p 8.9e-01 | 0.2200 BELOW, loss 0.111, p 3.7e-03 | 0.4550 BELOW, loss 0.000, p 6.0e-01 | 0.5775 AT, loss 0.045, p 1.7e-02 |
| reword 100% | Rewording | yes | 0.2450 BELOW, loss 0.000, p 5.9e-01 | 0.2025 BELOW, loss 0.182, p 2.7e-04 | 0.4300 BELOW, loss 0.055, p 7.7e-02 | 0.5525 BELOW, loss 0.087, p 9.6e-04 |
| fragment partial | Fragmentation | gradient | 0.2450 BELOW, loss 0.000, p 1.0e+00 | 0.2300 BELOW, loss 0.071, p 3.3e-02 | 0.4650 BELOW, loss -0.022, p 8.8e-01 | 0.6225 AT, loss -0.029, p 9.8e-01 |
| fragment complete | Fragmentation | yes | 0.2450 BELOW, loss 0.000, p 1.0e+00 | 0.2375 BELOW, loss 0.040, p 2.4e-01 | 0.4525 BELOW, loss 0.005, p 5.0e-01 | 0.6125 AT, loss -0.012, p 7.6e-01 |
| vague moderate | Vagueness | yes | 0.2375 BELOW, loss 0.031, p 2.5e-01 | 0.2425 BELOW, loss 0.020, p 3.9e-01 | 0.4575 BELOW, loss -0.005, p 7.7e-01 | 0.6050 AT, loss 0.000, p 6.6e-01 |
| vague high | Vagueness | gradient | 0.2375 BELOW, loss 0.031, p 2.7e-01 | 0.2300 BELOW, loss 0.071, p 9.5e-02 | 0.4600 BELOW, loss -0.011, p 8.6e-01 | 0.5925 AT, loss 0.021, p 1.8e-01 |

Calibration and abstention under every condition:

| Condition | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|
| remove 1 finding | cal 0.1372 BELOW; abst 0.0225 BELOW | cal 0.0757 AT; abst 0.0025 BELOW | cal 0.0809 AT; abst 0.3450 BELOW | cal 0.0386 AT; abst 0.8250 ABOVE |
| remove 2 findings | cal 0.0999 AT; abst 0.0100 BELOW | cal 0.0469 AT; abst 0.0075 BELOW | cal 0.0880 AT; abst 0.3900 BELOW | cal 0.0496 AT; abst 0.7775 ABOVE |
| remove 3 findings | cal 0.1064 AT; abst 0.0075 BELOW | cal 0.0620 AT; abst 0.0075 BELOW | cal 0.0773 AT; abst 0.1550 BELOW | cal 0.1089 BELOW; abst 0.4675 AT |
| reword 25% | cal 0.1325 BELOW; abst 0.0200 BELOW | cal 0.0465 AT; abst 0.0025 BELOW | cal 0.0715 AT; abst 0.3950 BELOW | cal 0.0479 AT; abst 0.9150 ABOVE |
| reword 50% | cal 0.1422 BELOW; abst 0.0225 BELOW | cal 0.0601 AT; abst 0.0025 BELOW | cal 0.0529 AT; abst 0.3950 BELOW | cal 0.0660 AT; abst 0.8750 ABOVE |
| reword 100% | cal 0.1369 BELOW; abst 0.0200 BELOW | cal 0.0405 AT; abst 0.0000 BELOW | cal 0.0708 AT; abst 0.2500 BELOW | cal 0.0815 AT; abst 0.7975 ABOVE |
| fragment partial | cal 0.1393 BELOW; abst 0.0225 BELOW | cal 0.0549 AT; abst 0.0025 BELOW | cal 0.0471 AT; abst 0.3900 BELOW | cal 0.0582 AT; abst 1.0000 ABOVE |
| fragment complete | cal 0.1393 BELOW; abst 0.0225 BELOW | cal 0.0450 AT; abst 0.0025 BELOW | cal 0.0492 AT; abst 0.3100 BELOW | cal 0.0663 AT; abst 0.9775 ABOVE |
| vague moderate | cal 0.1274 BELOW; abst 0.0225 BELOW | cal 0.0564 AT; abst 0.0000 BELOW | cal 0.0588 AT; abst 0.4100 BELOW | cal 0.0688 AT; abst 0.9750 ABOVE |
| vague high | cal 0.1338 BELOW; abst 0.0225 BELOW | cal 0.0400 AT; abst 0.0000 BELOW | cal 0.0648 AT; abst 0.3825 BELOW | cal 0.0719 AT; abst 0.9350 ABOVE |

## H3. Breaking distance

SUPPORTED. The smallest breaking distance is 18.7 percent.

| Model | BELOW property | Mark | Must move to | Movement | Can one mark change the verdict |
|---|---|---|---|---|---|
| TF-IDF retrieval | accuracy | 0.6200 | 0.2894 | down 53.3% | no, 3 properties are BELOW |
| TF-IDF retrieval | calibration | 0.0786 | 0.1033 | up 31.4% | no, 3 properties are BELOW |
| TF-IDF retrieval | abstention | 0.5000 | 0.0422 | down 91.6% | no, 3 properties are BELOW |
| Encoder, no fine-tuning | accuracy | 0.6200 | 0.2921 | down 52.9% | no, 2 properties are BELOW |
| Encoder, no fine-tuning | abstention | 0.5000 | 0.0140 | down 97.2% | no, 2 properties are BELOW |
| Encoder, fine-tuned 2 epochs | accuracy | 0.6200 | 0.5040 | down 18.7% | yes, at 18.7% |

Grades that move when one mark is shifted by one tenth of its value:

| Model | Property | Mark moved to | Grade was | Grade becomes |
|---|---|---|---|---|
| TF-IDF retrieval | robustness | 0.7093 | AT | ABOVE |
| Encoder, no fine-tuning | robustness | 0.8669 | AT | BELOW |
| Encoder, fine-tuned 2 epochs | robustness | 0.7093 | AT | ABOVE |
| Encoder, fine-tuned 2 epochs | robustness | 0.8669 | AT | BELOW |
| Encoder, fine-tuned 2 epochs | abstention | 0.4500 | AT | ABOVE |
| Encoder, fine-tuned 8 epochs | accuracy | 0.6820 | AT | BELOW |
| Encoder, fine-tuned 8 epochs | robustness | 0.7093 | AT | ABOVE |

## Robustness under each matching rule

| Rule | Fixed mark | Recomputed | Physician M3 | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|---|---|---|
| short name only | 0.7822 | 0.7822 (1128 of 1442) [0.7602, 0.8028] | 0.5225, 0.5550, 0.7250 | AT | AT | AT | AT |
| short or full name (adopted) | 0.7881 | 0.7881 (1220 of 1548) [0.7671, 0.8077] | 0.5600, 0.6000, 0.7750 | AT | AT | AT | AT |
| any gold-list entry | 0.8960 | 0.8949 (1890 of 2112) [0.8811, 0.9073] | 0.7950, 0.8750, 0.9700 | AT | BELOW | BELOW | BELOW |

## Calibration and abstention under the three recalibration procedures

| Procedure | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|
| Temperature fitted on training folds, as first run | ECE 0.1786 [0.1571, 0.2384] BELOW; coverage 0.0200 BELOW | ECE 0.0869 [0.0625, 0.1347] AT; coverage 0.0000 BELOW | ECE 0.0865 [0.0604, 0.1371] AT; coverage 0.5275 AT | ECE 0.2219 [0.1802, 0.2679] BELOW; coverage 0.9750 ABOVE |
| Temperature fitted out of sample, Section 3.4 (graded) | ECE 0.1394 [0.1033, 0.1792] BELOW; coverage 0.0225 BELOW | ECE 0.0422 [0.0385, 0.1037] AT; coverage 0.0025 BELOW | ECE 0.0634 [0.0481, 0.1178] AT; coverage 0.5075 AT | ECE 0.0577 [0.0523, 0.1231] AT; coverage 0.9750 ABOVE |
| Isotonic regression, fitted out of sample | ECE 0.0749 [0.0543, 0.1203] AT; coverage 0.0350 BELOW | ECE 0.0439 [0.0428, 0.1086] AT; coverage 0.0000 BELOW | ECE 0.1018 [0.0667, 0.1439] AT; coverage 0.5025 AT | ECE 0.0559 [0.0512, 0.1233] AT; coverage 0.9700 ABOVE |

Grades that differ across the three procedures (as first run, out of sample, isotonic): TF-IDF retrieval calibration: BELOW, BELOW, AT; Encoder, fine-tuned 8 epochs calibration: BELOW, AT, AT.

## Supporting analyses

Closed-set ceiling. 167 of 400 cases have a reference diagnosis absent from their own training fold (131 singletons and 36 whose cases fell in the same fold), so a closed-set classifier is capped at 0.5825.

Two epochs against eight epochs, paired on the same 400 cases. The longer run gains 79 cases and loses 19. One-sided exact McNemar p = 3.56e-10.

Accuracy and abstention across the 4 models correlate at r = 0.997.

Difficulty strata, from the three physicians:

| Physicians correct | Cases | TF-IDF retrieval | Encoder, no fine-tuning | Encoder, fine-tuned 2 epochs | Encoder, fine-tuned 8 epochs |
|---|---|---|---|---|---|
| 3 of 3 | 171 | M3 0.3099, mean confidence 0.2149 | M3 0.2924, mean confidence 0.2571 | M3 0.5556, mean confidence 0.4926 | M3 0.6959, mean confidence 0.6269 |
| 2 of 3 | 96 | M3 0.2292, mean confidence 0.1615 | M3 0.2292, mean confidence 0.2550 | M3 0.3542, mean confidence 0.4377 | M3 0.5938, mean confidence 0.5712 |
| 1 of 3 | 67 | M3 0.1791, mean confidence 0.2088 | M3 0.2388, mean confidence 0.2402 | M3 0.4478, mean confidence 0.4561 | M3 0.5373, mean confidence 0.5872 |
| 0 of 3 | 66 | M3 0.1667, mean confidence 0.1766 | M3 0.1667, mean confidence 0.2091 | M3 0.3485, mean confidence 0.4413 | M3 0.4545, mean confidence 0.5933 |

Leakage audit. On the full serialized input, the most similar pair is cases 43 and 268 (meniere disease; meniere disease) at 0.7686, and 0 pairs reach 0.80. On the absent findings removed, the most similar pair is cases 43 and 268 (meniere disease; meniere disease) at 0.8848, and 1 pairs reach 0.80.

Non-redundancy check. Grade distribution: accuracy BELOW/BELOW/BELOW/AT; robustness AT/AT/AT/AT; calibration BELOW/AT/AT/AT; abstention BELOW/BELOW/AT/ABOVE; auditability ABOVE/ABOVE/ABOVE/ABOVE.

## Hypotheses

| Hypothesis | Question | Verdict |
|---|---|---|
| H1 | Does a non-accuracy property separate a pair of models where accuracy does not deliver that separation? | NOT SUPPORTED |
| H2 | Does a profile measured on clean input hold under degraded input? | SUPPORTED |
| H3 | Does every breaking distance exceed 10 percent? | SUPPORTED |
