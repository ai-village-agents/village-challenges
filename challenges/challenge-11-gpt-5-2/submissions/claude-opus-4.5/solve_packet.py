#!/usr/bin/env python3
"""
Challenge 11: GitHub Forensics Packet Parser
Author: Claude Opus 4.5

Parses offline HTTP response files to generate a forensics report
detecting Pages configuration inconsistencies and ghost accounts.
"""

import argparse
import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any


def parse_http_response(content: str) -> Dict[str, Any]:
    """
    Parse a raw HTTP response from a .http file.
    Handles both LF and CRLF line endings.
    """
    # Split headers from body - body starts after blank line
    if '\r\n\r\n' in content:
        header_section, body = content.split('\r\n\r\n', 1)
        lines = header_section.split('\r\n')
    elif '\n\n' in content:
        header_section, body = content.split('\n\n', 1)
        lines = header_section.split('\n')
    else:
        lines = content.replace('\r\n', '\n').split('\n')
        body = ''
    
    lines = [line.rstrip('\r') for line in lines]
    
    # Parse status line
    status_line = lines[0] if lines else ''
    status_match = re.match(r'HTTP/[\d.]+\s+(\d+)\s*(.*)', status_line)
    
    if status_match:
        status_code = int(status_match.group(1))
        status_text = status_match.group(2).strip()
    else:
        status_code = 0
        status_text = ''
    
    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    # Try to parse body as JSON
    json_body = None
    if body.strip():
        try:
            json_body = json.loads(body.strip())
        except json.JSONDecodeError:
            pass
    
    return {
        'status_code': status_code,
        'status_text': status_text,
        'headers': headers,
        'body': body.strip(),
        'json_body': json_body
    }


def parse_http_file(filepath: str) -> Dict[str, Any]:
    """Read and parse an HTTP response from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_http_response(content)


def extract_field(json_body: Optional[Dict], field: str, default=None):
    """Safely extract a nested field using dot notation."""
    if json_body is None:
        return default
    
    parts = field.split('.')
    current = json_body
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    
    return current


def get_repos_from_manifest(packet_dir: str) -> list:
    """Read repo list from packet_manifest.json."""
    manifest_path = os.path.join(packet_dir, 'packet_manifest.json')
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    return manifest.get('repos', [])


def get_expected_logins(packet_dir: str) -> list:
    """Read expected logins from expected_logins.json."""
    logins_path = os.path.join(packet_dir, 'expected_logins.json')
    with open(logins_path, 'r') as f:
        return json.load(f)


def analyze_repo(packet_dir: str, repo_name: str) -> dict:
    """Analyze a single repo by parsing its HTTP response files."""
    http_dir = os.path.join(packet_dir, 'http')
    
    # Parse repos endpoint
    repos_file = os.path.join(http_dir, f'repos__{repo_name}.http')
    repos_data = parse_http_file(repos_file)
    repos_json = repos_data['json_body'] or {}
    
    has_pages = repos_json.get('has_pages', False)
    default_branch = repos_json.get('default_branch', 'main')
    
    # Parse pages endpoint
    pages_file = os.path.join(http_dir, f'pages__{repo_name}.http')
    pages_data = parse_http_file(pages_file)
    pages_json = pages_data['json_body'] or {}
    pages_status = pages_data['status_code']
    
    # Determine pages API status
    if pages_status == 404:
        api_status = 'not_found'
        pages_info = {
            'api_status': api_status,
            'html_url': None,
            'source_branch': None,
            'source_path': None
        }
    else:
        api_status = pages_json.get('status', 'unknown')
        pages_info = {
            'api_status': api_status,
            'html_url': pages_json.get('html_url'),
            'source_branch': extract_field(pages_json, 'source.branch'),
            'source_path': extract_field(pages_json, 'source.path')
        }
    
    # Parse public endpoint
    public_file = os.path.join(http_dir, f'public__{repo_name}.http')
    public_data = parse_http_file(public_file)
    
    public_url = f'https://ai-village-agents.github.io/{repo_name}/'
    public_info = {
        'url': public_url,
        'http_status': public_data['status_code'],
        'location': public_data['headers'].get('location')
    }
    
    # Compute inconsistency flags
    flags = []
    
    if not has_pages and pages_status != 404:
        flags.append('has_pages_false_but_pages_endpoint_ok')
    
    if has_pages and pages_status == 404:
        flags.append('has_pages_true_but_pages_endpoint_404')
    
    if api_status == 'built' and public_data['status_code'] == 404:
        flags.append('pages_built_but_public_404')
    
    source_branch = pages_info.get('source_branch')
    if source_branch is not None and source_branch != default_branch:
        flags.append('pages_source_non_default_branch')
    
    flags.sort()
    
    return {
        'repo': repo_name,
        'has_pages': has_pages,
        'pages': pages_info,
        'public': public_info,
        'flags': flags
    }


def analyze_ghost_accounts(packet_dir: str, expected_logins: list) -> list:
    """Check each expected login for ghost account status (404 on /users)."""
    http_dir = os.path.join(packet_dir, 'http')
    ghosts = []
    
    for login in expected_logins:
        user_file = os.path.join(http_dir, f'users__{login}.http')
        if os.path.exists(user_file):
            user_data = parse_http_file(user_file)
            if user_data['status_code'] == 404:
                ghosts.append({
                    'login': login,
                    'reason': 'users endpoint returned 404 but login is listed in expected_logins.json'
                })
    
    ghosts.sort(key=lambda x: x['login'])
    return ghosts


def generate_report(packet_dir: str) -> dict:
    """Generate the full forensics report from the packet directory."""
    repos = get_repos_from_manifest(packet_dir)
    expected_logins = get_expected_logins(packet_dir)
    
    repo_reports = [analyze_repo(packet_dir, repo) for repo in repos]
    repo_reports.sort(key=lambda x: x['repo'])
    
    ghosts = analyze_ghost_accounts(packet_dir, expected_logins)
    
    return {
        'packet_version': 'v1',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'repos': repo_reports,
        'ghost_accounts': ghosts
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate C11 forensics report from HTTP packet directory'
    )
    parser.add_argument('--packet', required=True, help='Path to packet data directory')
    parser.add_argument('--out', required=True, help='Output path for report.json')
    
    args = parser.parse_args()
    
    report = generate_report(args.packet)
    
    with open(args.out, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report generated: {args.out}")


if __name__ == '__main__':
    main()
