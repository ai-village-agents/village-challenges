#!/usr/bin/env python3
"""Solver for Challenge #11: GitHub Forensics (Pages + Ghosts)"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_http_status(text: str) -> int:
    """Extract HTTP status code from first line of transcript."""
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    if not m:
        raise ValueError("No HTTP status line found")
    return int(m.group(1))


def parse_json_body(text: str) -> Any:
    """Extract JSON body from HTTP transcript (handle LF/CRLF)."""
    # Split on blank line (may be \r\n\r\n or \n\n)
    m = re.search(r"\r?\n\r?\n", text)
    if not m:
        raise ValueError("No blank line separating headers from body")
    body = text[m.end():]
    return json.loads(body)


def parse_location_header(text: str) -> Optional[str]:
    """Extract Location header from HEAD response."""
    m = re.search(r"^location:\s*(.+?)\s*$", text, flags=re.I | re.M)
    return m.group(1).strip() if m else None


def solve(packet_dir: Path, output_file: Path) -> None:
    """Parse packet and generate report."""
    http_dir = packet_dir / "http"
    
    # Load manifest and expected logins
    with open(packet_dir / "packet_manifest.json") as f:
        manifest = json.load(f)
    
    with open(packet_dir / "expected_logins.json") as f:
        expected_logins = json.load(f)
    
    repos_data: List[Dict[str, Any]] = []
    ghost_accounts: List[Dict[str, str]] = []
    
    # Process each repo
    for repo_name in manifest["repos"]:
        # Load repo metadata
        repos_path = http_dir / f"repos__{repo_name}.http"
        repos_text = repos_path.read_text("utf-8", errors="replace")
        repos_json = parse_json_body(repos_text)
        
        has_pages = bool(repos_json.get("has_pages"))
        default_branch = repos_json.get("default_branch")
        
        # Load pages endpoint
        pages_path = http_dir / f"pages__{repo_name}.http"
        pages_text = pages_path.read_text("utf-8", errors="replace")
        pages_status = parse_http_status(pages_text)
        
        if pages_status == 404:
            pages = {
                "api_status": "not_found",
                "html_url": None,
                "source_branch": None,
                "source_path": None,
            }
        else:
            pages_json = parse_json_body(pages_text)
            source = pages_json.get("source") or {}
            pages = {
                "api_status": pages_json.get("status"),
                "html_url": pages_json.get("html_url"),
                "source_branch": source.get("branch"),
                "source_path": source.get("path"),
            }
        
        # Load public endpoint (HEAD request)
        public_path = http_dir / f"public__{repo_name}.http"
        public_text = public_path.read_text("utf-8", errors="replace")
        public_status = parse_http_status(public_text)
        public_location = parse_location_header(public_text)
        
        public = {
            "url": f"{manifest['public_base']}{repo_name}/",
            "http_status": public_status,
            "location": public_location,
        }
        
        # Compute inconsistency flags
        flags: List[str] = []
        
        if not has_pages and pages_status != 404:
            flags.append("has_pages_false_but_pages_endpoint_ok")
        
        if has_pages and pages_status == 404:
            flags.append("has_pages_true_but_pages_endpoint_404")
        
        if pages.get("api_status") == "built" and public.get("http_status") == 404:
            flags.append("pages_built_but_public_404")
        
        if (pages.get("source_branch") and default_branch and 
            pages["source_branch"] != default_branch):
            flags.append("pages_source_non_default_branch")
        
        # Sort flags
        flags.sort()
        
        repos_data.append({
            "repo": repo_name,
            "has_pages": has_pages,
            "pages": pages,
            "public": public,
            "flags": flags,
        })
    
    # Detect ghost accounts
    for login in expected_logins:
        user_path = http_dir / f"users__{login}.http"
        user_text = user_path.read_text("utf-8", errors="replace")
        user_status = parse_http_status(user_text)
        
        if user_status == 404:
            ghost_accounts.append({
                "login": login,
                "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
            })
    
    # Sort repos by name, ghost_accounts by login
    repos_data.sort(key=lambda x: x["repo"])
    ghost_accounts.sort(key=lambda x: x["login"])
    
    # Build output
    report = {
        "packet_version": "v1",
        "generated_at": "Challenge #11 submission",
        "repos": repos_data,
        "ghost_accounts": ghost_accounts,
    }
    
    # Write output
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Parse GitHub forensics HTTP packet and generate report"
    )
    parser.add_argument("--packet", required=True, help="Path to packet directory")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    
    args = parser.parse_args()
    
    packet_dir = Path(args.packet)
    output_file = Path(args.out)
    
    if not packet_dir.exists():
        print(f"Error: packet directory not found: {packet_dir}", file=sys.stderr)
        sys.exit(1)
    
    try:
        solve(packet_dir, output_file)
        print(f"Report generated: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
