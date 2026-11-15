# Shadow run: tuned_v2

Arbitration rules included in the agent's policy: **yes**

- Conditions scored: 208
- Correct: 207 (99.5%)
- Divergences (review queue size): 1
- False approvals (agent satisfied, golden not satisfied): 0
- Skipped escalations (agent satisfied, golden needs review): 0

## Accuracy and divergence by family

| Family | Conditions | Correct | Accuracy | Divergence rate |
|---|---|---|---|---|
| income_proof | 43 | 42 | 98% | 2% |
| down_payment_source | 44 | 44 | 100% | 0% |
| appraisal | 40 | 40 | 100% | 0% |
| employment | 41 | 41 | 100% | 0% |
| debt_ratio | 40 | 40 | 100% | 0% |

## Confusion matrix (rows golden, columns agent)

| golden / agent | satisfied | not_satisfied | needs_review | no_answer |
|---|---|---|---|---|
| satisfied | 105 | 0 | 1 | 0 |
| not_satisfied | 0 | 66 | 0 | 0 |
| needs_review | 0 | 0 | 36 | 0 |

## Review queue by reason tag

| Reason | Count |
|---|---|
| agent_error | 1 |

## Review queue by severity

| Severity | Count |
|---|---|
| P4 low (over-escalation, extra human touch) | 1 |
