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

This repo walks through the method for answering those questions, end to end, on 208 conditions across 50 files, then checks the result on 20 unseen files.

## 2. How it works (seven steps)

| Step | What happens | Where |
|---|---|---|
| 1. Files | 50 synthetic mortgage files, each with 3 to 5 conditions (income proof, down payment source, appraisal, employment, debt ratio). Documents are text and deliberately messy: mixed date and currency formats, French and English, scanner typos, irrelevant pages. | `data/files/`, `tools/generate_data.py` |
| 2. Golden set | The correct decision for every condition (satisfied, not satisfied, needs review) plus the policy rule behind it. This is the answer key. | `golden/golden_set.csv` |
| 3. Calibration | Two simulated underwriting teams label all 50 files. I measure agreement (Cohen's kappa) per family, list disagreements, and write arbitration rules to close them. | `calibration/`, `policy/ARBITRATION_RULES.md` |
| 4. Shadow mode | The agent (Claude) decides every condition from the documents. Nothing is acted on. Each divergence from the golden set goes to a review queue with a reason tag. | `shadow/runs/` |
| 5. Tuning | One round of prompt and config changes, logged with before and after accuracy. The golden set is never changed. | `config_log/CONFIG_LOG.md`, `prompts/` |
| 5b. Holdout | 20 NEW files (MF-101 to MF-120, different random seed) with their own hash-locked golden set. The frozen baseline and tuned configs each run once on them, with no changes after seeing results. | `data/holdout/`, `shadow/runs/holdout_*` |
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

### Shadow mode, tuning and holdout
Two sets of files. The **tuning set** (50 files) is where I diagnosed failures and wrote the fixes. The **holdout set** (20 new files, MF-101 to MF-120)
was generated with a different random seed and labelled before any agent saw it. Each config ran on it exactly once, frozen, with no edits afterwards.

| | Tuning set (50 files, 208 conditions) | | Holdout (20 unseen files, 87 conditions) | |
|---|---|---|---|---|
| | Baseline (v1) | Tuned (v2) | Baseline (v1) | Tuned (v2) |
| Accuracy vs golden | 68.8% (143 of 208) | 99.5% (207 of 208) | 69.0% (60 of 87) | 98.9% (86 of 87) |
| False approvals (agent approved, should fail) | 13 | 0 | 6 | 0 |
| Skipped escalations (agent approved, should escalate) | 11 | 0 | 2 | 0 |
| Safe automation rate | 61.5% | 82.2% | 57.5% | 81.6% |
| Review queue size | 65 | 1 | 27 | 1 |
| Queue tags | 55 policy ambiguity, 7 agent error, 3 missing document | 1 agent error | 22 policy ambiguity, 5 agent error | 1 agent error |

**What the gap between 99.5% and 98.9% means, in plain language.** I tuned the agent on the first 50 files, so the worry is that it just memorised them.
If that were true, the score on new files would drop sharply. It did not: it moved by 0.6 points, which is one condition out of 87. One condition is
1.1 points on this size of set, so a gap this small is within noise. The fix (clearer policy plus an explicit method) transferred to files the agent had never seen.
The baseline did the same thing on both sets (68.8% and 69.0%), which is a second sign that the two sets are comparable.

**What the holdout does not show.** The holdout answers "did you overfit?". It does not answer "will this work on real documents?". The holdout files come from the same generator
and the golden labels come from the same rules now written into policy v1.1, so a high score is partly built in. Treat 98.9% as evidence that the method works on new
instances of the same kind of problem, not as a forecast for production.

**Failure patterns.**
- *Baseline on holdout (27 divergences).* (1) Stale or thin documents accepted: 6 false approvals, from a stale paystub, letter and appraisal, a 60-day bank history and two funds shortfalls,
  almost all where policy v1.0 says only "current" or "seasoned". (2) Over-escalation: 15 conditions sent to review that the rules could decide, such as clear TDS failures and clean files, which is extra human work.
  (3) Judgment calls decided instead of escalated or the reverse: probation, exception band, far-relative gift, small appraisal shortfall.
- *Tuned on holdout (1 divergence, MF-112-C1).* The agent compared the Notice of Assessment as well as the paystub, found a 6.9% shortfall on the NOA, and escalated. The rule I wrote says to use the annualized paystub, so it is scored as an error.
  The same pattern caused the one miss on the tuning set (MF-003-C1). Two misses with one cause means a rule gap: policy v1.1 does not say which document defines "documented income" for salaried applicants. I have **not** fixed it, because the config is frozen. It is logged in `RAID.md` as the proposed next rule (AR-17).

Details and the change list: [config_log/CONFIG_LOG.md](config_log/CONFIG_LOG.md). Both golden sets are hash-locked (`python tools/verify_golden.py`).

### Value baseline (assumption-driven, see warning)
| | Tuning set: Baseline | Tuning set: Tuned | Holdout: Baseline | Holdout: Tuned |
|---|---|---|---|---|
| Automation rate (agent decides itself) | 78.8% | 82.2% | 71.3% | 81.6% |
| Safe automation rate (decides itself and right) | 61.5% | 82.2% | 57.5% | 81.6% |
| Human touches avoided vs all-manual | 58.6% | 76.8% | 55.7% | 76.3% |
| Avg queue wait per condition | 0.93 h | 0.79 h | 1.22 h | 0.82 h |

(Manual process: 4.0 h average queue wait per condition, an assumption.) Why the two automation rates matter: the baseline agent "decided" 71% to 79% of conditions on its own but only 58% to 62% correctly. The gap
is wrong automated decisions, each of which becomes rework. Full report: [reports/VALUE_BASELINE.md](reports/VALUE_BASELINE.md).
The manual-process figures (minutes per condition, 12% rework, 4 h queue wait) are my illustrative assumptions in
`config_log/value_assumptions.json`, not measurements.

## 4. Limitations (please read)

1. **The data is synthetic and cleaner than reality.** Real documents have problems this generator does not produce
   (skewed scans, handwriting, tables that break, contradictory documents). Known generator flaw: a bill of sale can be dated after the deposit it explains.
2. **The holdout shows the tuning transferred, not that it will work on real documents.** On 20 unseen files the tuned agent scored 98.9% against 99.5% on the tuning set, so it did not just memorise the first 50 files.
   But the holdout comes from the same generator, and its golden labels follow the same rules that policy v1.1 now spells out, so a high score is partly built in. Twenty files (87 conditions) is also small: one condition moves accuracy by 1.1 points.
   Real documents, and a real policy owner who disagrees with my thresholds, are the next test.
3. **The two underwriting teams are scripts, not people.** Each has a stated house style plus a small random slip rate
   (`tools/calibrate.py`). The kappa numbers demonstrate the method, not real underwriter behaviour. The disagreement table also
   uses a scenario tag only a generator would know.
4. **The agent was run through Claude Code subagents, not the API.** Five fresh Sonnet subagents per round and per set, given only the prompt,
   the policy and the documents (the golden set was never in their workspace). One run per config per set, so no measure of run-to-run variation. I did not record an exact model version string.
   `tools/run_agent_api.py` is an optional API runner for repeating this; it has only been tested in dry-run mode.
5. **One tuning round with four bundled changes.** The effect of each change is not separated.
6. **Reason tags are a script's first pass.** A human would confirm them. The `policy_ambiguity` tag means the policy the agent was
   given did not settle the question; some of those divergences may still contain a genuine agent slip.
7. **Value numbers are illustrative.** Change `value_assumptions.json` and rerun `python tools/value_baseline.py` to see how
   sensitive the business case is.

## 5. Repeat it

```bash
python tools/generate_data.py        # files and golden set (deterministic)
python tools/calibrate.py            # kappa and disagreements
python tools/score_run.py --run baseline_v1 --raw-dir shadow/runs/baseline_v1/raw --ar-in-policy no
python tools/score_run.py --run tuned_v2 --raw-dir shadow/runs/tuned_v2/raw --ar-in-policy yes
python tools/score_run.py --run holdout_baseline_v1 --raw-dir shadow/runs/holdout_baseline_v1/raw --ar-in-policy no --golden data/holdout/golden_set.csv
python tools/score_run.py --run holdout_tuned_v2 --raw-dir shadow/runs/holdout_tuned_v2/raw --ar-in-policy yes --golden data/holdout/golden_set.csv
python tools/verify_golden.py        # confirms both golden sets match their locked hashes
python tools/value_baseline.py       # report
```
Python 3.10 or later, standard library only. The agent decisions are stored in `shadow/runs/*/raw/`.

## 6. Repository map
- `data/files/` 50 synthetic mortgage files (agent input)
- `golden/golden_set.csv` answer key (hash in `golden_set.sha256`)
- `data/holdout/` 20 unseen files and their own hash-locked golden set
- `policy/` policy v1.0 (client wording), arbitration rules, policy v1.1
- `calibration/` both teams' labels, disagreements, kappa report
- `prompts/` agent prompts v1 and v2
- `shadow/runs/` decisions, metrics, summary and review queue for each run
- `config_log/` change log and value assumptions
- `reports/VALUE_BASELINE.md`
- `PLAYBOOK.md`, `RAID.md`
- `tools/` all scripts
