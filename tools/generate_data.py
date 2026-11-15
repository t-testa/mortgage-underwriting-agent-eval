#!/usr/bin/env python3
"""Generate 50 synthetic mortgage files and the golden set.

Everything here is invented. Names, employers, appraisers and numbers are fake.
Python standard library only. Deterministic: same seed, same output.

How the golden set stays honest: each document is RENDERED from a small
structured record, and the golden decision is COMPUTED from that same record by
a rule function (decide_*). The rule functions encode the policy as clarified by
the arbitration rules (policy/ARBITRATION_RULES.md). If a generated record does
not produce the decision its scenario intended, it is regenerated.
"""
import csv
import datetime as dt
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N_FILES = 50
SEED = 20260115

S, N, R = "satisfied", "not_satisfied", "needs_review"
FAMILIES = ["income_proof", "down_payment_source", "appraisal", "employment", "debt_ratio"]

# ---------------------------------------------------------------- vocabulary
FIRST_EN = ["Daniel", "Priya", "Marcus", "Hannah", "Omar", "Elena", "Jordan", "Aisha", "Tyler", "Mei",
            "Callum", "Nadia", "Victor", "Sana", "Ethan", "Leila", "Raj", "Chloe", "Andre", "Maya"]
FIRST_FR = ["Mathieu", "Camille", "Etienne", "Sophie", "Julien", "Genevieve", "Olivier", "Marie-Eve",
            "Simon", "Isabelle", "Philippe", "Catherine"]
LAST = ["Larkin", "Okafor", "Brannigan", "Desrosiers", "Whitlock", "Tremblay-Roy", "Marchetti", "Haddad",
        "Pelletier", "Kowalczyk", "Nguyen", "Gagnon", "Ferreira", "Stanfield", "Bouchard", "Iyer",
        "Castellan", "Dubreuil", "Mackenzie", "Verreault"]
EMPLOYERS = [("Northgate Logistics Inc.", "Northgate"), ("Maplebrook Health Services", "Maplebrook"),
             ("Aurelia Software Ltd.", "Aurelia"), ("Cedar Ridge Municipal Services", "Cedar Ridge"),
             ("Blue Heron Manufacturing", "Blue Heron"), ("Lumen Retail Group", "Lumen"),
             ("Kestrel Engineering Partners", "Kestrel"), ("Fairwater Education Board", "Fairwater"),
             ("Brightfield Insurance Corp.", "Brightfield"), ("Tamarack Food Distributors", "Tamarack")]
STREETS = ["Birchwood Crescent", "Rue des Peupliers", "Alder Lane", "Boulevard Fontaine", "Harbour View Road",
           "Rue Saint-Exemple", "Quarry Street", "Chemin des Cedres"]
CITIES = [("Sherbrooke", "QC"), ("Gatineau", "QC"), ("Ottawa", "ON"), ("Laval", "QC"), ("Kingston", "ON"),
          ("Trois-Rivieres", "QC"), ("Hamilton", "ON"), ("Longueuil", "QC")]
APPROVED_APPRAISERS = ["Valeur Reference Inc.", "Summit Property Valuations", "Lakeshore Appraisal Group",
                       "Cardinal Evaluation Services", "Rive-Nord Evaluations", "Ironbridge Valuation Ltd.",
                       "Prairie Oak Appraisals", "Meridian Real Estate Appraisers"]
UNAPPROVED_APPRAISERS = ["QuickValue Express", "HomeWorth Online Appraisals", "Bargain Appraisal Co.",
                         "Evalu-Rapide Plus"]
APPRAISER_NAMES = ["R. Castonguay, AACI", "L. Whitfield, CRA", "M. Abdallah, AACI", "P. Girouard, CRA",
                   "S. Thornbury, AACI", "D. Lefebvre, CRA"]
CREDITORS_CARD = ["Maple Visa Gold", "Northern MasterCard", "Retail Plus Card", "Travel Rewards Visa"]
CREDITORS_LOC = ["Personal Line of Credit", "Home Equity Line", "Student Line of Credit"]
CREDITORS_CAR = ["AutoFinance Canada", "Ridgeline Auto Credit", "Vehicle Loan"]
CREDITORS_STU = ["Government Student Loan", "Student Loan (Provincial)"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
             "October", "November", "December"]
MONTHS_FR = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre",
             "octobre", "novembre", "decembre"]
IMMEDIATE_EN = ["Mother", "Father", "Grandmother", "Grandfather", "Sister", "Brother"]
IMMEDIATE_FR = ["Mere", "Pere", "Grand-mere", "Grand-pere", "Soeur", "Frere"]
FAR_EN = ["Aunt", "Uncle", "Cousin", "Family friend", "Friend"]
FAR_FR = ["Tante", "Oncle", "Cousin", "Ami de la famille", "Ami"]
IMMEDIATE_SET = set(IMMEDIATE_EN + IMMEDIATE_FR)

# ---------------------------------------------------------------- scenarios
# (tag, expected decision, weight, ambiguity refs in policy v1.0 wording)
SCENARIOS = {
    "income_proof": [
        ("clean", S, 16, ""), ("stale_edge", N, 2, "AR-04"), ("stale_far", N, 2, "AR-04"),
        ("shortfall_small", S, 3, "AR-01"), ("shortfall_mid", R, 4, "AR-01"),
        ("shortfall_large", N, 3, "AR-01"), ("missing_noa", N, 3, ""),
        ("variable_two_year", S, 4, "AR-02"), ("variable_one_year", R, 4, "AR-02"),
        ("illegible", N, 3, "AR-03")],
    "down_payment_source": [
        ("clean_savings", S, 13, ""), ("asset_sale_ok", S, 3, ""), ("gift_ok", S, 5, ""),
        ("unexplained_big", N, 4, "AR-06"), ("unexplained_mid", R, 4, "AR-06"),
        ("gift_no_nonrepay", N, 3, ""), ("gift_far_relation", R, 4, "AR-07"),
        ("insufficient_clear", N, 2, ""), ("insufficient_closing_gap", N, 3, "AR-05"),
        ("short_history", N, 3, "AR-05")],
    "appraisal": [
        ("clean", S, 16, ""), ("above_value", S, 5, ""), ("shortfall_small", S, 3, "AR-08"),
        ("shortfall_mid", R, 4, "AR-08"), ("shortfall_large", N, 3, "AR-08"),
        ("stale", N, 3, "AR-04"), ("subject_to", N, 3, ""), ("unapproved", N, 3, ""),
        ("recommend_inspection", R, 4, "AR-09")],
    "employment": [
        ("clean_permanent", S, 17, ""), ("stale_edge", N, 2, "AR-04"), ("stale_far", N, 2, "AR-04"),
        ("unsigned_or_no_letterhead", N, 3, ""), ("probation", R, 4, "AR-10"),
        ("contract_long", S, 3, "AR-11"), ("contract_mid", R, 4, "AR-11"),
        ("contract_short", N, 3, "AR-11"), ("salary_mismatch", R, 3, "AR-12"), ("no_letter", N, 3, "")],
    "debt_ratio": [
        ("clean", S, 16, ""), ("borderline_pass", S, 4, "AR-13"), ("fail_tds", N, 4, ""),
        ("exception_band", R, 5, "AR-14"), ("undisclosed_fail", N, 3, "AR-13"),
        ("undisclosed_pass", S, 2, "AR-13"), ("low_score", N, 3, ""), ("gds_fail", N, 2, ""),
        ("closed_listed", S, 2, "AR-13"), ("band_low_score", N, 3, "AR-14")],
}
EXPECTED = {f: {t: e for t, e, _, _ in L} for f, L in SCENARIOS.items()}
AMBIG = {f: {t: a for t, _, _, a in L} for f, L in SCENARIOS.items()}
MISSING_DOC_SCENARIOS = {("income_proof", "missing_noa"), ("income_proof", "illegible"),
                         ("employment", "no_letter")}

