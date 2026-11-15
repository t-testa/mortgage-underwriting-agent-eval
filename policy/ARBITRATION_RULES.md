# Arbitration rules (adjudication decisions after calibration)

Source: disagreements between Team A and Team B in `calibration/kappa_report.md`, plus places where policy v1.0
is silent or vague. Each rule closes a question once, in writing, so that the golden set, the human teams and the
agent all apply the same line. In a real engagement each rule would carry the name of the UW Expert who approved
it and the date; here the approver is "UW Expert (simulated)".

How rules were triaged: a disagreement that follows a repeated pattern is closed by a rule written by the delivery
manager and signed off in a batch. Only genuine policy calls (a threshold that changes risk appetite) go to the UW
Expert. In this exercise the calls that needed an expert are marked **[UW Expert]**.

| ID | Policy rule | Question closed | Rule | Evidence from calibration |
|---|---|---|---|---|
| AR-01 | INC-03 | How big a shortfall between stated and documented income is acceptable? | Shortfall = (stated minus documented) / stated. Up to 5%: satisfied. Over 5% up to 15%: needs_review. Over 15%: not_satisfied. If documented is higher than stated, no shortfall. **[UW Expert]** | Team A accepted mid shortfalls, Team B escalated even small ones |
| AR-02 | INC-05 | What is "sufficient history" for variable income? | Documented variable income = average of line 15000 over the last two NOAs. Two NOAs needed. Only one year: needs_review. Then apply AR-01. **[UW Expert]** | Team B escalated complete two-year files, Team A accepted one-year files |
| AR-03 | INC-06 | What if a key figure is unreadable? | If gross pay, YTD, or any figure needed for a decision cannot be read with confidence: not_satisfied, and request a clearer copy. Do not escalate illegible files. | Team A escalated, Team B rejected |
| AR-04 | INC-01, EMP-01, APP-01 | How recent is "recent"? | Paystub and employment letter: 30 days or fewer before the review date. Appraisal: 90 days or fewer. No grace period. | Team B gave informal grace on 32 to 40 day-old documents |
| AR-05 | DP-01, DP-02 | What is "seasoned" and what are "closing costs"? | History must span at least 90 days. Required funds = down payment + 1.5% of purchase price. Closing balance below required funds: not_satisfied. | Disagreement on files whose balance covered the down payment but not closing costs |
| AR-06 | DP-03 | What is a "large" deposit? | Non-payroll deposit over 2,500 needs an explanation document (gift letter, bill of sale, etc.). Unexplained 2,500 to 5,000: needs_review. Unexplained over 5,000: not_satisfied. Small deposits up to 2,500 need no explanation. **[UW Expert]** | Team A accepted unexplained mid-size deposits |
| AR-07 | DP-04 | Who counts as "close family" and what must a gift letter say? | Immediate family: parent, grandparent, sibling, spouse, child. Letter must state donor, relationship, amount, a statement that the gift is not repayable, and be signed. Missing non-repayable statement or signature: not_satisfied. Donor not immediate family (aunt, uncle, cousin, friend): needs_review. **[UW Expert]** | Team A accepted far relations, Team B rejected them |
| AR-08 | APP-02 | How far can the appraisal fall short of price? | Shortfall = (price minus value) / price. Up to 2%: satisfied. Over 2% up to 5%: needs_review. Over 5%: not_satisfied. Value at or above price: satisfied. **[UW Expert]** | Team A accepted mid shortfalls, Team B rejected or escalated small ones |
| AR-09 | APP-05 | When is an appraisal condition outstanding? | "Subject to" completion or repair of something: not_satisfied. A recommendation for further inspection with value reported as-is: needs_review. Cosmetic comments with no value impact: ignore. | Split on inspection recommendations |
| AR-10 | EMP-04 | What happens when the applicant is on probation? | Probation end date after the review date: needs_review. Compute the end date from the start date and probation length if not stated. | Team A accepted, Team B rejected |
| AR-11 | EMP-05 | What is a "stable" contract history? | Continuous contract history of 24 months or more: satisfied. 12 up to 24 months: needs_review. Under 12 months: not_satisfied. **[UW Expert]** | Three-way splits on mid-length contracts |
| AR-12 | EMP-06 | What does "consistent with the application" mean? | If the letter salary is more than 5% below stated income: needs_review. Otherwise consistent. | Team A escalated, Team B rejected |
| AR-13 | DTI-01 | How are liabilities assessed? | Housing = mortgage P&I + property tax + heating + 50% of condo fees. GDS = housing / gross monthly income. TDS = (housing + other debts) / gross monthly income. Other debts: credit cards and lines of credit at 3% of balance; instalment loans (auto, student) at the stated monthly payment. The credit bureau report prevails over the application: include debts on the bureau that the applicant did not declare, and exclude closed or zero-balance accounts. | Calculation questions raised in review of borderline files |
| AR-14 | DTI-03 | What is "marginally above" and "strong credit"? | If GDS or TDS exceeds its limit by 2 percentage points or less AND the credit score is 720 or higher: needs_review. Any other breach: not_satisfied. **[UW Expert]** | Team A escalated, Team B rejected |
| AR-15 | General | Which outcome wins when several rules apply? | not_satisfied beats needs_review beats satisfied. A missing required document is not_satisfied, never needs_review. | General principle |
| AR-16 | EMP-02 | Letter without signature or letterhead? | not_satisfied. | General principle |

## Triage note for the playbook
Of 16 rules, 7 are marked **[UW Expert]** because they set a risk threshold (a number that moves risk appetite).
The other 9 clarify wording or arithmetic and can be closed by the delivery manager and confirmed in a batch.
Keeping the expert queue to threshold decisions is what makes the SLA achievable.
