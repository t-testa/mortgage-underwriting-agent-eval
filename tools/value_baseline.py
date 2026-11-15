#!/usr/bin/env python3
"""Value baseline report: automation, divergence, touches, cycle time, rework.

Reads shadow/runs/<run>/metrics.json and config_log/value_assumptions.json.
All business parameters are ILLUSTRATIVE assumptions (see that file).

Definitions
  Automation rate        share of conditions the agent decides itself (satisfied or not_satisfied)
  Safe automation rate   share the agent decides itself AND gets right vs the golden set
  Divergence rate        share where agent differs from golden
  Baseline touches       manual process: every condition gets one human touch, plus rework touches
  Future-state touches   agent needs_review items (human decides) + QA sample of automated decisions
                         + rework for wrong automated decisions (counted in full, conservative)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAMS = ["income_proof", "down_payment_source", "appraisal", "employment", "debt_ratio"]


def compute(m, A):
    n = m["conditions"]
    files = m.get("files", A["files_measured"])
    mins = A["manual_minutes_per_condition"]
    base_touch = n * (1 + A["manual_rework_rate"])
    base_min = sum(m["by_family"][f]["n"] * mins[f] for f in FAMS) * (1 + A["manual_rework_rate"] * A["rework_minutes_multiplier"])
    fut_touch = fut_min = 0.0
    for f in FAMS:
        c = m["by_family"][f]
        qa = c["auto"] * A["qa_sample_rate"]
        fut_touch += c["review"] + qa + c["auto_wrong"]
        fut_min += (c["review"] * A["human_review_minutes_multiplier"] + qa * A["qa_minutes_multiplier"]
                    + c["auto_wrong"] * A["rework_minutes_multiplier"]) * mins[f]
    auto_share = m["auto_decided"] / n
    wait_base = A["queue_wait_hours_per_human_touch"]
    wait_fut = (1 - auto_share) * wait_base + auto_share * A["agent_decision_wait_hours"]
    scale = A["scale_to_files"] / files
    return dict(
        n=n, auto=auto_share, safe=(m["auto_decided"] - m["auto_wrong"]) / n, diverge=1 - m["accuracy"],
        base_touch=base_touch, fut_touch=fut_touch, touch_saved=base_touch - fut_touch,
        touch_saved_pct=(base_touch - fut_touch) / base_touch,
        base_hours=base_min / 60, fut_hours=fut_min / 60, hours_saved=(base_min - fut_min) / 60,
        hours_saved_scaled=(base_min - fut_min) / 60 * scale,
        files=files, accuracy=m["accuracy"], wait_base=wait_base, wait_fut=wait_fut, wait_saved_pct=(wait_base - wait_fut) / wait_base,
        rework_base=A["manual_rework_rate"], rework_agent=m["auto_wrong"] / n,
        false_approvals=m["false_approvals"], scale=scale)


def main():
    runs = sys.argv[1:] or ["baseline_v1", "tuned_v2", "holdout_baseline_v1", "holdout_tuned_v2"]
    A = json.loads((ROOT / "config_log" / "value_assumptions.json").read_text(encoding="utf-8"))
    M = {r: json.loads((ROOT / "shadow" / "runs" / r / "metrics.json").read_text(encoding="utf-8")) for r in runs}
    V = {r: compute(M[r], A) for r in runs}
    pct = lambda x: f"{x * 100:.1f}%"
    out = ["# Value baseline report", "",
           "**Read this first.** Agent results are measured against the golden set. Columns baseline_v1 and tuned_v2 use the 50 tuning files; "
           "holdout_* columns use 20 unseen files (MF-101 to MF-120) and a separate, hash-locked golden set. "
           "Manual-process numbers (minutes per condition, rework rate, queue wait) are ILLUSTRATIVE assumptions in "
           "`config_log/value_assumptions.json`, not measurements. In a real engagement they come from the client's "
           "signed process blueprint and every result is compared to that baseline.", "",
           "## Headline metrics", "",
           "| Metric | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
    rows = [("Files / conditions scored", lambda v: f"{v['files']} / {v['n']}"),
            ("Accuracy vs golden", lambda v: pct(v["accuracy"])),
            ("Automation rate (agent decides itself)", lambda v: pct(v["auto"])),
            ("Safe automation rate (decides itself and is right)", lambda v: pct(v["safe"])),
            ("Divergence rate vs golden", lambda v: pct(v["diverge"])),
            ("False approvals (agent satisfied, golden not satisfied)", lambda v: str(v["false_approvals"]))]
    for label, fn in rows:
        out.append(f"| {label} | " + " | ".join(fn(V[r]) for r in runs) + " |")
    out += ["", "## Divergence rate by condition family", "",
            "| Family | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
    for f in FAMS:
        out.append(f"| {f} | " + " | ".join(pct(1 - M[r]["by_family"][f]["ok"] / M[r]["by_family"][f]["n"]) for r in runs) + " |")
    out += ["", "## Estimated interventions, effort, cycle time and rework (assumption-driven)", "",
            "| Metric | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
    rows2 = [
        ("Human touches, manual process (this run's files)", lambda v: f"{v['base_touch']:.0f}"),
        ("Human touches, with agent (this run's files)", lambda v: f"{v['fut_touch']:.0f}"),
        ("Touches avoided", lambda v: f"{v['touch_saved']:.0f} ({pct(v['touch_saved_pct'])})"),
        ("Handling hours saved (this run's files)", lambda v: f"{v['hours_saved']:.1f} h"),
        (f"Handling hours saved, scaled to {int(A['scale_to_files'])} files", lambda v: f"{v['hours_saved_scaled']:.0f} h"),
        ("Avg queue wait per condition, manual", lambda v: f"{v['wait_base']:.1f} h"),
        ("Avg queue wait per condition, with agent", lambda v: f"{v['wait_fut']:.2f} h ({pct(v['wait_saved_pct'])} lower)"),
        ("Rework rate, manual (assumed)", lambda v: pct(v["rework_base"])),
        ("Rework rate caused by wrong automated decisions (measured)", lambda v: pct(v["rework_agent"])),
    ]
    for label, fn in rows2:
        out.append(f"| {label} | " + " | ".join(fn(V[r]) for r in runs) + " |")
    out += ["", "## How to read the numbers", "",
            "- A high automation rate is only valuable if the safe automation rate is close to it. The gap between "
            "the two is wrong automated decisions, each of which becomes rework.",
            "- False approvals are the risk metric. They are reported separately because one false approval can cost more than "
            "many saved minutes.",
            "- Touches avoided and hours saved move with the assumptions. Change a parameter in "
            "`config_log/value_assumptions.json` and rerun `python tools/value_baseline.py` to see sensitivity.",
            "- Rework from wrong automated decisions is counted in full (conservative). A QA sample would catch only "
            "part of it before it reaches a borrower.", ""]
    (ROOT / "reports" / "VALUE_BASELINE.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
