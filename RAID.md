# RAID log (risks, assumptions, issues, dependencies)

Format mirrors what I would co-own with a Project Manager on a real implementation. Entries describe this
portfolio exercise; the "Client equivalent" column says what the same line would be on a real client engagement.
Status as of the final commit of this repo.

## Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Client equivalent |
|---|---|---|---|---|---|---|
| R1 | Policy wording is vague, so humans and agent apply different thresholds | High | High | Calibration exercise, arbitration rules, policy v1.1 | Delivery manager | Same, plus policy owner sign-off |
| R2 | Agent approves a condition that should fail (false approval) | Medium | High | Report false approvals separately; keep human review on any non-trivial family until the rate is near zero | Delivery manager + UW Expert | Hard gate before leaving shadow mode |
| R3 | Tuning on the same 50 files overstates real-world accuracy (overfitting) | High | Medium | Disclosed in README; golden set never changed; next step is a fresh holdout set | Delivery manager | Reserve a holdout slice before labeling starts |
| R4 | Golden set encodes one reading of the policy, not the lender's real appetite | Medium | High | UW Expert signs off the 7 threshold rules (AR-01, 02, 06, 07, 08, 11, 14) | UW Expert | Named expert approval with dates |
| R5 | Real documents are messier than synthetic ones | High | Medium | Start production labeling on real files early; track new document patterns in the playbook | Delivery manager | Live client data dependency (D1) |
| R6 | Value numbers rest on assumptions, not measurements | High | Medium | Labelled illustrative; sensitivity via one JSON file | Delivery manager | Replace with signed baseline from process blueprint |
| R7 | Cost of assumed minutes drives the business case more than agent accuracy does | Medium | Medium | Show touches and accuracy separately from hours | Delivery manager | Same |

## Assumptions

| ID | Assumption | If wrong |
|---|---|---|
| A1 | All data is synthetic; no real borrower, employer or lender data is used | Stop and remove the data |
| A2 | The two underwriting teams are scripted simulations with fixed house styles | Kappa values would differ with real people; method unchanged |
| A3 | The golden set follows policy plus the arbitration rules; the generator computes it from the same data that renders the documents | Golden errors would show up as "agent errors"; mitigated by regeneration checks |
| A4 | Fresh Claude Code subagents on the same model stand in for a production agent | API-based agent could differ; `tools/run_agent_api.py` lets someone repeat the run |
| A5 | Manual minutes per condition, rework rate and queue wait in `value_assumptions.json` | Business case numbers change; accuracy numbers do not |
| A6 | One condition is one unit of work for the value baseline | Different units change counts, not the method |

## Issues

| ID | Issue | Status | Resolution |
|---|---|---|---|
| I1 | Baseline policy text left 55 of 65 divergences as policy ambiguity rather than model error | Closed | Arbitration rules written and added to the agent config (see `config_log/CONFIG_LOG.md`) |
| I2 | Reason tags are assigned by script from golden metadata, which is coarse (an ambiguity-tagged condition may still contain a real agent mistake) | Open | A human reviewer would confirm tags in production; noted in limitations |
| I3 | Single tuning round bundles several changes, so the effect of each cannot be separated | Open | Documented; the playbook recommends one change per round on real work |

## Dependencies

| ID | Dependency | Needed by | Status | Real-world note |
|---|---|---|---|---|
| D1 | Live client data (real documents) | Production labeling | Not applicable here | Bi-weekly platform-program dependency sync |
| D2 | Environments for the agent (test and production) | Shadow mode | Simulated with local workspace | Confirm access before calibration week |
| D3 | UW Expert availability for threshold decisions | Arbitration | Simulated | Agree an SLA (see PLAYBOOK) |
| D4 | Release schedule for config changes | Tuning round | Simulated | Config changes ship on the platform release train |
| D5 | Client policy owner | Policy v1.1 sign-off | Simulated | Named person, not a team alias |
