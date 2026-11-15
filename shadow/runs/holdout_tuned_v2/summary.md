# Shadow run: holdout_tuned_v2

Arbitration rules included in the agent's policy: **yes**

- Conditions scored: 87
- Correct: 86 (98.9%)
- Divergences (review queue size): 1
- False approvals (agent satisfied, golden not satisfied): 0
- Skipped escalations (agent satisfied, golden needs review): 0

## Accuracy and divergence by family

| Family | Conditions | Correct | Accuracy | Divergence rate |
|---|---|---|---|---|
| income_proof | 19 | 18 | 95% | 5% |
| down_payment_source | 17 | 17 | 100% | 0% |
| appraisal | 19 | 19 | 100% | 0% |
| employment | 15 | 15 | 100% | 0% |
| debt_ratio | 17 | 17 | 100% | 0% |

## Confusion matrix (rows golden, columns agent)

| golden / agent | satisfied | not_satisfied | needs_review | no_answer |
|---|---|---|---|---|
| satisfied | 49 | 0 | 1 | 0 |
| not_satisfied | 0 | 22 | 0 | 0 |
| needs_review | 0 | 0 | 15 | 0 |

## Review queue by reason tag

| Reason | Count |
|---|---|
| agent_error | 1 |

## Review queue by severity

| Severity | Count |
|---|---|
| P4 low (over-escalation, extra human touch) | 1 |
