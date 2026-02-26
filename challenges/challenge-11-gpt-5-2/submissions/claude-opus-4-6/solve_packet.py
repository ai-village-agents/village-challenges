#!/usr/bin/env python3
"""Solve Challenge 11: GitHub Forensics — Pages + Ghosts (Offline Packet)"""
import argparse
import json
import re
import os
from datetime import datetime

def parse_http_response(filepath):
    """Parse a raw HTTP response file, returning (status_code, headers_dict, body_str)."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Split headers from body - handle both \r\n\r\n and \n\n
    parts = re.split(r'\r?\n\r?\n', content, maxsplit=1)
    header_block = parts[0]
    body = parts[1] if len(parts) > 1 else ''
    
    lines = header_block.split('\n')
    # First line is status line
    status_line = lines[0].strip().rstrip('\r')
    status_match = re.search(r'(\d{3})', status_line)
    status_code = int(status_match.group(1)) if status_match else 0
    
    headers = {}
    for line in lines[1:]:
        line = line.strip().rstrip('\r')
        if ':' in line:
            key, val = line.split(':', 1)
            headers[key.strip().lower()] = val.strip()
    
    return status_code, headers, body.strip()

def parse_json_body(body):
    """Try to parse JSON from body."""
    try:
        return json.loads(body)
    except (json.JSONDecodeError, ValueError):
        return None

def main():
    parser = argparse.ArgumentParser(description='Solve C11 GitHub Forensics packet')
    parser.add_argument('--packet', required=True, help='Path to packet data directory')
    parser.add_argument('--out', required=True, help='Output JSON report path')
    args = parser.parse_args()
    
    http_dir = os.path.join(args.packet, 'http')
    
    # Load manifest
    with open(os.path.join(args.packet, 'packet_manifest.json')) as f:
        manifest = json.load(f)
    
    # Load expected logins
    with open(os.path.join(args.packet, 'expected_logins.json')) as f:
        expected_logins = json.load(f)
    
    repos = []
    for repo_name in sorted(manifest['repos']):
        # Parse repos endpoint
        repo_file = os.path.join(http_dir, f'repos__{repo_name}.http')
        repo_status, repo_headers, repo_body = parse_http_response(repo_file)
        repo_data = parse_json_body(repo_body)
        
        has_pages = repo_data.get('has_pages', False) if repo_data else False
        default_branch = repo_data.get('default_branch', 'main') if repo_data else 'main'
        
        # Parse pages endpoint
        pages_file = os.path.join(http_dir, f'pages__{repo_name}.http')
        pages_status, pages_headers, pages_body = parse_http_response(pages_file)
        pages_data = parse_json_body(pages_body)
        
        if pages_status == 404:
            api_status = 'not_found'
            html_url = None
            source_branch = None
            source_path = None
        else:
            api_status = pages_data.get('status', 'built') if pages_data else 'built'
            html_url = pages_data.get('html_url') if pages_data else None
            source = pages_data.get('source', {}) if pages_data else {}
            source_branch = source.get('branch') if source else None
            source_path = source.get('path') if source else None
        
        # Parse public endpoint
        public_file = os.path.join(http_dir, f'public__{repo_name}.http')
        pub_status, pub_headers, pub_body = parse_http_response(public_file)
        pub_location = pub_headers.get('location', None)
        pub_url = f"https://ai-village-agents.github.io/{repo_name}/"
        
        # Compute flags
        flags = []
        if not has_pages and api_status != 'not_found':
            flags.append('has_pages_false_but_pages_endpoint_ok')
        if has_pages and api_status == 'not_found':
            flags.append('has_pages_true_but_pages_endpoint_404')
        if api_status == 'built' and pub_status == 404:
            flags.append('pages_built_but_public_404')
        if source_branch and source_branch != default_branch:
            flags.append('pages_source_non_default_branch')
        flags.sort()
        
        repo_entry = {
            'repo': repo_name,
            'has_pages': has_pages,
            'pages': {
                'api_status': api_status,
                'html_url': html_url,
                'source_branch': source_branch,
                'source_path': source_path,
            },
            'public': {
                'url': pub_url,
                'http_status': pub_status,
                'location': pub_location if pub_location else None,
            },
            'flags': flags,
        }
        repos.append(repo_entry)
    
    # Ghost detection
    ghost_accounts = []
    for login in sorted(expected_logins):
        user_file = os.path.join(http_dir, f'users__{login}.http')
        if os.path.exists(user_file):
            user_status, _, _ = parse_http_response(user_file)
            if user_status == 404:
                ghost_accounts.append({
                    'login': login,
                    'reason': 'users endpoint returned 404 but login is listed in expected_logins.json'
                })
    
    report = {
        'packet_version': 'v1',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'repos': repos,
        'ghost_accounts': ghost_accounts,
    }
    
    with open(args.out, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report written to {args.out}")
    print(f"  Repos: {len(repos)}")
    print(f"  Ghosts: {len(ghost_accounts)}")

if __name__ == '__main__':
    main()
