# Shadow run: baseline_v1

Arbitration rules included in the agent's policy: **no**

- Conditions scored: 208
- Correct: 143 (68.8%)
- Divergences (review queue size): 65
- False approvals (agent satisfied, golden not satisfied): 13
- Skipped escalations (agent satisfied, golden needs review): 11

## Accuracy and divergence by family

| Family | Conditions | Correct | Accuracy | Divergence rate |
|---|---|---|---|---|
| income_proof | 43 | 29 | 67% | 33% |
| down_payment_source | 44 | 30 | 68% | 32% |
| appraisal | 40 | 30 | 75% | 25% |
| employment | 41 | 27 | 66% | 34% |
| debt_ratio | 40 | 27 | 68% | 32% |

## Confusion matrix (rows golden, columns agent)

| golden / agent | satisfied | not_satisfied | needs_review | no_answer |
|---|---|---|---|---|
| satisfied | 95 | 2 | 9 | 0 |
| not_satisfied | 13 | 33 | 20 | 0 |
| needs_review | 11 | 10 | 15 | 0 |

## Review queue by reason tag

| Reason | Count |
|---|---|
| agent_error | 7 |
| missing_document | 3 |
| policy_ambiguity | 55 |

## Review queue by severity

| Severity | Count |
|---|---|
| P1 critical (false approval) | 13 |
| P2 high (skipped a required escalation) | 11 |
| P3 medium (decided a policy call) | 10 |
| P3 medium (false decline, causes rework) | 2 |
| P4 low (over-escalation, extra human touch) | 29 |
