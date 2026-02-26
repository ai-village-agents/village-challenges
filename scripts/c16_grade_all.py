#!/usr/bin/env python3
"""Helper script to re-run the C16 Rashomon grader over a
curated list of submissions, based only on data in this git repo.

This tool is intentionally read-only with respect to git: it never
modifies the working tree, never checks out branches, and never commits.
Instead, it uses `git show <revision>:<path>` to snapshot the relevant
Rashomon grader script and submission files into a temporary directory,
then invokes the official C16 grader on those snapshots.

Config schema (JSON):

{
  "challenge": {
    "grader_branch": "origin/challenge-15-claude-opus-4-5-proposal",
    "grader_path": "challenges/challenge-15-claude-opus-4-5/grade.py",
    "kind": "rashomon"
  },
  "submissions": [
    {
      "id": "c16-rashomon-claude-opus-4-6",
      "agent": "claude-opus-4-6",
      "pr": 266,
      "branch": "origin/c16-opus-4-6-rashomon",
      "submission_path": "challenges/.../submissions/claude-opus-4-6/submission.md",
      "notes": "optional free-form notes"
    },
    ...
  ]
}

The script emits a JSON summary (either to stdout or to --output-json)
containing per-submission automated factual-consistency scores and raw
grader output, and optionally writes a Markdown table when --output-md
is provided.

Note: C16's official scoring rubric is 20 automated points for factual
consistency plus 80 points of manual rubric-based scoring. This helper
only re-computes the *automated* 20-point consistency component; it
does not attempt to reproduce the subjective rubric scores.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ----------------------
# Git helpers
# ----------------------


def run_git_show(revision: str, path: str) -> str:
    """Return the blob contents for revision:path via `git show`.

    Raises RuntimeError on failure.
    """

    proc = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git show {revision}:{path} failed (code {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def materialize_blob(revision: str, repo_rel_path: str, dest_path: Path) -> None:
    """Materialize a single file from git into dest_path.

    Parent directories are created as needed.
    """

    content = run_git_show(revision, repo_rel_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")


# ----------------------
# Config structures
# ----------------------


@dataclass
class ChallengeConfig:
    grader_branch: str
    grader_path: str
    kind: str  # e.g. "rashomon"


@dataclass
class SubmissionConfig:
    sid: str
    agent: str
    pr: Optional[int]
    branch: str
    submission_path: str
    notes: Optional[str]


def load_config(path: Path) -> Tuple[ChallengeConfig, List[SubmissionConfig]]:
    """Load and validate the JSON config file.

    Returns (challenge_cfg, submissions).
    """

    raw = json.loads(path.read_text(encoding="utf-8"))

    challenge_raw = raw.get("challenge")
    if not isinstance(challenge_raw, dict):
        raise SystemExit("Config error: 'challenge' object is required")

    try:
        challenge_cfg = ChallengeConfig(
            grader_branch=str(challenge_raw["grader_branch"]),
            grader_path=str(challenge_raw["grader_path"]),
            kind=str(challenge_raw["kind"]),
        )
    except KeyError as exc:  # pragma: no cover - config shape error
        raise SystemExit(f"Config error in 'challenge': missing {exc}") from exc

    submissions_raw = raw.get("submissions") or []
    if not isinstance(submissions_raw, list):
        raise SystemExit("Config error: 'submissions' must be a list")

    subs: List[SubmissionConfig] = []
    for item in submissions_raw:
        if not isinstance(item, dict):
            raise SystemExit("Config error: each submission must be an object")
        try:
            sid = str(item["id"])
            agent = str(item["agent"])
            branch = str(item["branch"])
            submission_path = str(item["submission_path"])
        except KeyError as exc:
            raise SystemExit(f"Config error in submissions: missing {exc}") from exc

        pr_val = item.get("pr")
        pr_int: Optional[int]
        if isinstance(pr_val, int):
            pr_int = pr_val
        else:
            try:
                pr_int = int(pr_val) if pr_val is not None else None
            except (TypeError, ValueError):
                pr_int = None

        notes_val = item.get("notes")
        notes_str = str(notes_val) if notes_val is not None else None

        subs.append(
            SubmissionConfig(
                sid=sid,
                agent=agent,
                pr=pr_int,
                branch=branch,
                submission_path=submission_path,
                notes=notes_str,
            )
        )

    return challenge_cfg, subs


# ----------------------
# Snapshot helpers
# ----------------------


def snapshot_grader(cfg: ChallengeConfig, tmp_dir: Path) -> Path:
    """Materialize the C16 Rashomon grader into tmp_dir and return its path.

    Raises RuntimeError on failure.
    """

    dest = tmp_dir / "graders" / "c16_rashomon_grade.py"
    materialize_blob(cfg.grader_branch, cfg.grader_path, dest)
    return dest


def snapshot_submission(sub: SubmissionConfig, tmp_dir: Path) -> Path:
    """Materialize a submission file into tmp_dir and return its path.

    Raises RuntimeError on failure.
    """

    basename = os.path.basename(sub.submission_path) or "submission.md"
    dest = tmp_dir / "subs" / f"{sub.sid}__{basename}"
    materialize_blob(sub.branch, sub.submission_path, dest)
    return dest


# ----------------------
# Subprocess and grading
# ----------------------


def run_subprocess(args: List[str]) -> Tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""

    proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


# Example tail of official C16 grade.py output:
#   Overall consistency score: 100.0%
#   ...
#   [AUTOMATED SCORE: 20.0/20]

_AUTO_SCORE_RE = re.compile(r"\[AUTOMATED SCORE:\s*([0-9]+(?:\.[0-9]+)?)/20\]")
_CONSISTENCY_RE = re.compile(r"Overall consistency score:\s*([0-9]+(?:\.[0-9]+)?)%")


def grade_submission(grader_path: Path, sub_path: Path) -> Dict[str, Any]:
    """Invoke the C16 grader on a single submission snapshot.

    Returns a dict with keys: score (0–20 automated), consistency_pct,
    automated_checks_passed, status, raw_stdout, raw_stderr, error.
    """

    python_exe = sys.executable or "python3"
    rc, stdout, stderr = run_subprocess([python_exe, str(grader_path), str(sub_path)])

    status = "ok"
    error: Optional[str] = None

    if rc != 0:
        status = "grader-error"
        error = f"grader exited with code {rc}"

    score: Optional[float] = None
    m = _AUTO_SCORE_RE.search(stdout)
    if m:
        try:
            score = float(m.group(1))
        except ValueError:
            score = None
            if status == "ok":
                status = "parse-error"
                error = "could not parse float score from AUTOMATED SCORE line"
    else:
        if status == "ok":
            status = "parse-error"
            error = "AUTOMATED SCORE line not found in grader output"

    consistency_pct: Optional[float] = None
    m2 = _CONSISTENCY_RE.search(stdout)
    if m2:
        try:
            consistency_pct = float(m2.group(1))
        except ValueError:
            consistency_pct = None

    automated_checks_passed: Optional[bool]
    if "All automated checks PASSED" in stdout:
        automated_checks_passed = True
    elif "Some automated checks FAILED" in stdout:
        automated_checks_passed = False
    else:
        automated_checks_passed = None

    if rc == 0 and score is not None:
        status = "ok"

    return {
        "score": score,  # 0–20 automated factual-consistency points
        "consistency_pct": consistency_pct,
        "automated_checks_passed": automated_checks_passed,
        "status": status,
        "raw_stdout": stdout,
        "raw_stderr": stderr,
        "error": error,
    }


# ----------------------
# Markdown rendering
# ----------------------


def write_markdown(results: List[Dict[str, Any]], cfg: ChallengeConfig, path: Path) -> None:
    """Write a simple Markdown table summarizing automated grading results."""

    headers = [
        "id",
        "agent",
        "pr",
        "auto_20",
        "consistency_pct",
        "auto_checks_passed",
        "status",
        "notes",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]

    # Sort: automated score desc (None last), then pr asc (None last), then id lexicographically
    def sort_key(row: Dict[str, Any]) -> Tuple[int, int, str]:
        score = row.get("score")
        # Use negative integer score for descending sort; floats get truncated
        score_key = -int(score) if isinstance(score, (int, float)) else 10**9
        pr = row.get("pr")
        pr_key = int(pr) if isinstance(pr, int) else 10**9
        sid = str(row.get("id") or "")
        return (score_key, pr_key, sid)

    for row in sorted(results, key=sort_key):
        auto_val = row.get("score")
        consistency_val = row.get("consistency_pct")
        auto_str = "" if auto_val is None else f"{auto_val:.1f}" if isinstance(auto_val, float) else str(auto_val)
        consistency_str = (
            "" if consistency_val is None else f"{consistency_val:.1f}"
            if isinstance(consistency_val, float)
            else str(consistency_val)
        )
        auto_passed = row.get("automated_checks_passed")
        if auto_passed is True:
            passed_str = "yes"
        elif auto_passed is False:
            passed_str = "no"
        else:
            passed_str = "?"

        vals = [
            str(row.get("id") or ""),
            str(row.get("agent") or ""),
            str(row.get("pr") or ""),
            auto_str,
            consistency_str,
            passed_str,
            str(row.get("status") or ""),
            str(row.get("notes") or ""),
        ]
        lines.append("| " + " | ".join(vals) + " |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------
# Main CLI
# ----------------------


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Re-run C16 Rashomon automated factual-consistency grader over "
            "configured submissions."
        )
    )
    parser.add_argument("--config", required=True, help="Path to C16 config JSON file.")
    parser.add_argument(
        "--output-json",
        help=(
            "Optional path to write JSON summary. If omitted, prints to stdout. "
            "Includes raw grader output for each submission."
        ),
    )
    parser.add_argument(
        "--output-md",
        help=(
            "Optional path to write Markdown table summary of automated scores."
        ),
    )
    parser.add_argument(
        "--tmp-dir",
        default=".c16_helper_tmp",
        help="Temporary directory for grader and submission snapshots (default: .c16_helper_tmp)",
    )

    args = parser.parse_args(argv)

    config_path = Path(args.config)
    tmp_dir = Path(args.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    challenge_cfg, submissions = load_config(config_path)

    try:
        grader_path = snapshot_grader(challenge_cfg, tmp_dir)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"Failed to snapshot grader: {exc}") from exc

    results: List[Dict[str, Any]] = []

    for sub in submissions:
        try:
            local_sub_path = snapshot_submission(sub, tmp_dir)
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "id": sub.sid,
                    "agent": sub.agent,
                    "pr": sub.pr,
                    "branch": sub.branch,
                    "submission_path": sub.submission_path,
                    "local_path": None,
                    "score": None,
                    "consistency_pct": None,
                    "automated_checks_passed": None,
                    "status": "submission-missing",
                    "error": str(exc),
                    "raw_stdout": "",
                    "raw_stderr": "",
                    "notes": sub.notes,
                }
            )
            continue

        grade_info = grade_submission(grader_path, local_sub_path)
        results.append(
            {
                "id": sub.sid,
                "agent": sub.agent,
                "pr": sub.pr,
                "branch": sub.branch,
                "submission_path": sub.submission_path,
                "local_path": str(local_sub_path),
                "score": grade_info["score"],
                "consistency_pct": grade_info["consistency_pct"],
                "automated_checks_passed": grade_info["automated_checks_passed"],
                "status": grade_info["status"],
                "error": grade_info["error"],
                "raw_stdout": grade_info["raw_stdout"],
                "raw_stderr": grade_info["raw_stderr"],
                "notes": sub.notes,
            }
        )

    output: Dict[str, Any] = {
        "metadata": {
            "challenge_kind": challenge_cfg.kind,
            "grader_branch": challenge_cfg.grader_branch,
            "grader_path": challenge_cfg.grader_path,
            "total_submissions": len(submissions),
        },
        "results": results,
    }

    json_text = json.dumps(output, indent=2, sort_keys=True)

    if args.output_json:
        Path(args.output_json).write_text(json_text + "\n", encoding="utf-8")
    else:
        print(json_text)

    if args.output_md:
        write_markdown(results, challenge_cfg, Path(args.output_md))


if __name__ == "__main__":  # pragma: no cover
    main()
