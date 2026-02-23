#!/usr/bin/env python3
"""Offline GitHub forensics packet solver for Challenge #11.

Usage (from repo root):

  python challenges/challenge-11-gpt-5-2/submissions/gpt-5-1/solve_packet.py \
    --packet challenges/challenge-11-gpt-5-2/data \
    --out challenges/challenge-11-gpt-5-2/submissions/gpt-5-1/report.json

Stdlib-only, no network access. Parses the HTTP transcript files in the
packet directory and emits a normalized JSON report as required by the
challenge spec.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Tuple, Optional, Any


HTTPStatus = Tuple[int, Dict[str, str], str]


def parse_http_file(path: str) -> HTTPStatus:
    """Parse a raw HTTP transcript file.

    Returns (status_code, headers_dict, body_text).
    Accepts both CRLF and LF line endings and status lines like
    "HTTP/2.0 200 OK" or "HTTP/2 404".
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"HTTP transcript not found: {path}")

    # Normalize line endings
    raw = raw.replace("\r\n", "\n")
    lines = raw.split("\n")
    if not lines or not lines[0].strip():
        raise ValueError(f"Malformed HTTP transcript (missing status line): {path}")

    status_line = lines[0].strip()
    parts = status_line.split()
    if len(parts) < 2:
        raise ValueError(f"Malformed HTTP status line in {path!r}: {status_line!r}")
    try:
        status_code = int(parts[1])
    except ValueError:
        raise ValueError(f"Non-numeric HTTP status code in {path!r}: {status_line!r}")

    headers: Dict[str, str] = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        i += 1
        if line == "":
            break
        if ":" in line:
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()

    body = "\n".join(lines[i:]) if i < len(lines) else ""
    return status_code, headers, body


def load_json_body(path: str) -> Any:
    """Parse an HTTP transcript expected to contain a JSON body.

    Returns the decoded JSON body, ignoring headers.
    Raises if the status is not 2xx or if the body is not valid JSON.
    """
    status, _headers, body = parse_http_file(path)
    if status < 200 or status >= 300:
        raise ValueError(f"Expected 2xx status in {path}, got {status}")
    body = body.strip()
    if not body:
        raise ValueError(f"Empty JSON body in {path}")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to decode JSON body in {path}: {exc}") from exc


def parse_repo_entry(repo: str, packet_dir: str, public_base: str) -> Dict[str, Any]:
    http_dir = os.path.join(packet_dir, "http")

    repos_path = os.path.join(http_dir, f"repos__{repo}.http")
    pages_path = os.path.join(http_dir, f"pages__{repo}.http")
    public_path = os.path.join(http_dir, f"public__{repo}.http")

    # Repo JSON (required)
    repo_json = load_json_body(repos_path)
    has_pages = bool(repo_json.get("has_pages", False))
    default_branch = repo_json.get("default_branch")

    # Pages endpoint
    pages_status, _pages_headers, pages_body = parse_http_file(pages_path)
    pages_api_status: Optional[str]
    pages_html_url: Optional[str]
    pages_source_branch: Optional[str]
    pages_source_path: Optional[str]

    if pages_status == 404:
        pages_api_status = "not_found"
        pages_html_url = None
        pages_source_branch = None
        pages_source_path = None
    else:
        # Best-effort JSON parse; if it fails, treat as not_found.
        body_stripped = pages_body.strip()
        if body_stripped:
            try:
                pages_json = json.loads(body_stripped)
            except json.JSONDecodeError:
                pages_json = {}
        else:
            pages_json = {}

        status_field = pages_json.get("status")
        # Keep the raw status string (e.g. "built", "building") so the
        # grader can distinguish intermediate states like "building".
        pages_api_status = status_field
        pages_html_url = pages_json.get("html_url")
        source = pages_json.get("source") or {}
        pages_source_branch = source.get("branch")
        pages_source_path = source.get("path")

    # Public URL HEAD
    public_status, public_headers, _public_body = parse_http_file(public_path)
    public_url = f"{public_base}{repo}/"
    location = public_headers.get("location")

    # Build flags
    flags = []
    if not has_pages and pages_status != 404:
        flags.append("has_pages_false_but_pages_endpoint_ok")
    if has_pages and pages_status == 404:
        flags.append("has_pages_true_but_pages_endpoint_404")
    if pages_api_status == "built" and public_status == 404:
        flags.append("pages_built_but_public_404")
    if pages_api_status == "built" and default_branch is not None and pages_source_branch is not None:
        if pages_source_branch != default_branch:
            flags.append("pages_source_non_default_branch")

    flags.sort()

    return {
        "repo": repo,
        "has_pages": has_pages,
        "pages": {
            "api_status": pages_api_status,
            "html_url": pages_html_url,
            "source_branch": pages_source_branch,
            "source_path": pages_source_path,
        },
        "public": {
            "url": public_url,
            "http_status": public_status,
            "location": location if location is not None else None,
        },
        "flags": flags,
    }


def compute_ghost_accounts(packet_dir: str, expected_logins: Any) -> Any:
    http_dir = os.path.join(packet_dir, "http")
    ghosts = []
    reason_text = (
        "users endpoint returned 404 but login is listed in expected_logins.json"
    )

    for login in expected_logins:
        if not isinstance(login, str):
            continue
        path = os.path.join(http_dir, f"users__{login}.http")
        if not os.path.exists(path):
            # If there is no transcript, we have no evidence; skip.
            continue
        status, _headers, _body = parse_http_file(path)
        if status == 404:
            ghosts.append({"login": login, "reason": reason_text})

    ghosts.sort(key=lambda g: g["login"])
    return ghosts


def build_report(packet_dir: str) -> Dict[str, Any]:
    manifest_path = os.path.join(packet_dir, "packet_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing packet_manifest.json in {packet_dir}")

    packet_version = manifest.get("packet_version", "v1")
    repos = manifest.get("repos") or []
    public_base = manifest.get("public_base", "https://ai-village-agents.github.io/")

    expected_path = os.path.join(packet_dir, "expected_logins.json")
    try:
        with open(expected_path, "r", encoding="utf-8") as f:
            expected_logins = json.load(f)
    except FileNotFoundError:
        expected_logins = []

    repo_entries = [
        parse_repo_entry(repo, packet_dir, public_base) for repo in repos
    ]
    repo_entries.sort(key=lambda r: r["repo"])

    ghost_accounts = compute_ghost_accounts(packet_dir, expected_logins)

    return {
        "packet_version": packet_version,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repos": repo_entries,
        "ghost_accounts": ghost_accounts,
    }


def main(argv: Optional[Any] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Solve the offline GitHub forensics packet (Challenge #11)",
    )
    parser.add_argument(
        "--packet",
        required=True,
        help="Path to the packet data directory (containing packet_manifest.json)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to write the generated report.json",
    )

    args = parser.parse_args(argv)

    packet_dir = args.packet
    out_path = args.out

    try:
        report = build_report(packet_dir)
    except Exception as exc:
        print(f"Error while building report: {exc}", file=sys.stderr)
        return 1

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=False)
        f.write("\n")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
