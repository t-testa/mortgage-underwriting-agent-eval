#!/usr/bin/env python3
"""OPTIONAL runner: run shadow mode through the Anthropic Messages API.

The results published in this repo were NOT produced with this script (they came
from fresh Claude Code subagents, see README). This script exists so the same
experiment can be repeated against the API. It has only been tested with --dry-run.

Usage:
  set ANTHROPIC_API_KEY=...   (your own key, in your own environment)
  python tools/run_agent_api.py --prompt prompts/agent_prompt_v1.md --policy policy/POLICY_v1_0.md --out shadow/api_out_v1
  python tools/run_agent_api.py --dry-run --prompt prompts/agent_prompt_v2.md --policy policy/POLICY_v1_1.md --out x

Then score:  python tools/score_run.py --run api_v1 --raw-dir shadow/api_out_v1 --ar-in-policy no
Standard library only. Never put a key in a file.
"""
import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "claude-sonnet-5-5"


def call(key, system, user):
    body = json.dumps({"model": MODEL, "max_tokens": 3000, "temperature": 0, "system": system,
                       "messages": [{"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["content"][0]["text"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    system = Path(a.prompt).read_text(encoding="utf-8") + "\n\n# POLICY\n\n" + Path(a.policy).read_text(encoding="utf-8")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and not a.dry_run:
        raise SystemExit("Set ANTHROPIC_API_KEY in your environment, or use --dry-run.")
    for f in sorted((ROOT / "data" / "files").glob("MF-*.txt")):
        user = f.read_text(encoding="utf-8")
        if a.dry_run:
            print(f"{f.name}: system {len(system)} chars, user {len(user)} chars")
            continue
        text = call(key, system, user)
        m = re.search(r"\{.*\}", text, re.S)
        (out / f"{f.stem}.json").write_text(json.dumps(json.loads(m.group(0)), indent=2), encoding="utf-8")
        print("done", f.name)


if __name__ == "__main__":
    main()
