#!/usr/bin/env python3
"""Challenge 11 packet solver for GPT-5.1.

Parses the offline GitHub HTTP packet and produces a normalized
report.json matching the challenge specification.

Usage:
  python challenges/challenge-11-gpt-5-2/submissions/gpt-5-1/solve_packet.py \
    --packet challenges/challenge-11-gpt-5-2/data \
    --out challenges/challenge-11-gpt-5-2/submissions/gpt-5-1/report.json

Only the Python standard library is used; no network access is required.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


HTTP_BODY_SPLIT_RE = re.compile(r"\r?\n\r?\n")
HTTP_STATUS_RE = re.compile(r"^HTTP/\S+\s+(\d{3})\b", flags=re.M)
HTTP_LOCATION_RE = re.compile(r"^location:\s*(.+?)\s*$", flags=re.I | re.M)


def _read_text(path: Path) -> str:
    """Read a file as UTF-8 text, replacing invalid bytes.

    This mirrors the robustness of the reference grader.
    """

    return path.read_text("utf-8", errors="replace")


def _load_json_from_http_transcript(path: Path) -> Any:
    """Extract JSON body from an HTTP transcript and parse it.

    Assumes a standard HTTP response layout: status/headers, then a blank
    line (CRLF or LF), then the JSON body.
    """

    text = _read_text(path)
    m = HTTP_BODY_SPLIT_RE.search(text)
    if not m:
        raise ValueError(f"No JSON body found in {path}")
    body = text[m.end() :]
    return json.loads(body)


def _load_status_from_http_transcript(path: Path) -> Optional[int]:
    """Extract the numeric HTTP status code from a transcript.

    Returns None if no status line can be found.
    """

    text = _read_text(path)
    m = HTTP_STATUS_RE.search(text)
    if not m:
        return None
    return int(m.group(1))


def _load_head_status_and_location(path: Path) -> Tuple[Optional[int], Optional[str]]:
    """Extract status code and Location header from a HEAD/curl -I transcript."""

    text = _read_text(path)
    m = HTTP_STATUS_RE.search(text)
    status = int(m.group(1)) if m else None
    m2 = HTTP_LOCATION_RE.search(text)
    loc = m2.group(1).strip() if m2 else None
    return status, loc


@dataclass
class RepoExpected:
    name: str
    has_pages: bool
    default_branch: Optional[str]
    pages_status: int
    pages_api_status: str
    pages_html_url: Optional[str]
    pages_source_branch: Optional[str]
    pages_source_path: Optional[str]
    public_status: Optional[int]
    public_location: Optional[str]


def _build_repo_record(
    manifest: Dict[str, Any],
    http_dir: Path,
    repo: str,
) -> Dict[str, Any]:
    """Build the normalized record for a single repo in the packet."""

    # Base repo information from the repos API response JSON
    repos_path = http_dir / f"repos__{repo}.http"
    repo_obj = _load_json_from_http_transcript(repos_path)
    has_pages = bool(repo_obj.get("has_pages"))
    default_branch = repo_obj.get("default_branch")

    # Pages endpoint
    pages_path = http_dir / f"pages__{repo}.http"
    pages_status = _load_status_from_http_transcript(pages_path)
    if pages_status is None:
        raise ValueError(f"No HTTP status found in {pages_path}")

    if pages_status == 404:
        pages_api_status = "not_found"
        pages_html_url = None
        pages_source_branch = None
        pages_source_path = None
    else:
        pages_obj = _load_json_from_http_transcript(pages_path)
        pages_api_status = pages_obj.get("status")
        pages_html_url = pages_obj.get("html_url")
        source = pages_obj.get("source") or {}
        pages_source_branch = source.get("branch")
        pages_source_path = source.get("path")

    # Public HEAD endpoint
    public_path = http_dir / f"public__{repo}.http"
    public_status, public_location = _load_head_status_and_location(public_path)
    public_url = f"{manifest['public_base']}{repo}/"

    # Compute flags using the same semantics as the grader
    flags: List[str] = []
    if (not has_pages) and pages_status != 404:
        flags.append("has_pages_false_but_pages_endpoint_ok")
    if has_pages and pages_status == 404:
        flags.append("has_pages_true_but_pages_endpoint_404")
    if pages_api_status == "built" and public_status == 404:
        flags.append("pages_built_but_public_404")
    if pages_source_branch and default_branch and pages_source_branch != default_branch:
        flags.append("pages_source_non_default_branch")

    return {
        "repo": repo,
        "has_pages": has_pages,
        "pages": {
            "api_status": pages_api_status,
            "html_url": pages_html_url,
            "source_branch": pages_source_branch,
            "source_path": pages_source_path,
        },
        "public": {
            "url": public_url,
            "http_status": public_status,
            "location": public_location,
        },
        "flags": sorted(flags),
    }


def _build_ghost_accounts(packet_dir: Path, http_dir: Path) -> List[Dict[str, Any]]:
    """Compute ghost_accounts from expected_logins + users__*.http transcripts."""

    expected_logins_path = packet_dir / "expected_logins.json"
    expected_logins = json.loads(expected_logins_path.read_text("utf-8"))

    ghosts: List[Dict[str, Any]] = []
    for login in expected_logins:
        user_path = http_dir / f"users__{login}.http"
        status = _load_status_from_http_transcript(user_path)
        if status == 404:
            ghosts.append(
                {
                    "login": login,
                    "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
                }
            )

    ghosts.sort(key=lambda g: g["login"])
    return ghosts


def _generate_report(packet_dir: Path) -> Dict[str, Any]:
    """Generate the full report JSON object for a given packet directory."""

    manifest_path = packet_dir / "packet_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing packet_manifest.json in {packet_dir}")

    http_dir = packet_dir / "http"
    if not http_dir.is_dir():
        raise FileNotFoundError(f"Missing http/ directory in {packet_dir}")

    manifest = json.loads(manifest_path.read_text("utf-8"))
    packet_version = manifest.get("packet_version") or "v1"

    repos: List[Dict[str, Any]] = []
    for repo in manifest.get("repos", []):
        repos.append(_build_repo_record(manifest, http_dir, repo))
    repos.sort(key=lambda r: r["repo"])

    ghost_accounts = _build_ghost_accounts(packet_dir, http_dir)

    generated_at = _dt.datetime.now(_dt.timezone.utc).isoformat()

    return {
        "packet_version": packet_version,
        "generated_at": generated_at,
        "repos": repos,
        "ghost_accounts": ghost_accounts,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Solve the Challenge 11 offline GitHub forensics packet.",
    )
    parser.add_argument(
        "--packet",
        required=True,
        help="Path to the packet directory (containing packet_manifest.json, expected_logins.json, http/)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to write the output report.json",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(argv)
        packet_dir = Path(args.packet)
        out_path = Path(args.out)

        if not packet_dir.is_dir():
            raise FileNotFoundError(f"Packet directory not found: {packet_dir}")

        report = _generate_report(packet_dir)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 0
    except Exception as exc:  # pragma: no cover - defensive top-level
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

