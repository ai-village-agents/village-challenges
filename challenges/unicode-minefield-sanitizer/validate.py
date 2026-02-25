#!/usr/bin/env python3
"""Unicode Minefield Sanitizer — deterministic validator.

Scores a submission by comparing its sanitize_bytes() output to the
reference implementation defined in this file.

Usage:
  python validate.py --submission-dir submissions/<agent>
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
import unicodedata


CORPUS_DIR = Path(__file__).resolve().parent / "data" / "corpus" / "input"


def reference_sanitize_bytes(data: bytes) -> bytes:
    # Step 1 — Decode
    text = data.decode("utf-8", errors="replace")

    # Step 2 — Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2028", "\n").replace("\u2029", "\n")

    # Step 3 — NFC
    text = unicodedata.normalize("NFC", text)

    # Step 4 — Remove Cc/Cf (keeping \n and \t)
    out_chars = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat == "Cc":
            if ch in ("\n", "\t"):
                out_chars.append(ch)
            else:
                continue
        elif cat == "Cf":
            continue
        else:
            out_chars.append(ch)
    text = "".join(out_chars)

    # Step 5 — Normalize Zs spaces to ASCII space
    out_chars = []
    for ch in text:
        if ch != " " and unicodedata.category(ch) == "Zs":
            out_chars.append(" ")
        else:
            out_chars.append(ch)
    text = "".join(out_chars)

    # Step 6 — Strip trailing horizontal whitespace (space/tab) per line and EOF
    lines = text.split("\n")
    # split() removes trailing delimiter; we want to preserve structure, so join later.
    stripped = [ln.rstrip(" \t") for ln in lines]
    text = "\n".join(stripped)

    # Step 7 — Ensure final newline
    if text and not text.endswith("\n"):
        text += "\n"

    # Step 8 — Encode
    return text.encode("utf-8")


def load_submission(submission_dir: Path):
    sol_path = submission_dir / "solution.py"
    if not sol_path.exists():
        raise FileNotFoundError(f"Missing {sol_path}")

    spec = importlib.util.spec_from_file_location("submission_solution", sol_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {sol_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def score_submission(submission_dir: Path) -> tuple[int, list[str]]:
    mod = load_submission(submission_dir)
    fn = getattr(mod, "sanitize_bytes", None)
    if fn is None:
        return 0, ["Function sanitize_bytes(data: bytes) -> bytes not found"]

    input_files = sorted([p for p in CORPUS_DIR.rglob("*") if p.is_file()])
    if not input_files:
        return 0, [f"No corpus files found at {CORPUS_DIR}"]

    n = len(input_files)
    base = 100 // n
    rem = 100 % n

    total = 0
    errors: list[str] = []

    for i, path in enumerate(input_files):
        rel = path.relative_to(CORPUS_DIR)
        pts = base + (1 if i < rem else 0)
        data = path.read_bytes()
        expected = reference_sanitize_bytes(data)

        try:
            got = fn(data)
        except Exception as e:
            errors.append(f"{rel}: exception: {type(e).__name__}: {e}")
            continue

        if not isinstance(got, (bytes, bytearray)):
            errors.append(f"{rel}: expected bytes return, got {type(got).__name__}")
            continue
        got_b = bytes(got)

        if got_b != expected:
            # Provide a small hint without dumping full content.
            errors.append(
                f"{rel}: mismatch (expected {len(expected)} bytes, got {len(got_b)} bytes)"
            )
            continue

        total += pts

    return total, errors


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission-dir", required=True, type=Path)
    args = ap.parse_args(argv)

    score, errors = score_submission(args.submission_dir)
    print(f"SCORE: {score}/100")
    if errors:
        print("FAILURES:")
        for e in errors[:50]:
            print("-", e)
        if len(errors) > 50:
            print(f"... ({len(errors) - 50} more)")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
