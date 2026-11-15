#!/usr/bin/env python3
"""Score one shadow-mode run against the golden set and build its review queue.

Usage:
  python tools/score_run.py --run baseline_v1 --raw-dir <folder with MF-xxx.json> --ar-in-policy no
  python tools/score_run.py --run tuned_v2    --raw-dir <folder with MF-xxx.json> --ar-in-policy yes

The golden set is only ever READ here. Nothing in this repo writes to it after
tools/generate_data.py created it.

Review queue reason tags (a first-pass triage by script; a human confirms in practice):
  missing_document  the golden decision turns on a missing or unreadable document
  policy_ambiguity  the policy text the agent was given did not settle the question
                    (the golden condition is tied to an arbitration rule AND the agent run
                    did not include the arbitration rules)
  agent_error       everything else: the policy was clear enough and the agent got it wrong
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["satisfied", "not_satisfied", "needs_review"]
FAMILIES = ["income_proof", "down_payment_source", "appraisal", "employment", "debt_ratio"]


def severity(agent, gold):
    if agent == "satisfied" and gold == "not_satisfied":
        return "P1 critical (false approval)"
    if agent == "satisfied" and gold == "needs_review":
        return "P2 high (skipped a required escalation)"
    if agent == "not_satisfied" and gold == "satisfied":
        return "P3 medium (false decline, causes rework)"
    if agent == "not_satisfied" and gold == "needs_review":
        return "P3 medium (decided a policy call)"
    return "P4 low (over-escalation, extra human touch)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--ar-in-policy", choices=["yes", "no"], required=True)
    a = ap.parse_args()
    gold = list(csv.DictReader(open(ROOT / "golden" / "golden_set.csv", encoding="utf-8")))
    agent = {}
    for p in sorted(Path(a.raw_dir).glob("MF-*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        for d in obj["decisions"]:
            agent[d["condition_id"]] = d
    run_dir = ROOT / "shadow" / "runs" / a.run
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw").mkdir(exist_ok=True)
    for p in Path(a.raw_dir).glob("MF-*.json"):
        (run_dir / "raw" / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

    rows, queue = [], []
    for g in gold:
        d = agent.get(g["condition_id"])
        dec = d["decision"] if d else "no_answer"
        ok = dec == g["decision"]
        rows.append(dict(condition_id=g["condition_id"], family=g["family"], golden=g["decision"], agent=dec,
                         match="Y" if ok else "N", agent_rule=(d or {}).get("rule_cited", ""), golden_rule=g["rule_id"]))
        if not ok:
            if g["missing_document"] == "Y":
                reason = "missing_document"
            elif g["ambiguity_ref"] and a.ar_in_policy == "no":
                reason = "policy_ambiguity"
            else:
                reason = "agent_error"
            queue.append(dict(
                condition_id=g["condition_id"], family=g["family"], golden=g["decision"], agent=dec,
                severity=severity(dec, g["decision"]), reason_tag=reason, golden_rule=g["rule_id"],
                ambiguity_ref=g["ambiguity_ref"], agent_rule=(d or {}).get("rule_cited", ""),
                golden_rationale=g["rationale"], agent_rationale=(d or {}).get("rationale", "")))
    queue.sort(key=lambda q: (q["severity"], q["family"], q["condition_id"]))

    def write(name, data):
        with open(run_dir / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    write("decisions.csv", rows)
    if queue:
        write("review_queue.csv", queue)

    n = len(rows)
    fam = defaultdict(lambda: Counter())
    for r in rows:
        fam[r["family"]]["n"] += 1
        fam[r["family"]]["ok"] += r["match"] == "Y"
        fam[r["family"]]["auto"] += r["agent"] in ("satisfied", "not_satisfied")
        fam[r["family"]]["auto_wrong"] += r["agent"] in ("satisfied", "not_satisfied") and r["match"] == "N"
        fam[r["family"]]["review"] += r["agent"] == "needs_review"
    conf = Counter((r["golden"], r["agent"]) for r in rows)
    metrics = dict(
        run=a.run, conditions=n, correct=sum(r["match"] == "Y" for r in rows),
        accuracy=sum(r["match"] == "Y" for r in rows) / n,
        auto_decided=sum(r["agent"] in ("satisfied", "not_satisfied") for r in rows),
        auto_wrong=sum(r["agent"] in ("satisfied", "not_satisfied") and r["match"] == "N" for r in rows),
        agent_needs_review=sum(r["agent"] == "needs_review" for r in rows),
        no_answer=sum(r["agent"] == "no_answer" for r in rows),
        false_approvals=sum(r["agent"] == "satisfied" and r["golden"] == "not_satisfied" for r in rows),
        skipped_escalations=sum(r["agent"] == "satisfied" and r["golden"] == "needs_review" for r in rows),
        queue_by_reason=dict(Counter(q["reason_tag"] for q in queue)),
        queue_by_severity=dict(Counter(q["severity"] for q in queue)),
        by_family={f: dict(fam[f]) for f in FAMILIES},
        confusion={f"{g}|{p}": c for (g, p), c in conf.items()},
    )
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    md = [f"# Shadow run: {a.run}", "",
          f"Arbitration rules included in the agent's policy: **{a.ar_in_policy}**", "",
          f"- Conditions scored: {n}", f"- Correct: {metrics['correct']} ({metrics['accuracy'] * 100:.1f}%)",
          f"- Divergences (review queue size): {len(queue)}",
          f"- False approvals (agent satisfied, golden not satisfied): {metrics['false_approvals']}",
          f"- Skipped escalations (agent satisfied, golden needs review): {metrics['skipped_escalations']}", "",
          "## Accuracy and divergence by family", "",
          "| Family | Conditions | Correct | Accuracy | Divergence rate |", "|---|---|---|---|---|"]
    for f in FAMILIES:
        c = fam[f]
        md.append(f"| {f} | {c['n']} | {c['ok']} | {c['ok'] / c['n'] * 100:.0f}% | {(1 - c['ok'] / c['n']) * 100:.0f}% |")
    md += ["", "## Confusion matrix (rows golden, columns agent)", "",
           "| golden / agent | satisfied | not_satisfied | needs_review | no_answer |", "|---|---|---|---|---|"]
    for g in LABELS:
        md.append(f"| {g} | " + " | ".join(str(conf[(g, p)]) for p in LABELS + ["no_answer"]) + " |")
    md += ["", "## Review queue by reason tag", "", "| Reason | Count |", "|---|---|"]
    for k, v in sorted(metrics["queue_by_reason"].items()):
        md.append(f"| {k} | {v} |")
    md += ["", "## Review queue by severity", "", "| Severity | Count |", "|---|---|"]
    for k, v in sorted(metrics["queue_by_severity"].items()):
        md.append(f"| {k} | {v} |")
    (run_dir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
