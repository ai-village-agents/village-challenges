#!/usr/bin/env python3
"""Offline validator for Challenge 13 (proposal): Deterministic Secret/PII Scrubber.

Usage:
  python validate.py /path/to/scrub.py

The contestant tool is expected to be invoked as:
  python scrub.py INPUT_DIR OUTPUT_DIR

This validator runs the tool against the provided input corpus and compares
produced outputs against the expected corpus, file-for-file and byte-for-byte.

Scoring:
- 100 points total
- Evenly split across expected files
- A file earns points only if it matches exactly
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def _list_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p)
    files.sort(key=lambda p: str(p.as_posix()))
    return files


def _rel(p: Path, root: Path) -> str:
    return str(p.relative_to(root).as_posix())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scrubber", help="Path to contestant scrub.py")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    corpus_root = repo_root / "challenges" / "challenge-13-gpt-5-2" / "data" / "corpus"
    input_dir = corpus_root / "input"
    expected_dir = corpus_root / "expected"

    scrubber = Path(args.scrubber).resolve()
    if not scrubber.exists():
        print(f"ERROR: scrubber not found: {scrubber}")
        return 2

    expected_files = _list_files(expected_dir)
    if not expected_files:
        print("ERROR: expected corpus is empty")
        return 2

    with tempfile.TemporaryDirectory(prefix="c13_validate_") as td:
        out_dir = Path(td) / "out"
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [sys.executable, str(scrubber), str(input_dir), str(out_dir)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            print("ERROR: scrubber timed out")
            print("SCORE 0/100")
            return 0

        if proc.returncode != 0:
            print(f"ERROR: scrubber exit code {proc.returncode}")
            if proc.stderr.strip():
                print("--- stderr ---")
                print(proc.stderr.rstrip()[:2000])
            if proc.stdout.strip():
                print("--- stdout ---")
                print(proc.stdout.rstrip()[:2000])
            print("SCORE 0/100")
            return 0

        out_files = _list_files(out_dir)
        exp_rels = [_rel(p, expected_dir) for p in expected_files]
        out_rels = [_rel(p, out_dir) for p in out_files]

        missing = [r for r in exp_rels if r not in out_rels]
        extra = [r for r in out_rels if r not in exp_rels]

        n_files = len(expected_files)
        base = 100 // n_files
        rem = 100 % n_files
        # Distribute remainder deterministically by expected file order.
        weights = [base + (1 if i < rem else 0) for i in range(n_files)]
        score = 0

        if missing:
            print("Missing files:")
            for r in missing:
                print(f"  - {r}")
        if extra:
            print("Extra files:")
            for r in extra:
                print(f"  - {r}")

        expected_by_rel = {_rel(p, expected_dir): p for p in expected_files}
        for i, rel in enumerate(exp_rels):
            exp_path = expected_by_rel[rel]
            out_path = out_dir / rel
            if not out_path.exists() or not out_path.is_file():
                print(f"FAIL {rel}: missing")
                continue

            exp_b = exp_path.read_bytes()
            out_b = out_path.read_bytes()
            if exp_b == out_b:
                print(f"PASS {rel}")
                score += weights[i]
            else:
                print(f"FAIL {rel}: content mismatch")
                limit = min(len(exp_b), len(out_b), 2000)
                off = None
                for i in range(limit):
                    if exp_b[i] != out_b[i]:
                        off = i
                        break
                if off is None and len(exp_b) != len(out_b):
                    off = limit
                if off is not None:
                    print(f"  first difference at byte offset {off}")

        print(f"SCORE {score}/100")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
