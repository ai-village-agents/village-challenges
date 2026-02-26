#!/usr/bin/env python3
"""Generate report.json for Challenge 11 by replaying the reference grader logic."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PACKET_VERSION = "v1"
REPORT_FILENAME = "report.json"


def _load_json_from_http_transcript(path: Path) -> Any:
    text = path.read_text("utf-8", errors="replace")
    match = re.search(r"\r?\n\r?\n", text)
    if not match:
        raise ValueError(f"Could not locate JSON body separator in {path}")
    body = text[match.end() :]
    return json.loads(body)


def _load_status_from_http_transcript(path: Path) -> int:
    text = path.read_text("utf-8", errors="replace")
    match = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    if not match:
        raise ValueError(f"Could not locate HTTP status line in {path}")
    return int(match.group(1))


def _load_head_status_and_location(path: Path) -> Tuple[Optional[int], Optional[str]]:
    text = path.read_text("utf-8", errors="replace")
    status_match = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    status = int(status_match.group(1)) if status_match else None
    location_match = re.search(r"^location:\s*(.+?)\s*$", text, flags=re.I | re.M)
    location = location_match.group(1).strip() if location_match else None
    return status, location


def _build_repo_entry(repo: str, packet_dir: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
    http_dir = packet_dir / "http"

    repo_obj = _load_json_from_http_transcript(http_dir / f"repos__{repo}.http")
    has_pages = bool(repo_obj.get("has_pages"))
    default_branch = repo_obj.get("default_branch")

    pages_path = http_dir / f"pages__{repo}.http"
    pages_status = _load_status_from_http_transcript(pages_path)
    if pages_status == 404:
        pages = {
            "api_status": "not_found",
            "html_url": None,
            "source_branch": None,
            "source_path": None,
        }
    else:
        pages_obj = _load_json_from_http_transcript(pages_path)
        pages = {
            "api_status": pages_obj.get("status"),
            "html_url": pages_obj.get("html_url"),
            "source_branch": (pages_obj.get("source") or {}).get("branch"),
            "source_path": (pages_obj.get("source") or {}).get("path"),
        }

    pub_status, pub_location = _load_head_status_and_location(http_dir / f"public__{repo}.http")
    public = {
        "url": f"{manifest['public_base']}{repo}/",
        "http_status": pub_status,
        "location": pub_location,
    }

    flags: List[str] = []
    if (not has_pages) and pages_status != 404:
        flags.append("has_pages_false_but_pages_endpoint_ok")
    if has_pages and pages_status == 404:
        flags.append("has_pages_true_but_pages_endpoint_404")
    if pages.get("api_status") == "built" and public.get("http_status") == 404:
        flags.append("pages_built_but_public_404")
    if (
        pages.get("source_branch")
        and default_branch
        and pages["source_branch"] != default_branch
    ):
        flags.append("pages_source_non_default_branch")

    return {
        "repo": repo,
        "has_pages": has_pages,
        "default_branch": default_branch,
        "pages": pages,
        "public": public,
        "flags": sorted(flags),
    }


def _build_ghost_accounts(packet_dir: Path) -> List[Dict[str, str]]:
    http_dir = packet_dir / "http"
    expected_logins = json.loads((packet_dir / "expected_logins.json").read_text("utf-8"))
    ghosts: List[Dict[str, str]] = []
    for login in expected_logins:
        status = _load_status_from_http_transcript(http_dir / f"users__{login}.http")
        if status == 404:
            ghosts.append(
                {
                    "login": login,
                    "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
                }
            )
    ghosts.sort(key=lambda item: item["login"])
    return ghosts


def _generate_report(packet_dir: Path) -> Dict[str, Any]:
    manifest = json.loads((packet_dir / "packet_manifest.json").read_text("utf-8"))

    repos = sorted(
        (
            _build_repo_entry(repo, packet_dir, manifest)
            for repo in manifest.get("repos", [])
        ),
        key=lambda item: item["repo"],
    )

    return {
        "packet_version": PACKET_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repos": repos,
        "ghost_accounts": _build_ghost_accounts(packet_dir),
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    packet_dir = base_dir / "data"
    if not packet_dir.is_dir():
        raise SystemExit(f"Packet directory not found at {packet_dir}")

    report = _generate_report(packet_dir)
    output_path = base_dir / REPORT_FILENAME
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
