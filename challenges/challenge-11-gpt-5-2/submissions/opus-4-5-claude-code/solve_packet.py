#!/usr/bin/env python3
"""
solve_packet.py - GitHub Forensics: Pages + Ghosts (Offline Packet)
Challenge #11 solution by Opus 4.5 (Claude Code)

Parses raw HTTP response files to generate a report about GitHub Pages status
and ghost accounts.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_http_response(content):
    """Parse raw HTTP response into status code, headers dict, and body."""
    # Handle both LF and CRLF line endings
    content = content.replace('\r\n', '\n')

    # Split headers from body
    parts = content.split('\n\n', 1)
    header_section = parts[0]
    body = parts[1] if len(parts) > 1 else ''

    lines = header_section.split('\n')

    # Parse status line
    status_line = lines[0]
    # Match "HTTP/2.0 200 OK" or "HTTP/2 404 Not Found"
    match = re.match(r'HTTP/[\d.]+ (\d+)', status_line)
    status_code = int(match.group(1)) if match else 0

    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()

    return status_code, headers, body


def load_http_file(filepath):
    """Load and parse an HTTP response file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_http_response(content)
    except FileNotFoundError:
        return None, None, None


def process_repo(data_dir, repo_name):
    """Process a single repo and return its report entry."""
    http_dir = data_dir / 'http'

    # Load repo endpoint
    repos_file = http_dir / f'repos__{repo_name}.http'
    repos_status, repos_headers, repos_body = load_http_file(repos_file)

    if repos_status is None or repos_status != 200:
        return None

    repo_data = json.loads(repos_body)
    has_pages = repo_data.get('has_pages', False)
    default_branch = repo_data.get('default_branch', 'main')

    # Load pages endpoint
    pages_file = http_dir / f'pages__{repo_name}.http'
    pages_status, pages_headers, pages_body = load_http_file(pages_file)

    pages_info = {
        'api_status': 'not_found',
        'html_url': None,
        'source_branch': None,
        'source_path': None
    }

    if pages_status == 200 and pages_body:
        try:
            pages_data = json.loads(pages_body)
            # api_status uses the actual status field value from the response
            pages_info['api_status'] = pages_data.get('status', 'built')
            pages_info['html_url'] = pages_data.get('html_url')
            source = pages_data.get('source', {})
            pages_info['source_branch'] = source.get('branch')
            pages_info['source_path'] = source.get('path')
        except json.JSONDecodeError:
            pass

    # Load public endpoint
    public_file = http_dir / f'public__{repo_name}.http'
    public_status, public_headers, public_body = load_http_file(public_file)

    public_info = {
        'url': f'https://ai-village-agents.github.io/{repo_name}/',
        'http_status': public_status if public_status else 404,
        'location': public_headers.get('location') if public_headers else None
    }

    # Compute flags
    flags = []

    # has_pages_false_but_pages_endpoint_ok
    if not has_pages and pages_status == 200:
        flags.append('has_pages_false_but_pages_endpoint_ok')

    # has_pages_true_but_pages_endpoint_404
    if has_pages and pages_status == 404:
        flags.append('has_pages_true_but_pages_endpoint_404')

    # pages_built_but_public_404
    if pages_info['api_status'] == 'built' and public_status == 404:
        flags.append('pages_built_but_public_404')

    # pages_source_non_default_branch
    if pages_info['source_branch'] and pages_info['source_branch'] != default_branch:
        flags.append('pages_source_non_default_branch')

    flags.sort()

    return {
        'repo': repo_name,
        'has_pages': has_pages,
        'pages': pages_info,
        'public': public_info,
        'flags': flags
    }


def find_ghost_accounts(data_dir, expected_logins):
    """Find ghost accounts from user endpoint files."""
    http_dir = data_dir / 'http'
    ghosts = []

    for login in expected_logins:
        user_file = http_dir / f'users__{login}.http'
        status, headers, body = load_http_file(user_file)

        if status == 404:
            ghosts.append({
                'login': login,
                'reason': 'users endpoint returned 404 but login is listed in expected_logins.json'
            })

    # Sort by login
    ghosts.sort(key=lambda x: x['login'])
    return ghosts


def main():
    parser = argparse.ArgumentParser(
        description='GitHub Forensics: Parse offline HTTP packet to analyze Pages and ghost accounts'
    )
    parser.add_argument('--packet', required=True, help='Path to packet data directory')
    parser.add_argument('--out', required=True, help='Path to output report.json')

    args = parser.parse_args()

    data_dir = Path(args.packet)
    http_dir = data_dir / 'http'

    if not http_dir.exists():
        print(f"Error: HTTP directory not found at {http_dir}", file=sys.stderr)
        sys.exit(1)

    # Load expected logins
    expected_logins_file = data_dir / 'expected_logins.json'
    with open(expected_logins_file, 'r') as f:
        expected_logins = json.load(f)

    # Find all repo names from repos__ files
    repo_names = []
    for filename in os.listdir(http_dir):
        if filename.startswith('repos__') and filename.endswith('.http'):
            repo_name = filename[7:-5]  # Remove 'repos__' prefix and '.http' suffix
            repo_names.append(repo_name)

    # Process repos
    repos = []
    for repo_name in sorted(repo_names):
        repo_info = process_repo(data_dir, repo_name)
        if repo_info:
            repos.append(repo_info)

    # Find ghost accounts
    ghost_accounts = find_ghost_accounts(data_dir, expected_logins)

    # Build report
    report = {
        'packet_version': 'v1',
        'generated_at': datetime.now().isoformat(),
        'repos': repos,
        'ghost_accounts': ghost_accounts
    }

    # Write output
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report generated: {out_path}")
    print(f"  Repos analyzed: {len(repos)}")
    print(f"  Ghost accounts found: {len(ghost_accounts)}")


if __name__ == '__main__':
    main()
