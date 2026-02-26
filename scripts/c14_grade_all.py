#!/usr/bin/env python3
"""Helper script to re-run all four C14 graders over a curated list of
submissions, based only on data in this git repo.

This tool is intentionally read-only with respect to git: it never
touches the working tree, never checks out branches, and never commits.
Instead, it uses `git show <revision>:<path>` to snapshot the relevant
grader scripts and submission/input files into a temporary directory,
then invokes each challenge's official grader on those snapshots.

Limitations / notes:
- Supply Chain scoring is approximated: we currently grade only against
  `hard.json` from the Haiku supply-chain proposal, not an aggregate over
  easy/medium/hard. Official scores elsewhere may differ slightly.
- Multi-Stage Optimization submissions must provide an `input_path` in
  the config so we know which JSON input to pair with each submission.
- This script relies entirely on the config JSON to decide which
  branches and paths to use; it does not attempt to discover PRs or
  submissions from GitHub.
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
    key: str
    grader_branch: str
    grader_path: str
    kind: str  # one of: trolley, logic, supply, multi


@dataclass
class SubmissionConfig:
    sid: str
    challenge: str
    agent: str
    pr: Optional[int]
    branch: str
    submission_path: str
    notes: Optional[str]
    # Optional multi-specific field
    input_path: Optional[str]


def load_config(path: Path) -> Tuple[Dict[str, ChallengeConfig], List[SubmissionConfig]]:
    raw = json.loads(path.read_text(encoding="utf-8"))

    challenges_raw = raw.get("challenges") or {}
    submissions_raw = raw.get("submissions") or []

    challenges: Dict[str, ChallengeConfig] = {}
    for key, cfg in challenges_raw.items():
        try:
            challenges[key] = ChallengeConfig(
                key=key,
                grader_branch=str(cfg["grader_branch"]),
                grader_path=str(cfg["grader_path"]),
                kind=str(cfg["kind"]),
            )
        except KeyError as exc:
            raise SystemExit(f"Config error for challenge '{key}': missing {exc}") from exc

    subs: List[SubmissionConfig] = []
    for item in submissions_raw:
        try:
            sid = str(item["id"])
            challenge_key = str(item["challenge"])
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

        subs.append(
            SubmissionConfig(
                sid=sid,
                challenge=challenge_key,
                agent=agent,
                pr=pr_int,
                branch=branch,
                submission_path=submission_path,
                notes=str(item["notes"]) if "notes" in item else None,
                input_path=str(item["input_path"]) if "input_path" in item else None,
            )
        )

    return challenges, subs


# ----------------------
# Grader snapshot cache
# ----------------------


class GraderCache:
    def __init__(self, tmp_dir: Path, challenges: Dict[str, ChallengeConfig]):
        self.tmp_dir = tmp_dir
        self.challenges = challenges
        self._paths: Dict[str, Optional[Path]] = {}
        self._errors: Dict[str, str] = {}

    def get_grader_path(self, key: str) -> Tuple[Optional[Path], Optional[str]]:
        """Return (path, error) for a grader snapshot.

        On success, (Path, None). On failure, (None, error_message).
        """

        if key in self._paths:
            return self._paths[key], self._errors.get(key)

        cfg = self.challenges.get(key)
        if cfg is None:
            msg = f"unknown challenge key '{key}' in submission config"
            self._paths[key] = None
            self._errors[key] = msg
            return None, msg

        dest = self.tmp_dir / "graders" / f"{key}_grade.py"
        try:
            materialize_blob(cfg.grader_branch, cfg.grader_path, dest)
        except Exception as exc:  # noqa: BLE001
            msg = f"failed to materialize grader from {cfg.grader_branch}:{cfg.grader_path}: {exc}"
            self._paths[key] = None
            self._errors[key] = msg
            return None, msg

        self._paths[key] = dest
        self._errors[key] = None
        return dest, None


# ----------------------
# Per-challenge grading
# ----------------------


def run_subprocess(args: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def grade_trolley(grader: Path, submission: Path) -> Tuple[Optional[int], str, str, Optional[str], Optional[Any]]:
    cmd = [sys.executable, str(grader), str(submission)]
    code, out, err = run_subprocess(cmd)
    if code != 0:
        return None, out, err, "grader-error", None

    m = re.search(r"Final Score:\s*(\d+)/100", out)
    if not m:
        return None, out, err, "parse-error", None
    score = int(m.group(1))
    return score, out, err, None, None


def grade_logic(grader: Path, submission: Path) -> Tuple[Optional[int], str, str, Optional[str], Optional[Any]]:
    cmd = [sys.executable, str(grader), str(submission)]
    code, out, err = run_subprocess(cmd)
    if code != 0:
        return None, out, err, "grader-error", None

    # Take last non-empty line and try to parse as JSON
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if not lines:
        return None, out, err, "parse-error", None
    last = lines[-1]
    try:
        obj = json.loads(last)
    except json.JSONDecodeError:
        return None, out, err, "parse-error", None
    score = obj.get("total_score")
    try:
        score_int = int(score)
    except (TypeError, ValueError):
        return None, out, err, "parse-error", obj
    return score_int, out, err, None, obj


def ensure_supply_input(tmp_dir: Path, cfg: ChallengeConfig) -> Tuple[Optional[Path], Optional[str]]:
    dest = tmp_dir / "inputs" / "supply_hard.json"
    if dest.exists():
        return dest, None
    try:
        materialize_blob(
            cfg.grader_branch,
            "challenges/challenge-14-claude-haiku-4-5/test_cases/hard.json",
            dest,
        )
    except Exception as exc:  # noqa: BLE001
        return None, f"failed to materialize supply hard.json: {exc}"
    return dest, None


def grade_supply(grader: Path, submission: Path, tmp_dir: Path, cfg: ChallengeConfig) -> Tuple[Optional[int], str, str, Optional[str], Optional[Any]]:
    testcase_path, err_msg = ensure_supply_input(tmp_dir, cfg)
    if testcase_path is None:
        return None, "", err_msg or "missing hard.json", "input-missing", None

    cmd = [sys.executable, str(grader), str(submission), str(testcase_path)]
    code, out, err = run_subprocess(cmd)
    if code != 0:
        return None, out, err, "grader-error", None

    m = re.search(r"Score:\s*(\d+)", out)
    if not m:
        return None, out, err, "parse-error", None
    score = int(m.group(1))
    return score, out, err, None, None


def materialize_multi_input(tmp_dir: Path, sub: SubmissionConfig) -> Tuple[Optional[Path], Optional[str]]:
    if not sub.input_path:
        return None, "multi-stage submission missing input_path in config"
    dest = tmp_dir / "inputs" / f"{sub.sid}_input.json"
    try:
        materialize_blob(sub.branch, sub.input_path, dest)
    except Exception as exc:  # noqa: BLE001
        return None, f"failed to materialize multi input from {sub.branch}:{sub.input_path}: {exc}"
    return dest, None


def grade_multi(grader: Path, submission: Path, tmp_dir: Path, sub: SubmissionConfig) -> Tuple[Optional[int], str, str, Optional[str], Optional[Any]]:
    input_path, err_msg = materialize_multi_input(tmp_dir, sub)
    if input_path is None:
        return None, "", err_msg or "input missing", "input-missing", None

    cmd = [
        sys.executable,
        str(grader),
        "--input",
        str(input_path),
        "--submission",
        str(submission),
        "--pretty",
    ]
    code, out, err = run_subprocess(cmd)
    if code != 0:
        return None, out, err, "grader-error", None

    try:
        obj = json.loads(out)
    except json.JSONDecodeError:
        return None, out, err, "parse-error", None

    score = obj.get("total_score")
    try:
        score_int = int(round(float(score)))
    except (TypeError, ValueError):
        return None, out, err, "parse-error", obj
    return score_int, out, err, None, obj


# ----------------------
# Main orchestration
# ----------------------


def build_md_table(results: List[Dict[str, Any]]) -> str:
    def sort_key(r: Dict[str, Any]):
        challenge = str(r.get("challenge") or "")
        score = r.get("score")
        score_key = float("-inf") if score is None else float(score)
        pr = r.get("pr")
        try:
            pr_key = int(pr) if pr is not None else 10**9
        except (TypeError, ValueError):
            pr_key = 10**9
        sid = str(r.get("id") or "")
        # sort: challenge asc, score desc, pr asc, id asc
        return (challenge, -score_key, pr_key, sid)

    rows = sorted(results, key=sort_key)

    header = "| id | challenge | agent | pr | branch | score | status |\n"
    sep = "|---|---|---|---|---|---|---|\n"
    lines = [header, sep]
    for r in rows:
        sid = str(r.get("id") or "")
        ch = str(r.get("challenge") or "")
        agent = str(r.get("agent") or "")
        pr = r.get("pr")
        pr_str = "" if pr is None else str(pr)
        branch = str(r.get("branch") or "")
        score = r.get("score")
        score_str = "" if score is None else str(score)
        status = str(r.get("status") or "")
        lines.append(f"| {sid} | {ch} | {agent} | {pr_str} | {branch} | {score_str} | {status} |\n")
    return "".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run all C14 graders over a curated config of submissions.")
    parser.add_argument("--config", required=True, help="Path to JSON config file.")
    parser.add_argument("--output-json", help="Where to write JSON summary (default: stdout).")
    parser.add_argument("--output-md", help="Optional path to write a Markdown table summary.")
    parser.add_argument(
        "--tmp-dir",
        default=".c14_helper_tmp",
        help="Temporary directory (under repo root) for grader and submission snapshots.",
    )

    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 1

    try:
        challenges, subs = load_config(config_path)
    except SystemExit as exc:
        # Already printed a message; just propagate non-zero exit.
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to load config: {exc}", file=sys.stderr)
        return 1

    tmp_dir = Path(args.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    grader_cache = GraderCache(tmp_dir, challenges)

    results: List[Dict[str, Any]] = []

    for sub_cfg in subs:
        ch_key = sub_cfg.challenge
        ch_meta = challenges.get(ch_key)
        result: Dict[str, Any] = {
            "id": sub_cfg.sid,
            "challenge": ch_key,
            "agent": sub_cfg.agent,
            "pr": sub_cfg.pr,
            "branch": sub_cfg.branch,
            "submission_path": sub_cfg.submission_path,
            "score": None,
            "status": None,
            "error": None,
            "raw_stdout": "",
            "raw_stderr": "",
            "grader_json": None,
            "notes": sub_cfg.notes,
        }

        # Resolve grader snapshot
        grader_path, grader_err = grader_cache.get_grader_path(ch_key)
        if grader_path is None:
            result["status"] = "grader-missing"
            result["error"] = grader_err
            results.append(result)
            continue

        # Materialize submission file
        sub_basename = os.path.basename(sub_cfg.submission_path)
        safe_id = sub_cfg.sid.replace("/", "_")
        dest_sub = tmp_dir / "subs" / f"{safe_id}__{sub_basename}"
        try:
            materialize_blob(sub_cfg.branch, sub_cfg.submission_path, dest_sub)
        except Exception as exc:  # noqa: BLE001
            result["status"] = "submission-missing"
            result["error"] = str(exc)
            results.append(result)
            continue

        # Dispatch to appropriate grader kind
        kind = (ch_meta.kind if ch_meta is not None else "").lower()
        score: Optional[int] = None
        status: str = "ok"
        err_msg: Optional[str] = None
        raw_out = ""
        raw_err = ""
        grader_json: Optional[Any] = None

        try:
            if kind == "trolley":
                score, raw_out, raw_err, err_msg, _ = grade_trolley(grader_path, dest_sub)
            elif kind == "logic":
                score, raw_out, raw_err, err_msg, grader_json = grade_logic(grader_path, dest_sub)
            elif kind == "supply":
                score, raw_out, raw_err, err_msg, _ = grade_supply(grader_path, dest_sub, tmp_dir, ch_meta)
            elif kind == "multi":
                score, raw_out, raw_err, err_msg, grader_json = grade_multi(
                    grader_path,
                    dest_sub,
                    tmp_dir,
                    sub_cfg,
                )
            else:
                status = "grader-missing"
                err_msg = f"unknown challenge kind '{kind}' for {ch_key}"
        except Exception as exc:  # noqa: BLE001
            status = "grader-error"
            err_msg = f"exception while grading: {exc}"

        if err_msg is not None and status == "ok":
            # Kind-specific functions can signal a more precise status.
            if err_msg in {"grader-error", "parse-error", "input-missing"}:
                # Should not happen (we use strings for statuses, not messages),
                # but guard defensively.
                status = err_msg
            else:
                # Map based on context: grade_* helpers already return status
                # through err_msg when score is None; infer type here.
                if score is None:
                    # Heuristic classification
                    if "input" in err_msg.lower():
                        status = "input-missing"
                    elif "parse" in err_msg.lower() or "json" in err_msg.lower():
                        status = "parse-error"
                    else:
                        status = "grader-error"

        if score is None and status == "ok":
            # No explicit error but no score either.
            status = "parse-error"

        result["score"] = score
        result["status"] = status
        result["error"] = err_msg
        result["raw_stdout"] = raw_out
        result["raw_stderr"] = raw_err
        result["grader_json"] = grader_json
        results.append(result)

    summary = {
        "metadata": {
            "script": "scripts/c14_grade_all.py",
            "config_path": str(config_path),
            "tmp_dir": str(tmp_dir),
            "num_submissions": len(results),
        },
        "results": results,
    }

    json_text = json.dumps(summary, indent=2)

    if args.output_json:
        Path(args.output_json).write_text(json_text, encoding="utf-8")
    else:
        print(json_text)

    if args.output_md:
        md = build_md_table(results)
        Path(args.output_md).write_text(md, encoding="utf-8")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
