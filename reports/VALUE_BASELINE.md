# Value baseline report

**Read this first.** Agent results are measured against the golden set. Columns baseline_v1 and tuned_v2 use the 50 tuning files; holdout_* columns use 20 unseen files (MF-101 to MF-120) and a separate, hash-locked golden set. Manual-process numbers (minutes per condition, rework rate, queue wait) are ILLUSTRATIVE assumptions in `config_log/value_assumptions.json`, not measurements. In a real engagement they come from the client's signed process blueprint and every result is compared to that baseline.

## Headline metrics

| Metric | baseline_v1 | tuned_v2 | holdout_baseline_v1 | holdout_tuned_v2 |
|---|---|---|---|---|
| Files / conditions scored | 50 / 208 | 50 / 208 | 20 / 87 | 20 / 87 |
| Accuracy vs golden | 68.8% | 99.5% | 69.0% | 98.9% |
| Automation rate (agent decides itself) | 78.8% | 82.2% | 71.3% | 81.6% |
| Safe automation rate (decides itself and is right) | 61.5% | 82.2% | 57.5% | 81.6% |
| Divergence rate vs golden | 31.2% | 0.5% | 31.0% | 1.1% |
| False approvals (agent satisfied, golden not satisfied) | 13 | 0 | 6 | 0 |

## Divergence rate by condition family

| Family | baseline_v1 | tuned_v2 | holdout_baseline_v1 | holdout_tuned_v2 |
|---|---|---|---|---|
| income_proof | 32.6% | 2.3% | 31.6% | 5.3% |
| down_payment_source | 31.8% | 0.0% | 41.2% | 0.0% |
| appraisal | 25.0% | 0.0% | 15.8% | 0.0% |
| employment | 34.1% | 0.0% | 33.3% | 0.0% |
| debt_ratio | 32.5% | 0.0% | 35.3% | 0.0% |

## Estimated interventions, effort, cycle time and rework (assumption-driven)

| Metric | baseline_v1 | tuned_v2 | holdout_baseline_v1 | holdout_tuned_v2 |
|---|---|---|---|---|
| Human touches, manual process (this run's files) | 233 | 233 | 97 | 97 |
| Human touches, with agent (this run's files) | 96 | 54 | 43 | 23 |
| Touches avoided | 137 (58.6%) | 179 (76.8%) | 54 (55.7%) | 74 (76.3%) |
| Handling hours saved (this run's files) | 44.6 h | 55.5 h | 17.9 h | 22.8 h |
| Handling hours saved, scaled to 1000 files | 891 h | 1111 h | 897 h | 1142 h |
| Avg queue wait per condition, manual | 4.0 h | 4.0 h | 4.0 h | 4.0 h |
| Avg queue wait per condition, with agent | 0.93 h (76.9% lower) | 0.79 h (80.2% lower) | 1.22 h (69.5% lower) | 0.82 h (79.6% lower) |
| Rework rate, manual (assumed) | 12.0% | 12.0% | 12.0% | 12.0% |
| Rework rate caused by wrong automated decisions (measured) | 17.3% | 0.0% | 13.8% | 0.0% |

## How to read the numbers

- A high automation rate is only valuable if the safe automation rate is close to it. The gap between the two is wrong automated decisions, each of which becomes rework.
- False approvals are the risk metric. They are reported separately because one false approval can cost more than many saved minutes.
- Touches avoided and hours saved move with the assumptions. Change a parameter in `config_log/value_assumptions.json` and rerun `python tools/value_baseline.py` to see sensitivity.
- Rework from wrong automated decisions is counted in full (conservative). A QA sample would catch only part of it before it reaches a borrower.
