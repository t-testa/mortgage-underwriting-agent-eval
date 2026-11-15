# Shadow run: holdout_baseline_v1

Arbitration rules included in the agent's policy: **no**

- Conditions scored: 87
- Correct: 60 (69.0%)
- Divergences (review queue size): 27
- False approvals (agent satisfied, golden not satisfied): 6
- Skipped escalations (agent satisfied, golden needs review): 2

## Accuracy and divergence by family

| Family | Conditions | Correct | Accuracy | Divergence rate |
|---|---|---|---|---|
| income_proof | 19 | 13 | 68% | 32% |
| down_payment_source | 17 | 10 | 59% | 41% |
| appraisal | 19 | 16 | 84% | 16% |
| employment | 15 | 10 | 67% | 33% |
| debt_ratio | 17 | 11 | 65% | 35% |

## Confusion matrix (rows golden, columns agent)

| golden / agent | satisfied | not_satisfied | needs_review | no_answer |
|---|---|---|---|---|
| satisfied | 41 | 1 | 8 | 0 |
| not_satisfied | 6 | 9 | 7 | 0 |
| needs_review | 2 | 3 | 10 | 0 |

## Review queue by reason tag

| Reason | Count |
|---|---|
| agent_error | 5 |
| policy_ambiguity | 22 |

## Review queue by severity

| Severity | Count |
|---|---|
| P1 critical (false approval) | 6 |
| P2 high (skipped a required escalation) | 2 |
| P3 medium (decided a policy call) | 3 |
| P3 medium (false decline, causes rework) | 1 |
| P4 low (over-escalation, extra human touch) | 15 |
