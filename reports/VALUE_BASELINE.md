# Value baseline report

**Read this first.** Agent results are measured against the golden set on 50 synthetic files. Manual-process numbers (minutes per condition, rework rate, queue wait) are ILLUSTRATIVE assumptions in `config_log/value_assumptions.json`, not measurements. In a real engagement they come from the client's signed process blueprint and every result is compared to that baseline.

## Headline metrics

| Metric | baseline_v1 | tuned_v2 |
|---|---|---|
| Conditions scored | 208 | 208 |
| Automation rate (agent decides itself) | 78.8% | 82.2% |
| Safe automation rate (decides itself and is right) | 61.5% | 82.2% |
| Divergence rate vs golden | 31.2% | 0.5% |
| False approvals (agent satisfied, golden not satisfied) | 13 | 0 |

## Divergence rate by condition family

| Family | baseline_v1 | tuned_v2 |
|---|---|---|
| income_proof | 32.6% | 2.3% |
| down_payment_source | 31.8% | 0.0% |
| appraisal | 25.0% | 0.0% |
| employment | 34.1% | 0.0% |
| debt_ratio | 32.5% | 0.0% |

## Estimated interventions, effort, cycle time and rework (assumption-driven)

| Metric | baseline_v1 | tuned_v2 |
|---|---|---|
| Human touches, manual process (50 files) | 233 | 233 |
| Human touches, with agent (50 files) | 96 | 54 |
| Touches avoided | 137 (58.6%) | 179 (76.8%) |
| Handling hours saved (50 files) | 44.6 h | 55.5 h |
| Handling hours saved, scaled to 1000 files | 891 h | 1111 h |
| Avg queue wait per condition, manual | 4.0 h | 4.0 h |
| Avg queue wait per condition, with agent | 0.93 h (76.9% lower) | 0.79 h (80.2% lower) |
| Rework rate, manual (assumed) | 12.0% | 12.0% |
| Rework rate caused by wrong automated decisions (measured) | 17.3% | 0.0% |

## How to read the numbers

- A high automation rate is only valuable if the safe automation rate is close to it. The gap between the two is wrong automated decisions, each of which becomes rework.
- False approvals are the risk metric. They are reported separately because one false approval can cost more than many saved minutes.
- Touches avoided and hours saved move with the assumptions. Change a parameter in `config_log/value_assumptions.json` and rerun `python tools/value_baseline.py` to see sensitivity.
- Rework from wrong automated decisions is counted in full (conservative). A QA sample would catch only part of it before it reaches a borrower.
