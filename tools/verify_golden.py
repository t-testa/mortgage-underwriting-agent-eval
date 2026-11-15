#!/usr/bin/env python3
"""Check that the golden sets still match their locked SHA-256 hashes.

Usage: python tools/verify_golden.py
Exit code 0 means both golden sets are untouched since they were locked.
To lock a set the first time (done once, never again):
  python tools/verify_golden.py --lock
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETS = [ROOT / "golden" / "golden_set.csv", ROOT / "data" / "holdout" / "golden_set.csv"]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    lock = "--lock" in sys.argv
    ok = True
    for p in SETS:
        h = p.with_suffix(".sha256")
        if lock:
            if h.exists():
                print(f"refusing to re-lock {p.relative_to(ROOT)}: hash file already exists")
                continue
            h.write_text(f"{digest(p)}  {p.name}\n", encoding="utf-8")
            print(f"locked {p.relative_to(ROOT)}")
            continue
        want = h.read_text(encoding="utf-8").split()[0]
        good = digest(p) == want
        ok &= good
        print(("OK       " if good else "CHANGED  ") + str(p.relative_to(ROOT)))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
