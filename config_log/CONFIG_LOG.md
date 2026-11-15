# Config log

Every change to the agent's configuration, with the reason and the measured effect. The golden set
(`golden/golden_set.csv`) was not touched in any round. Both runs were scored by the same `tools/score_run.py`.

## Round 1 (baseline) : config v1
| Item | Value |
|---|---|
| Prompt | `prompts/agent_prompt_v1.md` (short, generic) |
| Policy given to agent | `policy/POLICY_v1_0.md` (client wording, vague in places) |
| Runner | Five fresh Claude Code subagents (Sonnet), 10 files each, blind to the golden set |
| Result | 143 of 208 correct (68.8%); 65 divergences; 13 false approvals; 11 skipped escalations |
| Queue tags | 55 policy_ambiguity, 7 agent_error, 3 missing_document |

### Diagnosis from the review queue
1. Most divergences sit on rules where policy v1.0 gave no number (thresholds, document age, "sufficient history",
   how to count liabilities). That is a policy problem, not a model problem.
2. The agent was too lenient on stale documents and short bank history (false approvals).
3. The agent over-escalated rules it could have decided (extra human touches), and escalated illegible documents instead of rejecting.
4. Some arithmetic was not shown, so reviewers could not check it quickly.

## Round 2 (tuned) : config v2
| ID | Change | Why | Expected effect |
|---|---|---|---|
| C-001 | Policy v1.0 replaced by v1.1 (v1.0 plus the 16 arbitration rules) | Diagnosis 1 and 2 | Fewer policy-ambiguity divergences, fewer false approvals |
| C-002 | Prompt adds an explicit method: take the review date, extract facts, compute the numbers, show them | Diagnosis 4 | Fewer arithmetic and date errors, auditable rationale |
| C-003 | Prompt adds precedence (not satisfied beats needs review beats satisfied) and "missing or unreadable is not satisfied" | Diagnosis 3 | Less over-escalation |
| C-004 | Prompt says: escalate only where a rule says so | Diagnosis 3 | Fewer extra human touches |

| Item | Value |
|---|---|
| Prompt | `prompts/agent_prompt_v2.md` |
| Policy given to agent | `policy/POLICY_v1_1.md` |
| Runner | Five fresh Claude Code subagents (Sonnet), same split, blind to the golden set |
| Result | 207 of 208 correct (99.5%); 1 divergence (an over-escalation); 0 false approvals |

## Before and after
| Metric | Before (v1) | After (v2) |
|---|---|---|
| Accuracy | 68.8% | 99.5% |
| Divergences | 65 | 1 |
| False approvals | 13 | 0 |
| Skipped escalations | 11 | 0 |

## What this does and does not show
- C-001 to C-004 were applied together, so the effect of each is not separated. On real work, change one thing per round.
- The 55 of 65 baseline divergences tagged policy ambiguity say the biggest lever was fixing the policy text, not
  changing the model.
- The "after" score is close to a ceiling. The golden labels are computed from the same rules that are now in the agent's
  policy, and the documents are cleaner than real ones. Do not read 99.5% as expected production accuracy.
- The failures were diagnosed on the same 50 files they were then scored on. A real round needs a holdout set.
- The one remaining divergence (MF-003-C1) shows a real behaviour worth keeping: the agent compared the NOA to
  stated income as well as the paystub, and escalated when the two sources pointed different ways. The rule says
  to use the annualized paystub, so it is scored as an error, but it is a sensible reviewer instinct and a candidate
  for a clarifying rule.
