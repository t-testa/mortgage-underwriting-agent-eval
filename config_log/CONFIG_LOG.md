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
- The failures were diagnosed on the same 50 files they were then scored on. That concern is tested in the holdout
  section below: on 20 unseen files the frozen tuned config scored 98.9%.
- The one remaining divergence (MF-003-C1) shows a real behaviour worth keeping: the agent compared the NOA to
  stated income as well as the paystub, and escalated when the two sources pointed different ways. The rule says
  to use the annualized paystub, so it is scored as an error, but it is a sensible reviewer instinct and a candidate
  for a clarifying rule.

## Holdout evaluation (config frozen, no changes)

**Freeze point.** Configs v1 and v2 were frozen at commit `792b9b94d6eff76db546d8471b8f85f3366eb2bc`, made before any agent ran on the
holdout files. That commit contains the holdout files and the locked holdout golden set. The agent prompts and policy files have not changed
since the first commit of this repo. SHA-256 of the frozen configs:

| File | SHA-256 |
|---|---|
| `prompts/agent_prompt_v1.md` | `41bcaf0a1f192c50ff0c5776437281549c26512c0701c16410f25e72962746e6` |
| `prompts/agent_prompt_v2.md` | `c2dce5f8160421842b8ae6b0b1eebc893717e51c72fc1f5a7f23a05d344b43fe` |
| `policy/POLICY_v1_0.md` | `1aac69d9770d31d860af3ae8794bd273275993e72ba87917aaf9a01159dc7ff2` |
| `policy/POLICY_v1_1.md` | `4695f8782ad1a3701d90746f88302414655f02adcdb23763304e0beddce0bdb7` |

**How it ran.** 20 new files (MF-101 to MF-120, seed 424242). Five fresh Sonnet subagents per config, four files each, each config in its own
workspace containing only the prompt, the policy and the documents. One run per config. No prompt, policy or config change after seeing results.
Holdout labels were computed by the generator before any agent output existed.

| Metric | Baseline v1 | Tuned v2 |
|---|---|---|
| Accuracy | 69.0% (60 of 87) | 98.9% (86 of 87) |
| False approvals | 6 | 0 |
| Divergences | 27 | 1 |

**Residual finding, not acted on.** The single tuned divergence (MF-112-C1) has the same cause as the single tuning-set miss (MF-003-C1): the agent
cross-checked the NOA against stated income and escalated, while the golden rule uses the annualized paystub. Proposed AR-17 ("for salaried
applicants, documented income is the annualized current paystub; the NOA only needs to be present") is **not** applied here. It would be config v3 and should
be tested on a fresh holdout, not the one that revealed it.

**Provenance notes.** The runs happened after the freeze commit but their results were committed afterwards, so the commit order is: freeze, then results.
The golden set for the tuning data was left untouched; its hash lock file was added later in the freeze commit (the file itself is byte-identical to the first commit).
