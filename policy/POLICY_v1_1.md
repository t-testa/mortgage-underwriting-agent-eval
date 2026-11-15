# Synthetic Lender Underwriting Policy, v1.1 (v1.0 plus arbitration rules)

This is an invented policy for a fictional lender. It is deliberately written the way real policy documents
often read: clear in some places, vague in others. The vague parts are what the calibration exercise surfaces.

Decision values for every condition: `satisfied`, `not_satisfied`, `needs_review`.

## Income proof (INC)
- INC-01 Income documents must be current.
- INC-02 A Notice of Assessment (NOA) or T4 for the most recent tax year is required for salaried applicants.
- INC-03 Documented income must reasonably support the stated income. Material shortfalls require escalation.
- INC-05 Variable income (commission, bonus, overtime) is to be averaged over a sufficient history.
- INC-06 Documents must be legible.

## Down payment source (DP)
- DP-01 Down payment funds should be seasoned (account history shown).
- DP-02 Funds must cover the down payment and closing costs.
- DP-03 Large or unusual deposits must be explained.
- DP-04 Gifts are acceptable from close family with a gift letter confirming that no repayment is required.

## Appraisal (APP)
- APP-01 The appraisal must be recent.
- APP-02 The appraised value must support the purchase price.
- APP-05 Appraisal conditions must be cleared.
- APP-06 The appraiser must be on the approved panel: Valeur Reference Inc.; Summit Property Valuations;
  Lakeshore Appraisal Group; Cardinal Evaluation Services; Rive-Nord Evaluations; Ironbridge Valuation Ltd.;
  Prairie Oak Appraisals; Meridian Real Estate Appraisers.

## Employment (EMP)
- EMP-01 Employment letters must be recent.
- EMP-02 The letter must be on company letterhead and signed by an authorized representative.
- EMP-03 Permanent full-time employment with a letter meeting the above is acceptable.
- EMP-04 Applicants still on probation are not eligible unless approved by exception.
- EMP-05 Contract income requires a stable history.
- EMP-06 The letter must be consistent with the application.
- EMP-07 An employment letter is required.

## Debt ratio (DTI)
- DTI-01 Maximum GDS 39% and maximum TDS 44%. Liabilities are to be assessed using standard methodology.
- DTI-02 Minimum credit score 600.
- DTI-03 Exceptions for ratios marginally above the limits may be considered for applicants with strong credit.

## General
- A condition is `satisfied` only if the documents on file clearly meet policy.
- If a required document is missing, the condition is not satisfied.
- When in doubt, escalate with `needs_review`.

# Arbitration rules (these override any vague wording above)

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

