#!/usr/bin/env python3
"""Solve Challenge #11: GitHub Forensics Offline Packet.

Parses HTTP transcripts from the offline packet to determine:
1. Which repos have GitHub Pages enabled vs serving
2. Which GitHub accounts appear to be ghost accounts
3. Inconsistency flags for each repo

Usage:
    python solve_packet.py --packet <dir> --out <file>
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_http_status(text: str) -> int:
    """Extract HTTP status code from transcript."""
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    if not m:
        raise ValueError("No HTTP status line found")
    return int(m.group(1))


def parse_json_body(text: str):
    """Extract JSON body from HTTP transcript (after blank line)."""
    m = re.search(r"\r?\n\r?\n", text)
    if not m:
        raise ValueError("No blank line separator found")
    body = text[m.end():]
    return json.loads(body)


def parse_head_status_and_location(text: str):
    """Extract status and Location header from HEAD response."""
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    status = int(m.group(1)) if m else None
    m2 = re.search(r"^location:\s*(.+?)\s*$", text, flags=re.I | re.M)
    loc = m2.group(1).strip() if m2 else None
    return status, loc


def main():
    parser = argparse.ArgumentParser(
        description="Solve Challenge #11: GitHub Forensics Offline Packet"
    )
    parser.add_argument("--packet", required=True, help="Path to packet data directory")
    parser.add_argument("--out", required=True, help="Path to output report.json")
    args = parser.parse_args()

    packet_dir = Path(args.packet)
    http_dir = packet_dir / "http"

    # Load manifest
    manifest = json.loads((packet_dir / "packet_manifest.json").read_text("utf-8"))
    public_base = manifest["public_base"]

    repos_result = []

    for repo in manifest["repos"]:
        # 1. Parse repos endpoint
        repos_text = (http_dir / f"repos__{repo}.http").read_text("utf-8", errors="replace")
        repo_obj = parse_json_body(repos_text)
        has_pages = bool(repo_obj.get("has_pages"))
        default_branch = repo_obj.get("default_branch")

        # 2. Parse pages endpoint
        pages_text = (http_dir / f"pages__{repo}.http").read_text("utf-8", errors="replace")
        pages_status = parse_http_status(pages_text)

        if pages_status == 404:
            pages = {
                "api_status": "not_found",
                "html_url": None,
                "source_branch": None,
                "source_path": None,
            }
        else:
            pages_obj = parse_json_body(pages_text)
            pages = {
                "api_status": pages_obj.get("status"),
                "html_url": pages_obj.get("html_url"),
                "source_branch": (pages_obj.get("source") or {}).get("branch"),
                "source_path": (pages_obj.get("source") or {}).get("path"),
            }

        # 3. Parse public endpoint (HEAD response)
        public_text = (http_dir / f"public__{repo}.http").read_text("utf-8", errors="replace")
        pub_status, pub_loc = parse_head_status_and_location(public_text)

        public = {
            "url": f"{public_base}{repo}/",
            "http_status": pub_status,
            "location": pub_loc,
        }

        # 4. Compute flags
        flags = []
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

        repos_result.append({
            "repo": repo,
            "has_pages": has_pages,
            "pages": pages,
            "public": public,
            "flags": sorted(flags),
        })

    # Sort repos by name
    repos_result.sort(key=lambda r: r["repo"])

    # Ghost detection
    expected_logins = json.loads(
        (packet_dir / "expected_logins.json").read_text("utf-8")
    )
    ghost_accounts = []
    for login in expected_logins:
        user_text = (http_dir / f"users__{login}.http").read_text("utf-8", errors="replace")
        user_status = parse_http_status(user_text)
        if user_status == 404:
            ghost_accounts.append({
                "login": login,
                "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
            })

    ghost_accounts.sort(key=lambda g: g["login"])

    # Build report
    report = {
        "packet_version": "v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repos": repos_result,
        "ghost_accounts": ghost_accounts,
    }

    # Write output
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Report written to {out_path}")
    print(f"  Repos analyzed: {len(repos_result)}")
    print(f"  Ghost accounts: {len(ghost_accounts)}")
    for g in ghost_accounts:
        print(f"    - {g['login']}")


if __name__ == "__main__":
    main()
