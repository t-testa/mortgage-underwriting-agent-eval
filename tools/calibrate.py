#!/usr/bin/env python3
"""Calibration exercise: two SIMULATED underwriting teams label the same 50 files.

IMPORTANT: the two teams are scripted. Each team has a stated "house style"
(Team A leans lenient, Team B leans strict or escalates) plus a small random
slip rate. They are not real people. The point is to demonstrate the method
(label, measure agreement, list disagreements, write arbitration rules), not to
claim real underwriter behaviour.

Outputs:
  calibration/team_a_labels.csv, team_b_labels.csv
  calibration/disagreements.csv
  calibration/kappa_report.md
"""
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S, N, R = "satisfied", "not_satisfied", "needs_review"
LABELS = [S, N, R]
SEED = 7

# (family, scenario_tag) -> (label the team tends to give, probability)
TEAM_A = {  # lenient: accepts borderline paperwork, rarely escalates
    ("income_proof", "shortfall_mid"): (S, 0.6), ("income_proof", "variable_one_year"): (S, 0.6),
    ("income_proof", "illegible"): (R, 0.6),
    ("down_payment_source", "unexplained_mid"): (S, 0.6), ("down_payment_source", "gift_far_relation"): (S, 0.7),
    ("appraisal", "shortfall_mid"): (S, 0.6), ("appraisal", "recommend_inspection"): (S, 0.6),
    ("employment", "probation"): (S, 0.5), ("employment", "contract_mid"): (S, 0.5),
    ("debt_ratio", "borderline_pass"): (S, 0.0),
}
TEAM_B = {  # strict: grace on stale docs, rejects or escalates edge cases
    ("income_proof", "stale_edge"): (S, 0.8), ("employment", "stale_edge"): (S, 0.8),
    ("income_proof", "shortfall_small"): (R, 0.5), ("income_proof", "variable_two_year"): (R, 0.5),
    ("appraisal", "shortfall_mid"): (N, 0.6), ("appraisal", "shortfall_small"): (R, 0.5),
    ("employment", "probation"): (N, 0.6), ("employment", "contract_mid"): (N, 0.5),
    ("employment", "salary_mismatch"): (N, 0.5), ("debt_ratio", "exception_band"): (N, 0.6),
    ("debt_ratio", "borderline_pass"): (R, 0.4), ("down_payment_source", "gift_far_relation"): (N, 0.6),
}
SLIP = 0.03


def team_label(rng, row, profile):
    truth = row["decision"]
    key = (row["family"], row["scenario_tag"])
    lab = truth
    if key in profile and rng.random() < profile[key][1]:
        lab = profile[key][0]
    if rng.random() < SLIP:
        lab = rng.choice([x for x in LABELS if x != lab])
    return lab


def kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in LABELS)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def band(k):  # Landis and Koch labels
    return ("poor" if k < 0 else "slight" if k < .21 else "fair" if k < .41 else "moderate" if k < .61
            else "substantial" if k < .81 else "almost perfect")


def main():
    gold = list(csv.DictReader(open(ROOT / "golden" / "golden_set.csv", encoding="utf-8")))
    rng_a, rng_b = random.Random(SEED), random.Random(SEED + 1)
    a = [team_label(rng_a, r, TEAM_A) for r in gold]
    b = [team_label(rng_b, r, TEAM_B) for r in gold]
    cal = ROOT / "calibration"
    for name, labs in (("team_a", a), ("team_b", b)):
        with open(cal / f"{name}_labels.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["file_id", "condition_id", "family", "label"])
            for r, l in zip(gold, labs):
                w.writerow([r["file_id"], r["condition_id"], r["family"], l])

    fam_rows = defaultdict(list)
    for r, x, y in zip(gold, a, b):
        fam_rows[r["family"]].append((x, y))
    out = ["# Calibration report: Team A vs Team B", "",
           "Both teams are SIMULATED (scripted house styles plus 3% random slips). See `tools/calibrate.py`.", "",
           "## Agreement by condition family", "",
           "| Family | Conditions | Raw agreement | Cohen's kappa | Reading |", "|---|---|---|---|---|"]
    for fam in sorted(fam_rows):
        xs, ys = zip(*fam_rows[fam])
        k = kappa(xs, ys)
        po = sum(p == q for p, q in zip(xs, ys)) / len(xs)
        out.append(f"| {fam} | {len(xs)} | {po * 100:.0f}% | {k:.2f} | {band(k)} |")
    k_all = kappa(a, b)
    out += [f"| **All families** | {len(a)} | {sum(p == q for p, q in zip(a, b)) / len(a) * 100:.0f}% | **{k_all:.2f}** | {band(k_all)} |", "",
            "Kappa corrects raw agreement for the agreement two labelers would reach by chance. "
            "A common working target before production labeling is 0.80 or higher.", ""]

    dis = [(r, x, y) for r, x, y in zip(gold, a, b) if x != y]
    with open(cal / "disagreements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file_id", "condition_id", "family", "team_a", "team_b", "golden_rule_id", "scenario_tag"])
        for r, x, y in dis:
            w.writerow([r["file_id"], r["condition_id"], r["family"], x, y, r["rule_id"], r["scenario_tag"]])
    pat = Counter((r["family"], r["rule_id"], r["scenario_tag"], x, y) for r, x, y in dis)
    out += [f"## Disagreements: {len(dis)} of {len(a)} conditions", "",
            "Grouped into patterns. Each recurring pattern is a candidate arbitration rule "
            "(see `policy/ARBITRATION_RULES.md`). One-off slips are listed in `disagreements.csv`.", "",
            "| Count | Family | Rule | Scenario | Team A | Team B |", "|---|---|---|---|---|---|"]
    for (fam, rule, sc, x, y), c in sorted(pat.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"| {c} | {fam} | {rule} | {sc} | {x} | {y} |")
    (cal / "kappa_report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
