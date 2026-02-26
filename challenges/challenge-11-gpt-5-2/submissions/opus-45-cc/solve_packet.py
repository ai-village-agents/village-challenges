#!/usr/bin/env python3
"""
C11 GitHub Forensics: Pages + Ghosts (Offline Packet) solver
Author: Opus 4.5 (Claude Code)
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path


def parse_http_response(content: str) -> tuple[int, dict, str]:
    """Parse raw HTTP response into status code, headers dict, and body."""
    # Handle both LF and CRLF line endings
    # Split headers from body - look for double newline (empty line)
    parts = re.split(r'\r?\n\r?\n', content, maxsplit=1)
    header_section = parts[0]
    body = parts[1] if len(parts) > 1 else ""
    
    lines = header_section.split('\n')
    # First line is status line: HTTP/X.X STATUS_CODE STATUS_TEXT
    status_line = lines[0].strip()
    match = re.match(r'HTTP/[\d.]+ (\d+)', status_line)
    status_code = int(match.group(1)) if match else 0
    
    # Parse headers
    headers = {}
    for line in lines[1:]:
        line = line.strip().rstrip('\r')
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    return status_code, headers, body.strip()


def parse_json_body(body: str) -> dict:
    """Parse JSON body, return empty dict on failure."""
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def process_repo(packet_dir: Path, repo_name: str, public_base: str) -> dict:
    """Process a single repo and return its report entry."""
    http_dir = packet_dir / "http"
    
    # Read repos endpoint
    repos_file = http_dir / f"repos__{repo_name}.http"
    repos_content = repos_file.read_text() if repos_file.exists() else ""
    repos_status, _, repos_body = parse_http_response(repos_content)
    repos_data = parse_json_body(repos_body)
    
    has_pages = repos_data.get("has_pages", False)
    default_branch = repos_data.get("default_branch", "main")
    
    # Read pages endpoint
    pages_file = http_dir / f"pages__{repo_name}.http"
    pages_content = pages_file.read_text() if pages_file.exists() else ""
    pages_status, _, pages_body = parse_http_response(pages_content)
    pages_data = parse_json_body(pages_body)
    
    # Determine pages info
    if pages_status == 200:
        # Use exact status from the API response
        api_status = pages_data.get("status", "built")
        html_url = pages_data.get("html_url")
        source = pages_data.get("source", {})
        source_branch = source.get("branch")
        source_path = source.get("path")
    else:
        api_status = "not_found"
        html_url = None
        source_branch = None
        source_path = None
    
    # Read public endpoint
    public_file = http_dir / f"public__{repo_name}.http"
    public_content = public_file.read_text() if public_file.exists() else ""
    public_status, public_headers, _ = parse_http_response(public_content)
    
    public_url = f"{public_base}{repo_name}/"
    location = public_headers.get("location")
    
    # Compute flags
    flags = []
    
    # has_pages_false_but_pages_endpoint_ok
    if not has_pages and pages_status == 200:
        flags.append("has_pages_false_but_pages_endpoint_ok")
    
    # has_pages_true_but_pages_endpoint_404
    if has_pages and pages_status == 404:
        flags.append("has_pages_true_but_pages_endpoint_404")
    
    # pages_built_but_public_404 - only applies when status is exactly "built"
    if api_status == "built" and public_status == 404:
        flags.append("pages_built_but_public_404")
    
    # pages_source_non_default_branch
    if source_branch and source_branch != default_branch:
        flags.append("pages_source_non_default_branch")
    
    flags.sort()
    
    # Build pages object
    if api_status == "not_found":
        pages_obj = {
            "api_status": "not_found",
            "html_url": None,
            "source_branch": None,
            "source_path": None
        }
    else:
        pages_obj = {
            "api_status": api_status,
            "html_url": html_url,
            "source_branch": source_branch,
            "source_path": source_path
        }
    
    return {
        "repo": repo_name,
        "has_pages": has_pages,
        "pages": pages_obj,
        "public": {
            "url": public_url,
            "http_status": public_status,
            "location": location
        },
        "flags": flags
    }


def process_users(packet_dir: Path, expected_logins: list) -> list:
    """Process user files and detect ghost accounts."""
    http_dir = packet_dir / "http"
    ghost_accounts = []
    
    for login in expected_logins:
        user_file = http_dir / f"users__{login}.http"
        if not user_file.exists():
            continue
        
        content = user_file.read_text()
        status, _, _ = parse_http_response(content)
        
        if status == 404:
            ghost_accounts.append({
                "login": login,
                "reason": "users endpoint returned 404 but login is listed in expected_logins.json"
            })
    
    ghost_accounts.sort(key=lambda x: x["login"])
    return ghost_accounts


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Forensics packet analyzer for C11 challenge"
    )
    parser.add_argument(
        "--packet",
        required=True,
        help="Path to packet directory"
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output JSON file path"
    )
    args = parser.parse_args()
    
    packet_dir = Path(args.packet)
    
    # Load manifest
    manifest_file = packet_dir / "packet_manifest.json"
    manifest = json.loads(manifest_file.read_text())
    
    repos = manifest.get("repos", [])
    public_base = manifest.get("public_base", "https://ai-village-agents.github.io/")
    
    # Load expected logins
    logins_file = packet_dir / "expected_logins.json"
    expected_logins = json.loads(logins_file.read_text())
    
    # Process repos
    repo_results = []
    for repo_name in repos:
        result = process_repo(packet_dir, repo_name, public_base)
        repo_results.append(result)
    
    repo_results.sort(key=lambda x: x["repo"])
    
    # Process ghost accounts
    ghost_accounts = process_users(packet_dir, expected_logins)
    
    # Build report
    report = {
        "packet_version": "v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repos": repo_results,
        "ghost_accounts": ghost_accounts
    }
    
    # Write output
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()
