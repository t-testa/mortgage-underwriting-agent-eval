# Calibration report: Team A vs Team B

Both teams are SIMULATED (scripted house styles plus 3% random slips). See `tools/calibrate.py`.

## Agreement by condition family

| Family | Conditions | Raw agreement | Cohen's kappa | Reading |
|---|---|---|---|---|
| appraisal | 40 | 82% | 0.68 | substantial |
| debt_ratio | 40 | 88% | 0.77 | substantial |
| down_payment_source | 44 | 84% | 0.72 | substantial |
| employment | 41 | 71% | 0.52 | moderate |
| income_proof | 43 | 70% | 0.52 | moderate |
| **All families** | 208 | 79% | **0.64** | substantial |

Kappa corrects raw agreement for the agreement two labelers would reach by chance. A common working target before production labeling is 0.80 or higher.

## Disagreements: 44 of 208 conditions

Grouped into patterns. Each recurring pattern is a candidate arbitration rule (see `policy/ARBITRATION_RULES.md`). One-off slips are listed in `disagreements.csv`.

| Count | Family | Rule | Scenario | Team A | Team B |
|---|---|---|---|---|---|
| 4 | debt_ratio | DTI-03 | exception_band | needs_review | not_satisfied |
| 2 | appraisal | APP-02 | shortfall_mid | satisfied | needs_review |
| 2 | appraisal | APP-02 | shortfall_small | satisfied | needs_review |
| 2 | down_payment_source | DP-03 | unexplained_mid | satisfied | needs_review |
| 2 | down_payment_source | DP-04 | gift_far_relation | needs_review | not_satisfied |
| 2 | employment | EMP-04 | probation | satisfied | not_satisfied |
| 2 | employment | EMP-06 | salary_mismatch | needs_review | not_satisfied |
| 2 | income_proof | INC-03 | shortfall_mid | satisfied | needs_review |
| 2 | income_proof | INC-03 | shortfall_small | satisfied | needs_review |
| 2 | income_proof | INC-05 | variable_two_year | satisfied | needs_review |
| 2 | income_proof | INC-06 | illegible | needs_review | not_satisfied |
| 1 | appraisal | APP-02 | shortfall_mid | needs_review | not_satisfied |
| 1 | appraisal | APP-05 | recommend_inspection | needs_review | satisfied |
| 1 | appraisal | APP-05 | recommend_inspection | satisfied | needs_review |
| 1 | debt_ratio | DTI-01 | clean | satisfied | not_satisfied |
| 1 | down_payment_source | DP-02 | insufficient_clear | not_satisfied | satisfied |
| 1 | down_payment_source | DP-04 | gift_far_relation | satisfied | needs_review |
| 1 | down_payment_source | DP-04 | gift_far_relation | satisfied | not_satisfied |
| 1 | employment | EMP-01 | stale_edge | not_satisfied | satisfied |
| 1 | employment | EMP-03 | contract_long | satisfied | needs_review |
| 1 | employment | EMP-04 | probation | needs_review | not_satisfied |
| 1 | employment | EMP-04 | probation | satisfied | needs_review |
| 1 | employment | EMP-05 | contract_mid | needs_review | not_satisfied |
| 1 | employment | EMP-05 | contract_mid | satisfied | needs_review |
| 1 | employment | EMP-05 | contract_mid | satisfied | not_satisfied |
| 1 | employment | EMP-05 | contract_short | satisfied | not_satisfied |
| 1 | income_proof | INC-01 | stale_edge | not_satisfied | satisfied |
| 1 | income_proof | INC-03 | clean | needs_review | satisfied |
| 1 | income_proof | INC-03 | clean | satisfied | needs_review |
| 1 | income_proof | INC-05 | variable_one_year | not_satisfied | needs_review |
| 1 | income_proof | INC-05 | variable_one_year | satisfied | needs_review |
