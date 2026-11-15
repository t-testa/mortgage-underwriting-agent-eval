# Mortgage underwriting agent evaluation

A small portfolio project that shows how I would onboard an AI underwriting agent (in the style of nesto's Maestro) onto a new
family of underwriting conditions, and prove whether it can be trusted. **All data is synthetic.** Nothing here is nesto data,
nesto policy, or a real borrower. The policy, the two underwriting teams and the business-case numbers are invented.

## 1. The business problem

A mortgage file is approved subject to conditions: prove your income, show where the down payment came from, get an
appraisal, confirm your job, show your debts are manageable. Today an underwriter checks each condition by hand. That is slow,
and two underwriters often read the same document differently.

An AI agent can make many of these decisions in seconds. But "the AI is accurate" is not an acceptable answer for a lender.
The questions that matter are:
- Compared with what? (You need an agreed answer key.)
- Where does it go wrong, and are those errors dangerous (approving something that should fail)?
- Is the policy itself clear enough for anyone, human or AI, to apply the same way?
- How much work does it actually remove, and how do you know?

This repo walks through the method for answering those questions, end to end, on 208 conditions across 50 files.

## 2. How it works (seven steps)

| Step | What happens | Where |
|---|---|---|
| 1. Files | 50 synthetic mortgage files, each with 3 to 5 conditions (income proof, down payment source, appraisal, employment, debt ratio). Documents are text and deliberately messy: mixed date and currency formats, French and English, scanner typos, irrelevant pages. | `data/files/`, `tools/generate_data.py` |
| 2. Golden set | The correct decision for every condition (satisfied, not satisfied, needs review) plus the policy rule behind it. This is the answer key. | `golden/golden_set.csv` |
| 3. Calibration | Two simulated underwriting teams label all 50 files. I measure agreement (Cohen's kappa) per family, list disagreements, and write arbitration rules to close them. | `calibration/`, `policy/ARBITRATION_RULES.md` |
| 4. Shadow mode | The agent (Claude) decides every condition from the documents. Nothing is acted on. Each divergence from the golden set goes to a review queue with a reason tag. | `shadow/runs/` |
| 5. Tuning | One round of prompt and config changes, logged with before and after accuracy. The golden set is never changed. | `config_log/CONFIG_LOG.md`, `prompts/` |
| 6. Value baseline | Automation rate, divergence by family, touches, cycle time and rework. | `reports/VALUE_BASELINE.md` |
| 7. Playbook and RAID | How to repeat this for the next family, and the risk log. | `PLAYBOOK.md`, `RAID.md` |

### Design decisions you can defend in an interview
- **Why a golden set, and why never change it.** If you edit the answer key after seeing the agent's mistakes, you are
  marking your own homework. Wrong labels are fixed through a dated adjudication, and every earlier result is rerun.
- **Why calibration comes first.** If two human teams only agree 64% of the time (kappa 0.64 here), the answer key is shaky and
  the agent's score would be meaningless. Disagreement points at unclear policy, and unclear policy is cheaper to fix than a model.
- **Why three decision values.** "Needs review" is a legitimate answer. A good agent knows when to hand over. It also means errors
  have different costs: approving something that should fail is critical; escalating something it could have decided is only an extra touch.
- **Why tag every divergence.** The fix depends on the cause. Policy ambiguity is fixed by writing a rule, a missing document by
  better intake, an agent error by changing the prompt or configuration.
- **Why report false approvals separately.** A 95% accuracy figure can hide the one error that matters.
- **Why the baseline agent was given the vague policy.** That is what a client hands you on day one. The tuning round then shows
  what happens when the policy gets fixed.
- **Why the golden set is computed, not hand-typed.** Each document and its answer are generated from the same small record, so
  the key cannot drift from the documents. The cost is circularity, see limitations.

## 3. Results

### Calibration (two simulated teams, 208 conditions)
| Family | Agreement | Cohen's kappa |
|---|---|---|
| appraisal | 82% | 0.68 |
| debt_ratio | 88% | 0.77 |
| down_payment_source | 84% | 0.72 |
| employment | 71% | 0.52 |
| income_proof | 70% | 0.52 |
| **All** | **79%** | **0.64** |

None of the families reached the 0.80 working target. 44 conditions had disagreements; the repeated patterns became 16 arbitration
rules, 7 of which are threshold decisions that would go to a UW Expert and 9 of which a delivery manager can close.
Full detail: [calibration/kappa_report.md](calibration/kappa_report.md).

### Shadow mode and tuning
| | Baseline (v1) | After tuning (v2) |
|---|---|---|
| Accuracy vs golden | 68.8% (143 of 208) | 99.5% (207 of 208) |
| Divergences in review queue | 65 | 1 |
| False approvals | 13 | 0 |
| Skipped escalations (agent approved, should have escalated) | 11 | 0 |
| Review queue tags | 55 policy ambiguity, 7 agent error, 3 missing document | 1 agent error |

The headline finding is the baseline queue: **most divergence came from vague policy, not from the model.** Fixing the policy text
(arbitration rules) and asking the agent to show its arithmetic did most of the work. Details and the change list:
[config_log/CONFIG_LOG.md](config_log/CONFIG_LOG.md).

### Value baseline (assumption-driven, see warning)
| | Baseline (v1) | Tuned (v2) |
|---|---|---|
| Automation rate (agent decides itself) | 78.8% | 82.2% |
| Safe automation rate (decides itself and right) | 61.5% | 82.2% |
| Human touches avoided vs all-manual | 58.6% | 76.8% |
| Avg queue wait per condition | 0.93 h vs 4.0 h manual | 0.79 h vs 4.0 h manual |

Why the two automation rates matter: the baseline agent "decided" 79% of conditions on its own but only 61% correctly. The gap
is wrong automated decisions, each of which becomes rework. Full report: [reports/VALUE_BASELINE.md](reports/VALUE_BASELINE.md).
The manual-process figures (minutes per condition, 12% rework, 4 h queue wait) are my illustrative assumptions in
`config_log/value_assumptions.json`, not measurements.

## 4. Limitations (please read)

1. **The data is synthetic and cleaner than reality.** Real documents have problems this generator does not produce
   (skewed scans, handwriting, tables that break, contradictory documents). Known generator flaw: a bill of sale can be dated after the deposit it explains.
2. **The 99.5% is close to a ceiling, not a forecast.** The golden labels are computed from the same rules that were then given to the
   agent in policy v1.1. A sharp reader will see that is nearly circular. What the result does show is the relative effect: the same model went
   from 68.8% to 99.5% mainly by fixing policy wording.
3. **Tuned and scored on the same 50 files.** Failures were diagnosed on the files they were then measured on. A real tuning round needs a
   holdout set the agent has not seen.
4. **The two underwriting teams are scripts, not people.** Each has a stated house style plus a small random slip rate
   (`tools/calibrate.py`). The kappa numbers demonstrate the method, not real underwriter behaviour. The disagreement table also
   uses a scenario tag only a generator would know.
5. **The agent was run through Claude Code subagents, not the API.** Five fresh Sonnet subagents per round, given only the prompt,
   the policy and the documents (the golden set was never in their workspace). One run per round, so no measure of run-to-run variation. I did not record an exact model version string.
   `tools/run_agent_api.py` is an optional API runner for repeating this; it has only been tested in dry-run mode.
6. **One tuning round with four bundled changes.** The effect of each change is not separated.
7. **Reason tags are a script's first pass.** A human would confirm them. The `policy_ambiguity` tag means the policy the agent was
   given did not settle the question; some of those divergences may still contain a genuine agent slip.
8. **Value numbers are illustrative.** Change `value_assumptions.json` and rerun `python tools/value_baseline.py` to see how
   sensitive the business case is.

## 5. Repeat it

```bash
python tools/generate_data.py        # files and golden set (deterministic)
python tools/calibrate.py            # kappa and disagreements
python tools/score_run.py --run baseline_v1 --raw-dir shadow/runs/baseline_v1/raw --ar-in-policy no
python tools/score_run.py --run tuned_v2 --raw-dir shadow/runs/tuned_v2/raw --ar-in-policy yes
python tools/value_baseline.py       # report
```
Python 3.10 or later, standard library only. The agent decisions are stored in `shadow/runs/*/raw/`.

## 6. Repository map
- `data/files/` 50 synthetic mortgage files (agent input)
- `golden/golden_set.csv` answer key
- `policy/` policy v1.0 (client wording), arbitration rules, policy v1.1
- `calibration/` both teams' labels, disagreements, kappa report
- `prompts/` agent prompts v1 and v2
- `shadow/runs/` decisions, metrics, summary and review queue for each run
- `config_log/` change log and value assumptions
- `reports/VALUE_BASELINE.md`
- `PLAYBOOK.md`, `RAID.md`
- `tools/` all scripts
