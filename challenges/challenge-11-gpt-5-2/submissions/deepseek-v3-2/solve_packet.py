#!/usr/bin/env python3
"""
Challenge #11 GitHub Forensics solver.
Parses HTTP transcripts from packet and produces JSON report.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_json_from_http_transcript(path: Path) -> Any:
    """Parse HTTP response, extract JSON body."""
    text = path.read_text("utf-8", errors="replace")
    # Find blank line separating headers and body
    m = re.search(r"\r?\n\r?\n", text)
    if not m:
        raise ValueError(f"No JSON body found in {path}")
    body = text[m.end():]
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def load_status_from_http_transcript(path: Path) -> int:
    """Extract HTTP status code from first line."""
    text = path.read_text("utf-8", errors="replace")
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    if not m:
        raise ValueError(f"No HTTP status line found in {path}")
    return int(m.group(1))


def load_head_status_and_location(path: Path) -> Tuple[Optional[int], Optional[str]]:
    """Parse HEAD response: status line and Location header."""
    text = path.read_text("utf-8", errors="replace")
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    status = int(m.group(1)) if m else None
    m2 = re.search(r"^location:\s*(.+?)\s*$", text, flags=re.I | re.M)
    loc = m2.group(1).strip() if m2 else None
    return status, loc


def parse_packet(packet_dir: Path) -> Dict[str, Any]:
    """Main parsing logic."""
    http_dir = packet_dir / "http"
    
    # Load manifest
    manifest_path = packet_dir / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    
    repos = []
    for repo_name in manifest["repos"]:
        # Parse repo metadata
        repo_obj = load_json_from_http_transcript(http_dir / f"repos__{repo_name}.http")
        has_pages = bool(repo_obj.get("has_pages"))
        default_branch = repo_obj.get("default_branch")
        
        # Parse /pages endpoint
        pages_path = http_dir / f"pages__{repo_name}.http"
        pages_status = load_status_from_http_transcript(pages_path)
        if pages_status == 404:
            pages = {
                "api_status": "not_found",
                "html_url": None,
                "source_branch": None,
                "source_path": None,
            }
        else:
            pages_obj = load_json_from_http_transcript(pages_path)
            pages = {
                "api_status": pages_obj.get("status"),
                "html_url": pages_obj.get("html_url"),
                "source_branch": (pages_obj.get("source") or {}).get("branch"),
                "source_path": (pages_obj.get("source") or {}).get("path"),
            }
        
        # Parse public HEAD response
        pub_status, pub_loc = load_head_status_and_location(http_dir / f"public__{repo_name}.http")
        public = {
            "url": f"{manifest['public_base']}{repo_name}/",
            "http_status": pub_status,
            "location": pub_loc,
        }
        
        # Compute flags
        flags = []
        if (not has_pages) and pages_status != 404:
            flags.append("has_pages_false_but_pages_endpoint_ok")
        if has_pages and pages_status == 404:
            flags.append("has_pages_true_but_pages_endpoint_404")
        if pages.get("api_status") == "built" and public.get("http_status") == 404:
            flags.append("pages_built_but_public_404")
        if pages.get("source_branch") and default_branch and pages["source_branch"] != default_branch:
            flags.append("pages_source_non_default_branch")
        
        repos.append({
            "repo": repo_name,
            "has_pages": has_pages,
            "pages": pages,
            "public": public,
            "flags": sorted(flags),
        })
    
    # Sort repos by name
    repos.sort(key=lambda r: r["repo"])
    
    # Detect ghost accounts
    expected_logins = json.loads((packet_dir / "expected_logins.json").read_text("utf-8"))
    ghost_accounts = []
    for login in expected_logins:
        user_status = load_status_from_http_transcript(http_dir / f"users__{login}.http")
        if user_status == 404:
            ghost_accounts.append({
                "login": login,
                "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
            })
    
    ghost_accounts.sort(key=lambda g: g["login"])
    
    return {
        "packet_version": manifest.get("packet_version", "v1"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repos": repos,
        "ghost_accounts": ghost_accounts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse GitHub Forensics packet and produce JSON report."
    )
    parser.add_argument(
        "--packet",
        required=True,
        type=Path,
        help="Path to packet directory (contains data/)"
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON file path"
    )
    args = parser.parse_args()
    
    # Validate packet directory
    if not args.packet.exists():
        print(f"Error: packet directory '{args.packet}' does not exist", file=sys.stderr)
        return 1
    
    try:
        report = parse_packet(args.packet)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report written to {args.out}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
