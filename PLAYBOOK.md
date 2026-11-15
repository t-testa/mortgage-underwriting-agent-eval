# Playbook: onboarding the next condition family

How to repeat this implementation for a new family (for example "property tax", "credit exceptions" or "self-employed
income"). Each step names its output so you know when it is done. Times are what this exercise suggests for one
family of around 40 conditions; treat them as starting points.

## 0. Scope the family (half a day)
- Write down the condition in plain words, the documents that decide it, and who decides it today.
- Map the current process: who touches the condition, how many times, how long it waits, how often it comes back (rework).
  This becomes the signed process blueprint and the value baseline.
- Output: one-page process map, baseline numbers with their source, list of rules (even if vague).

## 1. Build the reference set (1 to 2 days)
- Collect around 50 real or realistic files for the family, including bad ones (stale, illegible, missing, conflicting).
- Aim for a mix: roughly half clear passes, a third clear fails, the rest genuine judgment calls.
- Output: the file set and a labeling guide.

## 2. Calibration (2 days)
- Two underwriter pods label the same 50 files independently.
- Compute Cohen's kappa per family (`tools/calibrate.py` shows how) and list every disagreement.
- Group disagreements into patterns. A pattern that repeats is a missing rule.
- Target: kappa of 0.80 or better before production labeling. Below that, more rules, not more labeling.
- Output: disagreement list, kappa table.

## 3. Adjudicate (SLA: 2 business days per batch)
- Triage each pattern: wording or arithmetic questions are closed by the delivery manager; threshold questions
  (a number that changes risk appetite) go to the UW Expert. In this repo 7 of 16 rules needed the expert.
- Write each decision as a rule with an ID, the question, the answer and the evidence. Publish to both pods.
- Re-label the disagreements under the new rules; confirm kappa moves up.
- Output: arbitration rules, policy v1.1, signed-off decision log.

## 4. Freeze the golden set
- The golden set is the answer key. Once frozen it is never edited to make the agent look better. If a label is wrong,
  log it as an issue, fix it through adjudication with a date and a reason, and rerun every earlier result.
- Output: golden set with a rule ID and rationale per condition.

## 5. Shadow mode
- The agent decides every condition from the documents; humans keep working as today. Nothing the agent says is acted on.
- Compare to the golden set. Every divergence goes to a review queue with a reason tag:
  policy ambiguity, missing document, or agent error. Rank by severity; false approvals come first.
- Output: divergence queue, accuracy by family, false-approval count.

## 6. Tune (one change at a time on real work)
- Read the queue. If most divergences are policy ambiguity, fix the policy text first (step 3), not the prompt.
  If they are agent errors, change the prompt or config (for example, force explicit arithmetic).
- Log each change in the config log: what, why, expected effect, before/after accuracy.
- Re-run on a holdout set the agent has not seen, not only on the files used to diagnose problems.
- Output: config log entry, new run results.

## 7. Value baseline and go/no-go
- Report automation rate, safe automation rate, divergence by family, touches, cycle time and rework, against the
  signed baseline from step 0.
- Go-live criteria are agreed in advance, for example: zero false approvals on the holdout, safe automation rate above
  an agreed floor, review queue within team capacity.
- Output: value baseline report and a decision (stay in shadow, go live for part of the volume, or stop).

## 8. Run the program
- Keep the RAID and decision logs current with the Project Manager. Hold the bi-weekly dependency sync (live data,
  environments, release schedule). Escalate a dependency risk the moment it slips, not at the next report.
- During production labeling, manage pod throughput and queue ageing; close ambiguous labels within SLA so only true
  policy calls reach the UW Expert.

## Lessons from this exercise (patterns to reuse)
1. Most early divergence was vague policy, not model weakness. Fix the wording before touching the agent.
2. Threshold rules are where pods disagree. List every number in the policy up front and ask who owns it.
3. "Missing or unreadable" needs an explicit rule. Otherwise pods split between reject and escalate.
4. Report false approvals separately from accuracy. A high accuracy figure can hide the one error that matters.
5. Arithmetic should be explicit in the agent's output (annualized pay, shortfall %, ratios) so a reviewer can check it quickly.
