#!/usr/bin/env python3
"""
Challenge #11 — GitHub Forensics: Pages + Ghosts (Offline Packet)
Solver script (stdlib only, no network calls required).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_http_file(path: Path) -> Tuple[int, Dict[str, str], str]:
    """Parse a raw HTTP response file.
    Returns (status_code, headers_dict, body_string).
    Handles both CRLF and LF line endings.
    """
    raw = path.read_bytes()
    # Normalise CRLF → LF so we can split uniformly
    raw = raw.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    text = raw.decode('utf-8', errors='replace')

    # Split headers from body on first blank line
    if '\n\n' in text:
        header_section, body = text.split('\n\n', 1)
    else:
        header_section = text
        body = ''

    lines = header_section.strip().split('\n')
    # Status line: "HTTP/2.0 200 OK" or "HTTP/2 404 "
    status_line = lines[0] if lines else ''
    m = re.match(r'^HTTP/\S+\s+(\d{3})', status_line)
    status_code = int(m.group(1)) if m else 0

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip().lower()] = v.strip()

    return status_code, headers, body.strip()


def load_json_body(path: Path) -> Any:
    """Parse a raw HTTP response and return the JSON body."""
    status, _, body = parse_http_file(path)
    return json.loads(body)


def solve(packet_dir: Path, out_file: Path) -> None:
    http_dir = packet_dir / 'http'
    manifest = json.loads((packet_dir / 'packet_manifest.json').read_text('utf-8'))
    public_base: str = manifest['public_base']
    repo_names: List[str] = manifest['repos']

    repos_out: List[Dict[str, Any]] = []

    for repo in repo_names:
        # --- repos endpoint ---
        repo_obj = load_json_body(http_dir / f'repos__{repo}.http')
        has_pages: bool = bool(repo_obj.get('has_pages'))
        default_branch: Optional[str] = repo_obj.get('default_branch')

        # --- pages endpoint ---
        pages_path = http_dir / f'pages__{repo}.http'
        pages_status, _, pages_body = parse_http_file(pages_path)

        if pages_status == 404:
            pages: Dict[str, Any] = {
                'api_status': 'not_found',
                'html_url': None,
                'source_branch': None,
                'source_path': None,
            }
        else:
            pages_obj = json.loads(pages_body)
            pages = {
                'api_status': pages_obj.get('status'),
                'html_url': pages_obj.get('html_url'),
                'source_branch': (pages_obj.get('source') or {}).get('branch'),
                'source_path': (pages_obj.get('source') or {}).get('path'),
            }

        # --- public URL endpoint ---
        pub_path = http_dir / f'public__{repo}.http'
        pub_status, pub_headers, _ = parse_http_file(pub_path)
        location = pub_headers.get('location') or None  # keep None if absent/empty

        public: Dict[str, Any] = {
            'url': f'{public_base}{repo}/',
            'http_status': pub_status,
            'location': location,
        }

        # --- flags ---
        flags: List[str] = []

        # has_pages=False but /pages endpoint is NOT 404
        if (not has_pages) and pages_status != 404:
            flags.append('has_pages_false_but_pages_endpoint_ok')

        # has_pages=True but /pages endpoint IS 404
        if has_pages and pages_status == 404:
            flags.append('has_pages_true_but_pages_endpoint_404')

        # pages says built but public is 404
        if pages.get('api_status') == 'built' and pub_status == 404:
            flags.append('pages_built_but_public_404')

        # pages source branch differs from repo default branch
        src_branch = pages.get('source_branch')
        if src_branch and default_branch and src_branch != default_branch:
            flags.append('pages_source_non_default_branch')

        flags = sorted(flags)

        repos_out.append({
            'repo': repo,
            'has_pages': has_pages,
            'pages': pages,
            'public': public,
            'flags': flags,
        })

    # Sort repos by name ascending
    repos_out.sort(key=lambda r: r['repo'])

    # --- ghost accounts ---
    expected_logins: List[str] = json.loads(
        (packet_dir / 'expected_logins.json').read_text('utf-8')
    )
    ghost_accounts: List[Dict[str, str]] = []
    for login in expected_logins:
        user_path = http_dir / f'users__{login}.http'
        user_status, _, _ = parse_http_file(user_path)
        if user_status == 404:
            ghost_accounts.append({
                'login': login,
                'reason': (
                    'users endpoint returned 404 but login is listed in expected_logins.json'
                ),
            })
    ghost_accounts.sort(key=lambda g: g['login'])

    report = {
        'packet_version': 'v1',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'repos': repos_out,
        'ghost_accounts': ghost_accounts,
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Report written to {out_file}')
    print(f'Repos: {len(repos_out)}, Ghost accounts: {len(ghost_accounts)}')


def main() -> int:
    ap = argparse.ArgumentParser(
        description='Challenge #11 GitHub Forensics solver — offline packet parser'
    )
    ap.add_argument('--packet', required=True, help='Path to the data/ packet directory')
    ap.add_argument('--out', required=True, help='Output path for report.json')
    args = ap.parse_args()

    packet_dir = Path(args.packet)
    out_file = Path(args.out)

    if not packet_dir.is_dir():
        print(f'ERROR: packet directory not found: {packet_dir}', file=sys.stderr)
        return 1

    solve(packet_dir, out_file)
    return 0


if __name__ == '__main__':
    sys.exit(main())
