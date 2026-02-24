#!/usr/bin/env python3
"""
Challenge #11 Solver: GitHub Forensics - Pages + Ghosts
Author: Claude Opus 4.5
Parses offline HTTP packet data to analyze GitHub Pages status and detect ghost accounts.
"""

import argparse
import json
import os
import re
from datetime import datetime


def parse_http_response(content):
    """Parse an HTTP response file, handling both LF and CRLF line endings."""
    # Normalize line endings and split headers from body
    # Headers end with double newline (either \r\n\r\n or \n\n)
    if '\r\n\r\n' in content:
        header_section, body = content.split('\r\n\r\n', 1)
    elif '\n\n' in content:
        header_section, body = content.split('\n\n', 1)
    else:
        header_section = content
        body = ''
    
    # Parse status line
    lines = header_section.replace('\r\n', '\n').split('\n')
    status_line = lines[0] if lines else ''
    
    # Extract HTTP status code
    status_match = re.search(r'HTTP/[\d.]+ (\d+)', status_line)
    status_code = int(status_match.group(1)) if status_match else 0
    
    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.lower().strip()] = value.strip()
    
    # Parse JSON body if present
    json_data = None
    body = body.strip()
    if body and body.startswith('{'):
        try:
            json_data = json.loads(body)
        except json.JSONDecodeError:
            pass
    
    return {
        'status_code': status_code,
        'headers': headers,
        'body': body,
        'json': json_data
    }


def get_repos_from_packet(http_dir):
    """Discover all repos from packet directory based on repos__*.http files."""
    repos = []
    for filename in os.listdir(http_dir):
        if filename.startswith('repos__') and filename.endswith('.http'):
            repo_name = filename[7:-5]  # Strip 'repos__' prefix and '.http' suffix
            repos.append(repo_name)
    return sorted(repos)


def process_repo(repo_name, http_dir):
    """Process a single repo and return its report entry."""
    # Read repos file
    repos_file = os.path.join(http_dir, f'repos__{repo_name}.http')
    with open(repos_file, 'r', encoding='utf-8') as f:
        repos_response = parse_http_response(f.read())
    
    repos_json = repos_response['json']
    has_pages = repos_json.get('has_pages', False) if repos_json else False
    default_branch = repos_json.get('default_branch', 'main') if repos_json else 'main'
    
    # Read pages file
    pages_file = os.path.join(http_dir, f'pages__{repo_name}.http')
    with open(pages_file, 'r', encoding='utf-8') as f:
        pages_response = parse_http_response(f.read())
    
    pages_status_code = pages_response['status_code']
    pages_json = pages_response['json']
    
    # Determine pages.api_status
    if pages_status_code == 404:
        api_status = 'not_found'
        pages_data = {
            'api_status': api_status,
            'html_url': None,
            'source_branch': None,
            'source_path': None
        }
    else:
        api_status = pages_json.get('status', 'built') if pages_json else 'built'
        source = pages_json.get('source', {}) if pages_json else {}
        pages_data = {
            'api_status': api_status,
            'html_url': pages_json.get('html_url') if pages_json else None,
            'source_branch': source.get('branch'),
            'source_path': source.get('path')
        }
    
    # Read public file
    public_file = os.path.join(http_dir, f'public__{repo_name}.http')
    with open(public_file, 'r', encoding='utf-8') as f:
        public_response = parse_http_response(f.read())
    
    public_status = public_response['status_code']
    location = public_response['headers'].get('location')
    
    public_data = {
        'url': f'https://ai-village-agents.github.io/{repo_name}/',
        'http_status': public_status,
        'location': location
    }
    
    # Compute flags
    flags = []
    
    # has_pages_false_but_pages_endpoint_ok
    if not has_pages and pages_status_code != 404:
        flags.append('has_pages_false_but_pages_endpoint_ok')
    
    # has_pages_true_but_pages_endpoint_404
    if has_pages and pages_status_code == 404:
        flags.append('has_pages_true_but_pages_endpoint_404')
    
    # pages_built_but_public_404
    if api_status == 'built' and public_status == 404:
        flags.append('pages_built_but_public_404')
    
    # pages_source_non_default_branch
    if pages_data['source_branch'] is not None and pages_data['source_branch'] != default_branch:
        flags.append('pages_source_non_default_branch')
    
    flags.sort()
    
    return {
        'repo': repo_name,
        'has_pages': has_pages,
        'pages': pages_data,
        'public': public_data,
        'flags': flags
    }


def detect_ghost_accounts(http_dir, expected_logins):
    """Detect ghost accounts (404 on /users endpoint but in expected_logins)."""
    ghosts = []
    
    for login in expected_logins:
        users_file = os.path.join(http_dir, f'users__{login}.http')
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                response = parse_http_response(f.read())
            
            if response['status_code'] == 404:
                ghosts.append({
                    'login': login,
                    'reason': 'users endpoint returned 404 but login is listed in expected_logins.json'
                })
    
    # Sort by login
    ghosts.sort(key=lambda x: x['login'])
    return ghosts


def main():
    parser = argparse.ArgumentParser(
        description='Challenge #11 Solver: GitHub Forensics - Pages + Ghosts',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--packet', required=True, help='Path to packet data directory')
    parser.add_argument('--out', required=True, help='Path for output JSON report')
    
    args = parser.parse_args()
    
    packet_dir = args.packet
    http_dir = os.path.join(packet_dir, 'http')
    
    # Load expected logins
    expected_logins_file = os.path.join(packet_dir, 'expected_logins.json')
    with open(expected_logins_file, 'r', encoding='utf-8') as f:
        expected_logins = json.load(f)
    
    # Process all repos
    repos = get_repos_from_packet(http_dir)
    repo_reports = []
    for repo_name in repos:
        repo_reports.append(process_repo(repo_name, http_dir))
    
    # Detect ghost accounts
    ghost_accounts = detect_ghost_accounts(http_dir, expected_logins)
    
    # Build final report
    report = {
        'packet_version': 'v1',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'repos': repo_reports,
        'ghost_accounts': ghost_accounts
    }
    
    # Write output
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f'Report written to {args.out}')
    print(f'Processed {len(repos)} repos, found {len(ghost_accounts)} ghost accounts')


if __name__ == '__main__':
    main()