CONDITION_TEXT = {
    "income_proof": ("Provide proof of income supporting the stated annual income of {inc}.",
                     "Fournir une preuve de revenu appuyant le revenu annuel declare de {inc}."),
    "down_payment_source": ("Confirm the source and availability of the down payment and closing costs.",
                            "Confirmer la provenance et la disponibilite de la mise de fonds et des frais de cloture."),
    "appraisal": ("Provide an acceptable appraisal supporting the purchase price.",
                  "Fournir une evaluation acceptable appuyant le prix d'achat."),
    "employment": ("Confirm current employment.", "Confirmer l'emploi actuel."),
    "debt_ratio": ("Confirm that GDS and TDS are within policy.",
                   "Confirmer que les ratios ABD et ATD respectent la politique."),
}


# ---------------------------------------------------------------- formatting
def money(x, lang, cents=True):
    s = f"{x:,.2f}" if cents else f"{x:,.0f}"
    if lang == "fr":
        return s.replace(",", " ").replace(".", ",") + " $"
    return "$" + s


def dstr(d, style, lang):
    if style == "iso":
        return d.isoformat()
    if style == "slash":
        return d.strftime("%Y/%m/%d")
    if style == "dmy" and d.day > 12:
        return d.strftime("%d/%m/%Y")
    if style == "mon":
        return d.strftime("%d-") + MONTHS_EN[d.month - 1][:3] + d.strftime("-%Y")
    if lang == "fr":
        return f"{d.day} {MONTHS_FR[d.month - 1]} {d.year}"
    return f"{MONTHS_EN[d.month - 1]} {d.day}, {d.year}"


def pick_style(rng):
    return rng.choice(["iso", "long", "long", "mon", "slash", "dmy"])


SUBS = [("l", "1"), ("o", "0"), ("e", "c"), ("i", "l"), ("a", "o"), ("rn", "m")]


def ocr_noise(text, rng, rate):
    """Scanner noise on lines without digits, so key figures are never touched."""
    out = []
    for line in text.split("\n"):
        if any(ch.isdigit() for ch in line) or not line.strip():
            out.append(line)
            continue
        chars = list(line)
        for i, ch in enumerate(chars):
            if ch.isalpha() and rng.random() < rate:
                for a, b in SUBS:
                    if ch == a:
                        chars[i] = b
                        break
        out.append("".join(chars))
    return "\n".join(out)


def garble_digits(s, rng):
    return "".join(rng.choice("#?") if ch.isdigit() and rng.random() < 0.5 else ch for ch in s)


def fname(rng):
    return rng.choice(["scan_{:04d}.pdf", "IMG_{:04d}.pdf", "upload_{:04d}.pdf", "Doc_{:04d}.pdf",
                       "final_v2_{:04d}.pdf"]).format(rng.randint(1, 9999))


# ---------------------------------------------------------------- file context
def make_ctx(rng, i):
    lang = "fr" if rng.random() < 0.26 else "en"
    first = FIRST_FR if lang == "fr" else FIRST_EN
    city, prov = rng.choice(CITIES)
    emp = rng.choice(EMPLOYERS)
    price = rng.randrange(340000, 880000, 5000)
    pct = rng.choice([0.05, 0.08, 0.10, 0.10, 0.15, 0.20, 0.25])
    ctx = dict(
        id=f"MF-{i:03d}", lang=lang,
        review=dt.date(2026, 6, 1) + dt.timedelta(days=rng.randint(0, 150)),
        price=price, down=round(price * pct, -2), income=float(rng.randrange(62000, 172000, 500)),
        prop_type=rng.choice(["house", "house", "condo"]),
        address=f"{rng.randint(12, 998)} {rng.choice(STREETS)}, {city}, {prov}",
        borrower=f"{rng.choice(first)} {rng.choice(LAST)}",
        employer=emp[0], employer_short=emp[1], city=city,
    )
    ctx["closing_costs"] = round(price * 0.015, 2)
    ctx["required_funds"] = ctx["down"] + ctx["closing_costs"]
    return ctx


def T(ctx, en, fr):
    return fr if ctx["lang"] == "fr" else en


# ---------------------------------------------------------------- INCOME
FREQ = {26: ("Bi-weekly", "Aux deux semaines"), 24: ("Semi-monthly", "Bimensuelle"), 12: ("Monthly", "Mensuelle")}


