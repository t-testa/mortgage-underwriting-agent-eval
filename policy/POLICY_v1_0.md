# Synthetic Lender Underwriting Policy, v1.0 (as written by the client)

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
