#!/usr/bin/env python3
"""
GitHub Forensics: Pages + Ghosts
Parse HTTP packet files and generate JSON report.
Python stdlib only, no network calls.
"""

import argparse
import datetime
import json
import os
import sys
from email.parser import BytesParser
from email import policy
import re

def parse_http_file(filepath):
    """Parse an HTTP response file into status code, headers, and body text.

    The packet captures in this challenge are slightly irregular:
    - Some status lines use a lone LF (HTTP/2.0 ...\\n) while headers use CRLF.
    - The header/body separator is always the first b'\\r\\n\\r\\n'.
    - Bodies should be returned even for non-200 responses.
    """
    with open(filepath, 'rb') as f:
        raw = f.read()

    # Split once at the first blank line separating headers from body.
    head, sep, body_bytes = raw.partition(b'\r\n\r\n')
    if not sep:
        # No separator found; treat everything as headers and leave body empty.
        head, body_bytes = raw, b''

    # Separate the status line (may end with LF or CRLF) from the header block.
    newline_idx = head.find(b'\n')
    if newline_idx == -1:
        status_line_bytes = head
        header_block = b''
    else:
        status_line_bytes = head[:newline_idx]
        header_block = head[newline_idx + 1:]

    status_line_text = status_line_bytes.rstrip(b'\r').decode('utf-8', errors='replace')
    status_match = re.search(r'HTTP/\d+(?:\.\d+)?\s+(\d{3})', status_line_text)
    status_code = int(status_match.group(1)) if status_match else None

    # Parse headers using the HTTP policy; parser expects headers + blank line.
    parser = BytesParser(policy=policy.HTTP)
    header_bytes = header_block + b'\r\n\r\n'
    headers_msg = parser.parsebytes(header_bytes)
    headers = dict(headers_msg.items())

    body_text = body_bytes.decode('utf-8', errors='replace') if body_bytes else ''

    return {
        'status_code': status_code,
        'headers': headers,
        'body': body_text
    }

def parse_repo_http(packet_dir, repo_name):
    """Parse all three HTTP files for a repository."""
    base_path = os.path.join(packet_dir, 'http')
    
    # Parse repo metadata
    repo_file = os.path.join(base_path, f'repos__{repo_name}.http')
    repo_resp = parse_http_file(repo_file)
    repo_json = json.loads(repo_resp['body']) if repo_resp['status_code'] == 200 else {}
    
    # Parse pages endpoint
    pages_file = os.path.join(base_path, f'pages__{repo_name}.http')
    pages_resp = parse_http_file(pages_file)
    pages_json = json.loads(pages_resp['body']) if pages_resp['status_code'] == 200 else None
    
    # Parse public HEAD
    public_file = os.path.join(base_path, f'public__{repo_name}.http')
    public_resp = parse_http_file(public_file)
    
    return {
        'repo': repo_resp,
        'pages': pages_resp,
        'public': public_resp,
        'repo_json': repo_json,
        'pages_json': pages_json
    }

def compute_flags(repo_data):
    """Compute inconsistency flags for a repository."""
    flags = []
    
    repo_json = repo_data['repo_json']
    pages_resp = repo_data['pages']
    pages_json = repo_data['pages_json']
    public_resp = repo_data['public']
    
    has_pages = repo_json.get('has_pages', False)
    default_branch = repo_json.get('default_branch')
    
    # has_pages_false_but_pages_endpoint_ok
    if has_pages == False and pages_resp['status_code'] == 200:
        flags.append('has_pages_false_but_pages_endpoint_ok')
    
    # has_pages_true_but_pages_endpoint_404
    if has_pages == True and pages_resp['status_code'] == 404:
        flags.append('has_pages_true_but_pages_endpoint_404')
    
    # pages_built_but_public_404
    if pages_json and pages_json.get('status') == 'built' and public_resp['status_code'] == 404:
        flags.append('pages_built_but_public_404')
    
    # pages_source_non_default_branch
    if pages_json and pages_json.get('source') and default_branch:
        source_branch = pages_json['source'].get('branch')
        if source_branch and source_branch != default_branch:
            flags.append('pages_source_non_default_branch')
    
    return sorted(flags)

def detect_ghost_accounts(packet_dir, expected_logins):
    """Detect ghost accounts based on 404 responses."""
    ghost_accounts = []
    base_path = os.path.join(packet_dir, 'http')
    
    for login in expected_logins:
        user_file = os.path.join(base_path, f'users__{login}.http')
        if not os.path.exists(user_file):
            continue
            
        resp = parse_http_file(user_file)
        if resp['status_code'] == 404:
            ghost_accounts.append({
                'login': login,
                'reason': 'users endpoint returned 404 but login is listed in expected_logins.json'
            })
    
    return sorted(ghost_accounts, key=lambda x: x['login'])

def generate_report(packet_dir, output_file):
    """Generate the complete JSON report."""
    # Read packet manifest
    manifest_path = os.path.join(packet_dir, 'packet_manifest.json')
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Read expected logins
    logins_path = os.path.join(packet_dir, 'expected_logins.json')
    with open(logins_path, 'r') as f:
        expected_logins = json.load(f)
    
    repos = []
    for repo_name in sorted(manifest['repos']):
        repo_data = parse_repo_http(packet_dir, repo_name)
        
        # Extract required fields
        repo_json = repo_data['repo_json']
        pages_json = repo_data['pages_json']
        pages_resp = repo_data['pages']
        public_resp = repo_data['public']
        
        has_pages = repo_json.get('has_pages', False)
        default_branch = repo_json.get('default_branch')
        
        # Determine pages.api_status
        if pages_resp['status_code'] == 200:
            api_status = pages_json.get('status') if pages_json and pages_json.get('status') else 'not_found'
        elif pages_resp['status_code'] == 404:
            api_status = 'not_found'
        else:
            api_status = 'error'
        
        # Determine pages.source_branch and pages.source_path
        if pages_json and pages_json.get('source'):
            source_branch = pages_json['source'].get('branch')
            source_path = pages_json['source'].get('path')
        else:
            source_branch = None
            source_path = None
        
        # Determine public.http_status
        public_http_status = public_resp['status_code']
        
        # Compute flags
        flags = compute_flags(repo_data)
        
        repo_entry = {
            'repo': repo_name,
            'has_pages': has_pages,
            'pages': {
                'api_status': api_status,
                'source_branch': source_branch,
                'source_path': source_path
            },
            'public': {
                'http_status': public_http_status,
                'location': None  # Not used in this packet
            },
            'flags': flags
        }
        repos.append(repo_entry)
    
    # Detect ghost accounts
    ghost_accounts = detect_ghost_accounts(packet_dir, expected_logins)
    
    # Build final report
    report = {
        'packet_version': manifest['packet_version'],
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'repos': repos,
        'ghost_accounts': ghost_accounts
    }
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    parser = argparse.ArgumentParser(
        description='Parse GitHub Pages forensics packet and generate JSON report.'
    )
    parser.add_argument(
        '--packet',
        required=True,
        help='Directory containing packet data (should have http/, packet_manifest.json, expected_logins.json)'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Output JSON file path'
    )
    args = parser.parse_args()
    
    if not os.path.isdir(args.packet):
        print(f"Error: Packet directory '{args.packet}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    try:
        generate_report(args.packet, args.out)
        print(f"Successfully generated report: {args.out}")
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