def doc_paystub(rng, ctx, per_period, freq, age, base=None, commission=None, garble=False):
    lang = ctx["lang"]
    ds = pick_style(rng)
    end = ctx["review"] - dt.timedelta(days=age)
    start = end - dt.timedelta(days=365 // freq - 1)
    pay = end + dt.timedelta(days=rng.randint(1, 4))
    periods = max(1, int((end - dt.date(end.year, 1, 1)).days / 365 * freq) + 1)
    ytd = per_period * periods
    net = round(per_period * rng.uniform(0.70, 0.77), 2)
    first, last = ctx["borrower"].split(" ", 1)[0], ctx["borrower"].split(" ", 1)[1]
    m = lambda v: money(v, lang)
    gross_s, ytd_s = m(per_period), m(ytd)
    if garble:
        gross_s, ytd_s = garble_digits(gross_s, rng), garble_digits(ytd_s, rng)
    lines = [
        ctx["employer"].upper(),
        T(ctx, "EARNINGS STATEMENT", "RELEVE DE PAIE"),
        f"{T(ctx, 'Employee', 'Employe')}: {last.upper()}, {first}   ID: {rng.randint(10000, 99999)}",
        f"{T(ctx, 'Pay frequency', 'Frequence')}: {FREQ[freq][1 if lang == 'fr' else 0]}",
        f"{T(ctx, 'Pay period', 'Periode')}: {dstr(start, ds, lang)} - {dstr(end, ds, lang)}",
        f"{T(ctx, 'Pay date', 'Date de paie')}: {dstr(pay, ds, lang)}",
    ]
    if base is not None:
        lines += [f"{T(ctx, 'Base salary', 'Salaire de base')}        {m(base)}",
                  f"{T(ctx, 'Commission', 'Commission')}              {m(commission)}"]
    else:
        lines += [f"{T(ctx, 'Regular earnings', 'Gains reguliers')}   {gross_s}"]
    lines += [
        f"{T(ctx, 'GROSS THIS PERIOD', 'BRUT PERIODE')}      {gross_s}",
        f"{T(ctx, 'Deductions (tax, CPP/QPP, EI, pension)', 'Retenues (impot, RPC/RRQ, AE, retraite)')}  {m(per_period - net)}",
        f"{T(ctx, 'NET PAY', 'PAIE NETTE')}               {m(net)}",
        f"{T(ctx, 'GROSS YEAR TO DATE', 'BRUT CUMULATIF')}   {ytd_s}",
    ]
    if garble:
        lines.append("[fax quality degraded - partial transmission]")
    return "\n".join(lines)


def doc_noa(rng, ctx, year, line15000):
    lang = ctx["lang"]
    ds = pick_style(rng)
    issued = dt.date(year + 1, rng.randint(3, 5), rng.randint(1, 27))
    net = line15000 * rng.uniform(0.93, 0.99)
    return "\n".join([
        T(ctx, "Canada Revenue Agency / Agence du revenu du Canada", "Agence du revenu du Canada / Canada Revenue Agency"),
        T(ctx, "NOTICE OF ASSESSMENT", "AVIS DE COTISATION"),
        f"{T(ctx, 'Tax year', 'Annee d imposition')}: {year}      {T(ctx, 'Date issued', 'Date d emission')}: {dstr(issued, ds, lang)}",
        f"SIN/NAS: XXX XXX {rng.randint(100, 999)}",
        f"Line 15000 {T(ctx, 'Total income', 'Revenu total')}:   {money(line15000, lang)}",
        f"Line 23600 {T(ctx, 'Net income', 'Revenu net')}:     {money(net, lang)}",
        f"{T(ctx, 'Balance', 'Solde')}: {money(rng.uniform(-2400, 900), lang)}",
    ])


def build_income(rng, ctx, sc):
    S_inc = ctx["income"]
    freq = rng.choice([26, 26, 24, 12])
    age = rng.randint(3, 26)
    if sc == "stale_edge":
        age = rng.randint(32, 40)
    if sc == "stale_far":
        age = rng.randint(45, 75)
    sf = {"clean": rng.uniform(-0.04, 0.012), "stale_edge": rng.uniform(-0.03, 0.01),
          "stale_far": rng.uniform(-0.03, 0.01), "shortfall_small": rng.uniform(0.025, 0.045),
          "shortfall_mid": rng.uniform(0.07, 0.13), "shortfall_large": rng.uniform(0.18, 0.30),
          "missing_noa": rng.uniform(-0.03, 0.01), "illegible": rng.uniform(-0.03, 0.01)}.get(sc, 0.0)
    docs = []
    variable = sc.startswith("variable")
    noa_years, noa_vals = [], []
    legible = sc != "illegible"
    if variable:
        base_annual = round(S_inc * rng.uniform(0.6, 0.75), -2)
        comm_annual = S_inc - base_annual
        per_p = round(S_inc / freq, 2)
        base_p, comm_p = round(base_annual / freq, 2), round(comm_annual / freq, 2)
        docs.append(doc_paystub(rng, ctx, round(base_p + comm_p, 2), freq, age, base=base_p, commission=comm_p))
        y25 = S_inc * rng.uniform(0.985, 1.03)
        y24 = S_inc * rng.uniform(0.96, 1.02)
        noa_years, noa_vals = [2025], [y25]
        docs.append(doc_noa(rng, ctx, 2025, y25))
        if sc == "variable_two_year":
            noa_years.append(2024)
            noa_vals.append(y24)
            docs.append(doc_noa(rng, ctx, 2024, y24))
        annual_doc = None
    else:
        annual_doc = round(S_inc * (1 - sf), 2)
        per_p = round(annual_doc / freq, 2)
        annual_doc = round(per_p * freq, 2)
        docs.append(doc_paystub(rng, ctx, per_p, freq, age, garble=not legible))
        if sc != "missing_noa":
            noa_years = [2025]
            noa_vals = [annual_doc * rng.uniform(0.96, 1.03)]
            docs.append(doc_noa(rng, ctx, 2025, noa_vals[0]))
    d = dict(stated=S_inc, age=age, legible=legible, variable=variable, noa_years=noa_years,
             noa_vals=noa_vals, annual_doc=annual_doc)
    return docs, decide_income(d, ctx)


def decide_income(d, ctx):
    stated = d["stated"]
    if not d["legible"]:
        return N, "INC-06", "Key figures on the paystub are illegible; a clearer copy is required (AR-03).", True
    if d["age"] > 30:
        return N, "INC-01", f"Paystub is {d['age']} days old; maximum is 30 days with no grace period (AR-04).", False
    if not d["noa_years"]:
        return N, "INC-02", "No Notice of Assessment or T4 for the last tax year was provided.", True
    if d["variable"]:
        if len(d["noa_years"]) < 2:
            return R, "INC-05", "Variable income with only one year of NOA history; two years needed (AR-02).", False
        doc = sum(d["noa_vals"]) / len(d["noa_vals"])
        rule = "INC-05"
    else:
        doc, rule = d["annual_doc"], "INC-03"
    sf = (stated - doc) / stated
    msg = f"Documented income {doc:,.0f} vs stated {stated:,.0f}; shortfall {sf * 100:.1f}% (AR-01)."
    if sf <= 0.05:
        return S, rule, msg, False
    if sf <= 0.15:
        return R, rule, msg, False
    return N, rule, msg, False


# ---------------------------------------------------------------- DOWN PAYMENT
def doc_bank(rng, ctx, hist_days, closing, extras):
    lang = ctx["lang"]
    ds = pick_style(rng)
    end = ctx["review"] - dt.timedelta(days=rng.randint(2, 12))
    start = end - dt.timedelta(days=hist_days - 1)
    net = round(ctx["income"] / 26 * 0.74, 2)
    tx = []
    d = start + dt.timedelta(days=rng.randint(0, 13))
    while d <= end:
        tx.append((d, f"PAYROLL DEP {ctx['employer_short'].upper()}", net))
        d += dt.timedelta(days=14)
    spend = ["GROCERY STORE", "PHARMACY", "FUEL", "RESTAURANT", "TELECOM BILL", "UTILITY PAYMENT",
             "RENT PAYMENT", "ONLINE PURCHASE", "TRANSIT PASS", "INSURANCE PREM"]
    for _ in range(rng.randint(14, 22)):
        day = start + dt.timedelta(days=rng.randint(0, hist_days - 1))
        tx.append((day, rng.choice(spend), -round(rng.uniform(18, 520), 2)))
    for _ in range(rng.randint(1, 3)):
        day = start + dt.timedelta(days=rng.randint(0, hist_days - 1))
        tx.append((day, "E-TRANSFER RECEIVED " + rng.choice(["A. MORIN", "T. LEE", "REFUND"]),
                   round(rng.uniform(60, 900), 2)))
    for off, desc, amt in extras:
        day = start + dt.timedelta(days=min(hist_days - 1, max(0, int(hist_days * off))))
        tx.append((day, desc, amt))
    tx.sort(key=lambda t: t[0])
    total = sum(t[2] for t in tx)
    opening = closing - total
    if opening < 300:
        bump = 300 - opening + rng.uniform(0, 400)
        opening, closing = opening + bump, closing + bump
    opening, closing = round(opening, 2), round(opening + total, 2)
    bal = opening
    lines = [
        T(ctx, "ACCOUNT STATEMENT - CHEQUING", "RELEVE DE COMPTE - CHEQUES"),
        f"{T(ctx, 'Account holder', 'Titulaire')}: {ctx['borrower'].upper()}",
        f"{T(ctx, 'Statement period', 'Periode du releve')}: {dstr(start, ds, lang)} to {dstr(end, ds, lang)}",
        f"{T(ctx, 'Opening balance', 'Solde d ouverture')}: {money(opening, lang)}",
        "",
    ]
    for day, desc, amt in tx:
        bal += amt
        lines.append(f"{dstr(day, ds, lang):<16}{desc:<36}{money(amt, lang):>16}{money(bal, lang):>18}")
    lines += ["", f"{T(ctx, 'Closing balance', 'Solde de cloture')}: {money(closing, lang)}"]
    return "\n".join(lines), closing


def doc_gift(rng, ctx, donor, relation, amount, nonrepay_mode, signed):
    lang = ctx["lang"]
    ds = pick_style(rng)
    gdate = ctx["review"] - dt.timedelta(days=rng.randint(10, 40))
    if lang == "fr":
        body = f"Je soussigne(e), {donor}, {relation.lower()} de {ctx['borrower']}, confirme faire un don de {money(amount, lang)} le {dstr(gdate, ds, lang)} pour l'achat de la propriete situee au {ctx['address']}."
        ok = "Ce don n'a pas a etre rembourse."
        bad = "Ce montant sera rembourse des que possible."
        sig = "Signature: ______________" if not signed else f"Signature: /s/ {donor}"
    else:
        body = f"I, {donor}, {relation.lower()} of {ctx['borrower']}, am giving the sum of {money(amount, lang)} on {dstr(gdate, ds, lang)} towards the purchase of the property at {ctx['address']}."
        ok = "This is a gift and does not have to be repaid."
        bad = "The borrower will repay this amount when able."
        sig = "Signature: ______________" if not signed else f"Signature: /s/ {donor}"
    lines = [T(ctx, "GIFT LETTER", "LETTRE DE DON"), body]
    if nonrepay_mode == "ok":
        lines.append(ok)
    elif nonrepay_mode == "repay":
        lines.append(bad)
    else:
        lines.append(T(ctx, "I am happy to help with their first home.", "Je suis heureux(se) de les aider pour leur premiere maison."))
    lines += [sig, f"{T(ctx, 'Donor phone', 'Tel. du donateur')}: 613-555-01{rng.randint(10, 99)}"]
    return "\n".join(lines)


def doc_bill_of_sale(rng, ctx, amount, buyer):
    lang = ctx["lang"]
    ds = pick_style(rng)
    d = ctx["review"] - dt.timedelta(days=rng.randint(15, 60))
    return "\n".join([
        T(ctx, "BILL OF SALE - USED VEHICLE", "FACTURE DE VENTE - VEHICULE USAGE"),
        f"{T(ctx, 'Seller', 'Vendeur')}: {ctx['borrower']}   {T(ctx, 'Buyer', 'Acheteur')}: {buyer}",
        f"{T(ctx, 'Vehicle', 'Vehicule')}: 2017 compact sedan, VIN ending {rng.randint(1000, 9999)}",
        f"{T(ctx, 'Sale price', 'Prix de vente')}: {money(amount, lang)}   {T(ctx, 'Date', 'Date')}: {dstr(d, ds, lang)}",
        T(ctx, "Paid in full by e-transfer. Sold as is.", "Paye au complet par virement. Vendu tel quel."),
    ])


def build_dp(rng, ctx, sc):
    req = ctx["required_funds"]
    hist = 60 if sc == "short_history" else rng.randint(90, 120)
    margin = rng.uniform(3000, 30000)
    closing = req + margin
    extras, docs_extra = [], []
    explained = True
    gift = None
    if sc == "insufficient_clear":
        closing = ctx["down"] - rng.uniform(2000, 20000)
    if sc == "insufficient_closing_gap":
        closing = ctx["down"] + ctx["closing_costs"] * rng.uniform(0.2, 0.8)
    if sc in ("unexplained_big", "unexplained_mid", "asset_sale_ok"):
        amt = {"unexplained_big": rng.uniform(6000, 32000), "unexplained_mid": rng.uniform(2700, 4800),
               "asset_sale_ok": rng.uniform(5200, 16000)}[sc]
        amt = round(amt, -1)
        if sc == "asset_sale_ok":
            buyer = rng.choice(LAST)
            extras.append((rng.uniform(0.3, 0.8), f"E-TRANSFER RECEIVED {buyer.upper()}", amt))
            docs_extra.append(doc_bill_of_sale(rng, ctx, amt, f"{rng.choice(FIRST_EN)} {buyer}"))
            closing = max(closing, req + amt * 0.3 + 4000)
        else:
            extras.append((rng.uniform(0.3, 0.8), rng.choice(["DEPOSIT", "E-TRANSFER RECEIVED J. ROY", "CASH DEPOSIT BRANCH"]), amt))
            closing = max(closing, req + amt * 0.3 + 4000)
    if sc in ("gift_ok", "gift_no_nonrepay", "gift_far_relation"):
        immediate = EN_IM = (IMMEDIATE_FR if ctx["lang"] == "fr" else IMMEDIATE_EN)
        far = FAR_FR if ctx["lang"] == "fr" else FAR_EN
        relation = rng.choice(far) if sc == "gift_far_relation" else rng.choice(immediate)
        amt = round(min(ctx["down"] * rng.uniform(0.3, 0.6), 60000), -2)
        donor = f"{rng.choice(FIRST_EN)} {ctx['borrower'].split(' ', 1)[1]}"
        mode = "ok"
        signed = True
        if sc == "gift_no_nonrepay":
            mode = rng.choice(["missing", "repay"])
            signed = rng.random() < 0.7
        docs_extra.append(doc_gift(rng, ctx, donor, relation, amt, mode, signed))
        extras.append((rng.uniform(0.4, 0.85), f"E-TRANSFER RECEIVED {donor.upper()}", amt))
        closing = max(closing, req + amt * 0.1 + 4000)
        gift = dict(relation=relation, nonrepay=(mode == "ok"), signed=signed, amount=amt)
    stmt, closing = doc_bank(rng, ctx, hist, closing, extras)
    unexpl = 0
    if sc in ("unexplained_big", "unexplained_mid"):
        unexpl = extras[0][2]
    d = dict(hist=hist, closing=closing, required=req, unexplained=unexpl, gift=gift)
    return [stmt] + docs_extra, decide_dp(d, ctx)


def decide_dp(d, ctx):
    if d["hist"] < 90:
        return N, "DP-01", f"Statement covers {d['hist']} days; 90 days of history required (AR-05).", False
    if d["closing"] < d["required"]:
        return N, "DP-02", (f"Closing balance {d['closing']:,.0f} is below required funds "
                            f"{d['required']:,.0f} (down payment plus 1.5% closing costs) (AR-05)."), False
    u = d["unexplained"]
    if u > 5000:
        return N, "DP-03", f"Unexplained non-payroll deposit of {u:,.0f} exceeds 5,000 (AR-06).", False
    g = d["gift"]
    if g:
        if not g["nonrepay"] or not g["signed"]:
            return N, "DP-04", "Gift letter lacks a non-repayable statement or the donor signature (AR-07).", False
        if g["relation"] not in IMMEDIATE_SET:
            return R, "DP-04", f"Donor relation '{g['relation']}' is not immediate family; escalate (AR-07).", False
    if u > 2500:
        return R, "DP-03", f"Unexplained non-payroll deposit of {u:,.0f} between 2,500 and 5,000 (AR-06).", False
    return S, "DP-02", "Funds seasoned 90+ days, cover down payment and closing costs, deposits explained.", False


# ---------------------------------------------------------------- APPRAISAL
def build_appraisal(rng, ctx, sc):
    lang = ctx["lang"]
    ds = pick_style(rng)
    P = ctx["price"]
    age = rng.randint(5, 80)
    if sc == "stale":
        age = rng.randint(95, 150)
    sf = {"clean": rng.uniform(-0.01, 0.0), "above_value": rng.uniform(-0.06, -0.015),
          "shortfall_small": rng.uniform(0.007, 0.018), "shortfall_mid": rng.uniform(0.027, 0.045),
          "shortfall_large": rng.uniform(0.06, 0.11)}.get(sc, rng.uniform(-0.01, 0.0))
    V = round(P * (1 - sf), -3)
    panel = sc != "unapproved"
    firm = rng.choice(APPROVED_APPRAISERS if panel else UNAPPROVED_APPRAISERS)
    rdate = ctx["review"] - dt.timedelta(days=age)
    comments = [T(ctx, "Minor cosmetic wear noted in kitchen and hallway; no impact on value.",
                  "Usure cosmetique mineure notee a la cuisine et au couloir; aucun impact sur la valeur.")]
    subject_to = recommend = False
    if sc == "subject_to":
        subject_to = True
        comments.append(T(ctx, "Value is subject to completion of the roof replacement; completion certificate to be provided.",
                          "La valeur est sujette a l'achevement du remplacement de la toiture; certificat d'achevement a fournir."))
    if sc == "recommend_inspection":
        recommend = True
        comments.append(T(ctx, "Appraiser recommends a further foundation inspection by a qualified engineer. Value reported as-is.",
                          "L'evaluateur recommande une inspection supplementaire des fondations par un ingenieur. Valeur rapportee telle quelle."))
    comps = []
    for _ in range(3):
        cp = round(V * rng.uniform(0.96, 1.04), -3)
        comps.append(f"  {rng.randint(10, 990)} {rng.choice(STREETS)}   {money(cp, lang, False)}   adj {rng.choice(['+', '-'])}{rng.randint(1, 4)}.{rng.randint(0, 9)}%")
    text = "\n".join([
        firm.upper(),
        T(ctx, "RESIDENTIAL APPRAISAL REPORT - SUMMARY", "RAPPORT D'EVALUATION RESIDENTIELLE - SOMMAIRE"),
        f"{T(ctx, 'Subject', 'Propriete')}: {ctx['address']}   ({ctx['prop_type']})",
        f"{T(ctx, 'Report date', 'Date du rapport')}: {dstr(rdate, ds, lang)}",
        f"{T(ctx, 'Contract purchase price', 'Prix d achat au contrat')}: {money(P, lang, False)}",
        f"{T(ctx, 'OPINION OF MARKET VALUE', 'VALEUR MARCHANDE ESTIMEE')}: {money(V, lang, False)}",
        T(ctx, "Direct comparison approach. Comparables:", "Methode de comparaison directe. Comparables:"),
        *comps,
        T(ctx, "Comments:", "Commentaires:"),
        *["  " + c for c in comments],
        f"{T(ctx, 'Appraiser', 'Evaluateur')}: {rng.choice(APPRAISER_NAMES)}   Lic. {rng.randint(10000, 99999)}",
    ])
    shortfall = (P - V) / P
    d = dict(panel=panel, age=age, subject_to=subject_to, recommend=recommend, shortfall=shortfall, V=V, P=P, firm=firm)
    return [text], decide_appraisal(d, ctx)


def decide_appraisal(d, ctx):
    if not d["panel"]:
        return N, "APP-06", f"{d['firm']} is not on the approved appraiser panel.", False
    if d["age"] > 90:
        return N, "APP-01", f"Appraisal is {d['age']} days old; maximum is 90 days (AR-04).", False
    if d["subject_to"]:
        return N, "APP-05", "Value is subject to completion of repairs; condition is not cleared (AR-09).", False
    sf = d["shortfall"]
    msg = f"Appraised {d['V']:,.0f} vs price {d['P']:,.0f}; shortfall {sf * 100:.1f}% (AR-08)."
    if sf > 0.05:
        return N, "APP-02", msg, False
    if sf > 0.02:
        return R, "APP-02", msg, False
    if d["recommend"]:
        return R, "APP-05", "Appraiser recommends a further inspection; escalate (AR-09).", False
    return S, "APP-02", msg, False


# ---------------------------------------------------------------- EMPLOYMENT
def build_employment(rng, ctx, sc):
    lang = ctx["lang"]
    ds = pick_style(rng)
    review = ctx["review"]
    age = rng.randint(3, 26)
    if sc == "stale_edge":
        age = rng.randint(32, 40)
    if sc == "stale_far":
        age = rng.randint(45, 75)
    ltype, months, prob_end = "permanent", None, None
    hire = review - dt.timedelta(days=rng.randint(250, 4300))
    salary = ctx["income"] * rng.uniform(0.97, 1.06)
    signed, letterhead = True, True
    stmt = ""
    if sc == "probation":
        hire = review - dt.timedelta(days=rng.randint(20, 110))
        prob_end = hire + dt.timedelta(days=182)
        stmt = rng.choice([T(ctx, "is currently within the standard six (6) month probationary period",
                              "est actuellement dans la periode de probation standard de six (6) mois"),
                           T(ctx, "is subject to a probationary period of six (6) months from the start date",
                             "est assujetti(e) a une periode de probation de six (6) mois a compter de la date d'entree")])
    elif sc == "clean_permanent" and rng.random() < 0.5:
        stmt = T(ctx, "has successfully completed the probationary period", "a termine avec succes sa periode de probation")
    if sc.startswith("contract"):
        ltype = "contract"
        months = {"contract_long": rng.randint(26, 60), "contract_mid": rng.randint(13, 23),
                  "contract_short": rng.randint(3, 10)}[sc]
        hire = review - dt.timedelta(days=int(months * 30.44))
    if sc == "salary_mismatch":
        salary = ctx["income"] * rng.uniform(0.78, 0.92)
    if sc == "unsigned_or_no_letterhead":
        if rng.random() < 0.5:
            signed = False
        else:
            letterhead = False
    if sc == "no_letter":
        docs = [T(ctx, "Cover note from borrower: 'My employer says the HR person is on leave, will send letter soon. Paystub already sent.'",
                  "Note de l'emprunteur: 'Mon employeur dit que la personne des RH est en conges, la lettre suivra. Talon de paie deja envoye.'")]
        return docs, decide_emp(dict(letter=False), ctx)
    ldate = review - dt.timedelta(days=age)
    status = (T(ctx, "permanent full-time", "permanent a temps plein") if ltype == "permanent" else
              T(ctx, f"fixed-term contract, continuously renewed with us since {dstr(hire, ds, lang)}",
                f"contrat a duree determinee, renouvele sans interruption depuis le {dstr(hire, ds, lang)}"))
    head = (f"[{T(ctx, 'Letterhead', 'Papier a en-tete')}: {ctx['employer']} | {rng.randint(100, 900)} {rng.choice(STREETS)} | tel 819-555-01{rng.randint(10, 99)}]"
            if letterhead else "(sent from personal mail account, no letterhead)")
    body = [
        head, dstr(ldate, ds, lang), T(ctx, "To whom it may concern,", "A qui de droit,"),
        T(ctx, f"This confirms that {ctx['borrower']} is employed by {ctx['employer']} as {rng.choice(['Senior Analyst', 'Operations Lead', 'Technician', 'Account Manager', 'Coordinator'])}.",
          f"La presente confirme que {ctx['borrower']} est employe(e) de {ctx['employer']} a titre de {rng.choice(['analyste principal', 'chef des operations', 'technicien', 'gestionnaire de comptes', 'coordonnateur'])}."),
        T(ctx, f"Start date: {dstr(hire, ds, lang)}. Employment status: {status}.",
          f"Date d'entree: {dstr(hire, ds, lang)}. Statut: {status}."),
    ]
    if stmt:
        body.append(T(ctx, f"The employee {stmt}.", f"L'employe(e) {stmt}."))
    body.append(T(ctx, f"Current annual base salary: {money(salary, lang)}.", f"Salaire annuel de base actuel: {money(salary, lang)}."))
    body.append(T(ctx, "Sincerely,", "Cordialement,"))
    body.append(("/s/ " if signed else "______________ ") + f"{rng.choice(FIRST_EN)} {rng.choice(LAST)}, {T(ctx, 'HR Manager', 'Gestionnaire RH')}"
                if signed else "Signature: ______________  (HR Manager)")
    d = dict(letter=True, age=age, signed=signed, letterhead=letterhead, ltype=ltype, months=months,
             prob_end=prob_end, review=review, salary=salary, stated=ctx["income"])
    return ["\n".join(body)], decide_emp(d, ctx)


def decide_emp(d, ctx):
    if not d["letter"]:
        return N, "EMP-07", "No employment letter was provided; paystub alone does not confirm employment.", True
    if not d["signed"] or not d["letterhead"]:
        return N, "EMP-02", "Letter is unsigned or not on letterhead (AR-16).", False
    if d["age"] > 30:
        return N, "EMP-01", f"Letter is {d['age']} days old; maximum is 30 days (AR-04).", False
    if d["ltype"] == "contract":
        m = d["months"]
        if m < 12:
            return N, "EMP-05", f"Contract history of about {m} months is below 12 (AR-11).", False
        if m < 24:
            return R, "EMP-05", f"Contract history of about {m} months is between 12 and 24 (AR-11).", False
    if d["prob_end"] and d["prob_end"] > d["review"]:
        return R, "EMP-04", f"Probation runs to {d['prob_end'].isoformat()}, after the review date; escalate (AR-10).", False
    if d["salary"] < d["stated"] * 0.95:
        return R, "EMP-06", f"Letter salary {d['salary']:,.0f} is more than 5% below stated {d['stated']:,.0f} (AR-12).", False
    return S, "EMP-03", "Signed letter on letterhead, current, stable status, salary consistent.", False


# ---------------------------------------------------------------- DEBT RATIO
SPEC = {  # gds range, tds range, score range
    "clean": ((0.27, 0.34), (0.35, 0.41), (700, 820)),
    "borderline_pass": ((0.33, 0.385), (0.425, 0.436), (680, 780)),
    "fail_tds": ((0.33, 0.38), (0.48, 0.55), (690, 780)),
    "exception_band": ((0.33, 0.385), (0.447, 0.457), (725, 790)),
    "band_low_score": ((0.33, 0.385), (0.447, 0.457), (640, 715)),
    "low_score": ((0.27, 0.34), (0.35, 0.41), (540, 595)),
    "gds_fail": ((0.43, 0.50), (0.50, 0.56), (680, 780)),
    "undisclosed_fail": ((0.30, 0.34), (0.37, 0.41), (700, 800)),
    "undisclosed_pass": ((0.28, 0.33), (0.31, 0.35), (700, 800)),
    "closed_listed": ((0.28, 0.34), (0.35, 0.40), (700, 800)),
}


def rev_line(kind, amt, rng, name=None, on_app=True, status="open"):
    if kind == "card":
        bal = round(amt / 0.03, -1)
        return dict(name=name or rng.choice(CREDITORS_CARD), kind=kind, balance=bal, limit=round(bal * rng.uniform(1.4, 3.0), -2) or 500,
                    payment=round(max(10, bal * 0.02), 2), status=status, on_app=on_app)
    if kind == "loc":
        bal = round(amt / 0.03, -2)
        return dict(name=name or rng.choice(CREDITORS_LOC), kind=kind, balance=bal, limit=round(bal * rng.uniform(1.2, 2.5), -3),
                    payment=round(max(25, bal * 0.01), 2), status=status, on_app=on_app)
    pay = round(amt, 0)
    nm = rng.choice(CREDITORS_CAR if kind == "car" else CREDITORS_STU)
    return dict(name=nm, kind=kind, balance=round(pay * rng.randint(24, 60), -2), limit=0, payment=pay, status=status, on_app=on_app)


def split_obligations(rng, total, n_lines):
    kinds = rng.sample(["card", "loc", "car", "student"], n_lines)
    shares = [rng.random() + 0.35 for _ in kinds]
    s = sum(shares)
    return [(k, total * sh / s) for k, sh in zip(kinds, shares)]


def dti_calc(h, lines):
    housing = h["pi"] + h["tax"] + h["heat"] + 0.5 * h["condo"]
    obl = 0.0
    for t in lines:
        if t["status"] != "open" or t["balance"] <= 0:
            continue
        obl += 0.03 * t["balance"] if t["kind"] in ("card", "loc") else t["payment"]
    return housing / h["income_m"], (housing + obl) / h["income_m"]


def build_dti(rng, ctx, sc):
    lang = ctx["lang"]
    g_r, t_r, s_r = SPEC[sc]
    I = round(ctx["income"] / 12, 2)
    g, t = rng.uniform(*g_r), rng.uniform(*t_r)
    t = max(t, g + 0.02)
    housing = g * I
    tax = round(rng.uniform(230, 560), 2)
    heat = round(rng.uniform(85, 190), 2)
    condo = round(rng.uniform(260, 540), 2) if ctx["prop_type"] == "condo" else 0.0
    pi = round(housing - tax - heat - 0.5 * condo, 2)
    h = dict(pi=pi, tax=tax, heat=heat, condo=condo, income_m=I)
    O = (t - g) * I
    lines = []
    if sc in ("undisclosed_fail", "undisclosed_pass"):
        disclosed = [rev_line(k, a, rng) for k, a in split_obligations(rng, O, rng.randint(1, 2))]
        total_t = {"undisclosed_fail": rng.uniform(0.47, 0.52), "undisclosed_pass": rng.uniform(0.37, 0.41)}[sc]
        extra_amt = max(60, (total_t - t) * I)
        hidden = rev_line(rng.choice(["card", "car", "loc"]), extra_amt, rng, on_app=False)
        lines = disclosed + [hidden]
    elif sc == "closed_listed":
        lines = [rev_line(k, a, rng) for k, a in split_obligations(rng, O, rng.randint(1, 2))]
        ghost = rev_line("car", rng.uniform(0.07, 0.10) * I, rng, status="closed")
        ghost["balance"] = 0.0
        lines.append(ghost)
    else:
        lines = [rev_line(k, a, rng) for k, a in split_obligations(rng, O, rng.randint(1, 3))]
    score = rng.randint(*s_r)
    gds, tds = dti_calc(h, lines)
    # --- render
    m = lambda v: money(v, lang)
    ds = pick_style(rng)
    app_lines = []
    for tl in lines:
        if tl["on_app"]:
            app_lines.append(f"  {tl['name']:<28}{m(tl['payment']):>14}")
    ws = "\n".join([
        T(ctx, "MORTGAGE QUALIFICATION WORKSHEET (draft, ratios to be confirmed)", "FICHE DE QUALIFICATION HYPOTHECAIRE (ebauche, ratios a confirmer)"),
        f"{T(ctx, 'Gross monthly income used', 'Revenu mensuel brut utilise')}: {m(I)}",
        f"{T(ctx, 'Property type', 'Type de propriete')}: {ctx['prop_type']}",
        f"{T(ctx, 'Qualifying mortgage payment (P&I, stress-tested)', 'Paiement hypothecaire de qualification (capital et interets)')}: {m(pi)}",
        f"{T(ctx, 'Property tax (monthly)', 'Taxes foncieres (mensuel)')}: {m(tax)}",
        f"{T(ctx, 'Heating (monthly)', 'Chauffage (mensuel)')}: {m(heat)}",
        f"{T(ctx, 'Condo fees (monthly)', 'Frais de copropriete (mensuel)')}: {m(condo) if condo else 'N/A'}",
        f"{T(ctx, 'Liabilities declared by applicant (monthly payment as stated)', 'Dettes declarees par le demandeur (paiement mensuel declare)')}:",
        *(app_lines or ["  " + T(ctx, "none declared", "aucune declaree")]),
    ])
    rows = []
    for tl in lines:
        rows.append(f"{tl['name']:<26}{tl['kind']:<10}{m(tl['limit']) if tl['limit'] else '-':>14}{m(tl['balance']):>16}{m(tl['payment']):>12}  "
                    f"{T(ctx, 'CLOSED - paid in full', 'FERME - paye') if tl['status'] == 'closed' else T(ctx, 'Open', 'Ouvert')}")
    bureau = "\n".join([
        T(ctx, "CREDIT BUREAU REPORT - SUMMARY", "RAPPORT DE CREDIT - SOMMAIRE"),
        f"{T(ctx, 'Subject', 'Sujet')}: {ctx['borrower'].upper()}    {T(ctx, 'Report date', 'Date du rapport')}: {dstr(ctx['review'] - dt.timedelta(days=rng.randint(2, 20)), ds, lang)}",
        f"{T(ctx, 'Credit score', 'Cote de credit')}: {score}",
        f"{T(ctx, 'Creditor', 'Creancier'):<26}{T(ctx, 'Type', 'Type'):<10}{T(ctx, 'Limit', 'Limite'):>14}{T(ctx, 'Balance', 'Solde'):>16}{T(ctx, 'Pmt', 'Pmt'):>12}  {T(ctx, 'Status', 'Statut')}",
        *rows, T(ctx, "Inquiries (12 mo): 2", "Demandes (12 mois): 2"),
    ])
    d = dict(h=h, lines=lines, score=score)
    return [ws, bureau], decide_dti(d, ctx, gds, tds)


def decide_dti(d, ctx, gds=None, tds=None):
    if gds is None:
        gds, tds = dti_calc(d["h"], d["lines"])
    score = d["score"]
    msg = f"GDS {gds * 100:.1f}%, TDS {tds * 100:.1f}%, score {score} (AR-13)."
    if score < 600:
        return N, "DTI-02", f"Credit score {score} is below the 600 minimum. " + msg, False
    if gds <= 0.39 and tds <= 0.44:
        return S, "DTI-01", msg, False
    over = max(gds - 0.39, tds - 0.44)
    if over <= 0.02 and score >= 720:
        return R, "DTI-03", "Ratios exceed limits by 2 points or less with score 720+; exception to underwriter (AR-14). " + msg, False
    return N, "DTI-01", "Ratios exceed policy limits. " + msg, False


BUILDERS = {"income_proof": build_income, "down_payment_source": build_dp, "appraisal": build_appraisal,
            "employment": build_employment, "debt_ratio": build_dti}


# ---------------------------------------------------------------- junk + assembly
def junk_docs(rng, ctx):
    lang = ctx["lang"]
    ds = pick_style(rng)
    close = ctx["review"] + dt.timedelta(days=rng.randint(30, 70))
    aps = "\n".join([
        T(ctx, "AGREEMENT OF PURCHASE AND SALE - excerpt (pages 1 and 7 of 14)", "PROMESSE D'ACHAT - extrait (pages 1 et 7 de 14)"),
        f"{T(ctx, 'Property', 'Propriete')}: {ctx['address']}",
        f"{T(ctx, 'Purchase price', 'Prix d achat')}: {money(ctx['price'], lang, False)}   {T(ctx, 'Closing date', 'Date de cloture')}: {dstr(close, ds, lang)}",
        f"{T(ctx, 'Deposit paid', 'Depot verse')}: {money(round(ctx['price'] * 0.02, -2), lang, False)}",
    ])
    pool = [aps,
            T(ctx, "DRIVER LICENCE (copy, masked)\nName: " + ctx["borrower"] + "\nLicence no: XXXX-XXXX-" + str(rng.randint(1000, 9999)),
              "PERMIS DE CONDUIRE (copie, masque)\nNom: " + ctx["borrower"]),
            "VOID CHEQUE\nTransit 0" + str(rng.randint(1000, 9999)) + "  Institution 00" + str(rng.randint(1, 9)) + "  Account ******" + str(rng.randint(100, 999)),
            "FAX COVER SHEET\nTo: Mortgage Ops   Pages: 3   Re: documents as requested\n[handwritten: sorry for the blurry pages!]"]
    k = rng.randint(1, 3)
    out = [pool[0]]
    out += rng.sample(pool[1:], k - 1) if k > 1 else []
    return out


def header(ctx, conds):
    lang = ctx["lang"]
    inc = money(ctx["income"], lang, False)
    lines = [
        f"FILE {ctx['id']}  |  {T(ctx, 'UNDERWRITING CONDITIONS REVIEW', 'REVISION DES CONDITIONS DE SOUSCRIPTION')}",
        f"{T(ctx, 'Review date', 'Date de revision')}: {ctx['review'].isoformat()}",
        f"{T(ctx, 'Applicant', 'Demandeur')}: {ctx['borrower']}",
        f"{T(ctx, 'Property', 'Propriete')}: {ctx['address']} ({ctx['prop_type']})",
        f"{T(ctx, 'Purchase price', 'Prix d achat')}: {money(ctx['price'], lang, False)}   {T(ctx, 'Down payment', 'Mise de fonds')}: {money(ctx['down'], lang, False)}",
        f"{T(ctx, 'Stated annual income', 'Revenu annuel declare')}: {inc}   {T(ctx, 'Employer (stated)', 'Employeur (declare)')}: {ctx['employer']}",
        "",
        T(ctx, "CONDITIONS TO DECIDE:", "CONDITIONS A DECIDER:"),
    ]
    for cid, fam in conds:
        lines.append(f"  {cid} [{fam}] " + CONDITION_TEXT[fam][1 if lang == "fr" else 0].format(inc=inc))
    return "\n".join(lines)


def main():
    rng = random.Random(SEED)
    pools = {f: [t for t, _, w, _ in SCENARIOS[f] for _ in range(w)] for f in FAMILIES}
    for f in FAMILIES:
        rng.shuffle(pools[f])
    golden = []
    outdir = ROOT / "data" / "files"
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob("*.txt"):
        old.unlink()
    for i in range(1, N_FILES + 1):
        ctx = make_ctx(rng, i)
        k = rng.choice([3, 4, 4, 4, 5, 5])
        fams = sorted(rng.sample(FAMILIES, k), key=FAMILIES.index)
        conds, docs = [], []
        for n, fam in enumerate(fams, 1):
            if not pools[fam]:
                pools[fam] = [t for t, _, w, _ in SCENARIOS[fam] for _ in range(w)]
                rng.shuffle(pools[fam])
            sc = pools[fam].pop()
            cid = f"{ctx['id']}-C{n}"
            for attempt in range(80):
                d_docs, (dec, rule, why, miss) = BUILDERS[fam](rng, ctx, sc)
                if dec == EXPECTED[fam][sc]:
                    break
            else:
                raise RuntimeError(f"could not realise {fam}/{sc}")
            conds.append((cid, fam))
            docs += d_docs
            golden.append(dict(file_id=ctx["id"], condition_id=cid, family=fam, decision=dec, rule_id=rule,
                               rationale=why, scenario_tag=sc, ambiguity_ref=AMBIG[fam][sc],
                               missing_document="Y" if miss else "N"))
        docs += junk_docs(rng, ctx)
        rng.shuffle(docs)
        parts = [header(ctx, conds), ""]
        for j, text in enumerate(docs, 1):
            if rng.random() < 0.5:
                text = ocr_noise(text, rng, rng.uniform(0.01, 0.04))
            pages = rng.randint(1, 3)
            parts += [f"=== DOCUMENT {j} | {fname(rng)} | {pages} page(s) ===", text,
                      f"[scanned {ctx['review'].isoformat()} 09:{rng.randint(10, 59)} - page 1 of {pages} - CONFIDENTIAL]", ""]
        (outdir / f"{ctx['id']}.txt").write_text("\n".join(parts), encoding="utf-8")
    gdir = ROOT / "golden"
    gdir.mkdir(exist_ok=True)
    cols = list(golden[0].keys())
    with open(gdir / "golden_set.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(golden)
    from collections import Counter
    print(len(golden), "conditions;", dict(Counter(g["decision"] for g in golden)),
          dict(Counter(g["family"] for g in golden)))


if __name__ == "__main__":
    main()
