#!/usr/bin/env python3
"""Parse offline GitHub HTTP packet transcripts into a consolidated report."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class HttpPayload:
    status_code: Optional[int]
    headers: Dict[str, str]
    body_text: str
    json_body: Optional[Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse offline GitHub HTTP packet transcripts."
    )
    parser.add_argument(
        "--packet",
        required=True,
        help="Path to packet directory containing data/expected_logins.json, data/packet_manifest.json, and data/http/*.http files.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output path for generated JSON report.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_http_response(raw_text: str) -> HttpPayload:
    text = normalize_newlines(raw_text)
    lines = text.split("\n")
    start_idx = next((idx for idx, line in enumerate(lines) if line.startswith("HTTP/")), 0)

    headers_block: List[str] = []
    body_lines: List[str] = []
    seen_blank = False
    for line in lines[start_idx:]:
        if not seen_blank:
            if line == "":
                seen_blank = True
                continue
            headers_block.append(line)
        else:
            body_lines.append(line)

    status_line = headers_block[0] if headers_block else ""
    status_code: Optional[int] = None
    parts = status_line.split()
    if len(parts) >= 2 and parts[0].startswith("HTTP/"):
        try:
            status_code = int(parts[1])
        except ValueError:
            status_code = None

    headers: Dict[str, str] = {}
    for line in headers_block[1:]:
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()

    body_text = "\n".join(body_lines).strip("\n")
    json_body: Optional[Any] = None
    if body_text.strip():
        try:
            json_body = json.loads(body_text)
        except json.JSONDecodeError:
            json_body = None

    return HttpPayload(
        status_code=status_code,
        headers=headers,
        body_text=body_text,
        json_body=json_body,
    )


def scan_http_files(http_dir: Path) -> Tuple[Dict[str, HttpPayload], Dict[str, HttpPayload], Dict[str, HttpPayload], Dict[str, HttpPayload]]:
    repos_payloads: Dict[str, HttpPayload] = {}
    pages_payloads: Dict[str, HttpPayload] = {}
    public_payloads: Dict[str, HttpPayload] = {}
    users_payloads: Dict[str, HttpPayload] = {}

    for path in sorted(http_dir.glob("*.http")):
        stem = path.stem
        if "__" not in stem:
            continue
        prefix, key = stem.split("__", 1)
        payload = parse_http_response(path.read_text(encoding="utf-8"))

        if prefix == "repos":
            repos_payloads[key] = payload
        elif prefix == "pages":
            pages_payloads[key] = payload
        elif prefix == "public":
            public_payloads[key] = payload
        elif prefix == "users":
            users_payloads[key] = payload

    return repos_payloads, pages_payloads, public_payloads, users_payloads


def determine_packet_version(manifest: Dict[str, Any]) -> str:
    for key in ("packet_version", "version"):
        value = manifest.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "unknown"


def first_non_null(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def compute_pages_info(payload: Optional[HttpPayload]) -> Tuple[Dict[str, Any], Optional[int], bool]:
    pages_info = {
        "api_status": None,
        "html_url": None,
        "source_branch": None,
        "source_path": None,
    }
    if payload is None:
        return pages_info, None, False

    status_code = payload.status_code
    body = payload.json_body if isinstance(payload.json_body, dict) else {}
    is_not_found = status_code == 404 or (isinstance(body, dict) and body.get("status") == "404")

    if is_not_found:
        pages_info.update(
            {
                "api_status": "not_found",
                "html_url": None,
                "source_branch": None,
                "source_path": None,
            }
        )
        return pages_info, status_code, True

    source = body.get("source") if isinstance(body, dict) else {}
    pages_info.update(
        {
            "api_status": body.get("status") if isinstance(body, dict) else None,
            "html_url": body.get("html_url") if isinstance(body, dict) else None,
            "source_branch": source.get("branch") if isinstance(source, dict) else None,
            "source_path": source.get("path") if isinstance(source, dict) else None,
        }
    )
    return pages_info, status_code, False


def compute_public_info(repo_name: str, payload: Optional[HttpPayload]) -> Tuple[Dict[str, Any], Optional[int]]:
    http_status = payload.status_code if payload else None
    location = payload.headers.get("location") if payload else None
    return (
        {
            "url": f"https://ai-village-agents.github.io/{repo_name}/",
            "http_status": http_status,
            "location": location,
        },
        http_status,
    )


def collect_repo_names(manifest: Dict[str, Any], *payload_sets: Iterable[str]) -> List[str]:
    manifest_repos = manifest.get("repos", [])
    names: set[str] = set()
    for name in manifest_repos if isinstance(manifest_repos, list) else []:
        if isinstance(name, str):
            names.add(name)
    for payload_keys in payload_sets:
        names.update(payload_keys)
    return sorted(names)


def main() -> None:
    args = parse_args()
    packet_dir = Path(args.packet)
    data_dir = packet_dir / "data"
    http_dir = data_dir / "http"

    expected_logins_path = data_dir / "expected_logins.json"
    manifest_path = data_dir / "packet_manifest.json"

    if not expected_logins_path.is_file():
        raise SystemExit(f"Missing expected logins file: {expected_logins_path}")
    if not manifest_path.is_file():
        raise SystemExit(f"Missing packet manifest file: {manifest_path}")
    if not http_dir.is_dir():
        raise SystemExit(f"Missing http directory: {http_dir}")

    expected_logins = load_json(expected_logins_path)
    manifest = load_json(manifest_path)
    if not isinstance(expected_logins, list):
        raise SystemExit("expected_logins.json must contain a list")

    repos_payloads, pages_payloads, public_payloads, users_payloads = scan_http_files(http_dir)

    repo_names = collect_repo_names(manifest, repos_payloads.keys(), pages_payloads.keys(), public_payloads.keys())
    packet_version = determine_packet_version(manifest)

    repos_output: List[Dict[str, Any]] = []
    for repo_key in repo_names:
        repo_payload = repos_payloads.get(repo_key)
        repo_body = repo_payload.json_body if repo_payload and isinstance(repo_payload.json_body, dict) else {}
        repo_name = first_non_null(
            repo_body.get("name") if isinstance(repo_body, dict) else None,
            repo_key,
        )
        has_pages = bool(repo_body.get("has_pages")) if isinstance(repo_body, dict) else False
        default_branch = repo_body.get("default_branch") if isinstance(repo_body, dict) else None

        pages_payload = pages_payloads.get(repo_key)
        pages_info, pages_status_code, pages_not_found = compute_pages_info(pages_payload)

        public_payload = public_payloads.get(repo_key)
        public_info, public_status_code = compute_public_info(repo_name, public_payload)

        flags: List[str] = []
        pages_api_status = pages_info["api_status"]
        pages_source_branch = pages_info["source_branch"]

        pages_ok = pages_api_status is not None and pages_api_status != "not_found" and (pages_status_code is None or pages_status_code < 400)
        if not has_pages and pages_ok:
            flags.append("has_pages_false_but_pages_endpoint_ok")
        if has_pages and (pages_not_found or (pages_status_code is not None and pages_status_code == 404)):
            flags.append("has_pages_true_but_pages_endpoint_404")
        if pages_api_status == "built" and public_status_code == 404:
            flags.append("pages_built_but_public_404")
        if pages_source_branch and default_branch and pages_source_branch != default_branch:
            flags.append("pages_source_non_default_branch")

        repos_output.append(
            {
                "repo": repo_name,
                "has_pages": has_pages,
                "pages": pages_info,
                "public": public_info,
                "flags": sorted(flags),
            }
        )

    repos_output = sorted(repos_output, key=lambda item: item["repo"])

    ghost_accounts = sorted(
        login
        for login in expected_logins
        if isinstance(login, str)
        and users_payloads.get(login)
        and users_payloads[login].status_code == 404
    )

    report = {
        "packet_version": packet_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repos": repos_output,
        "ghost_accounts": ghost_accounts,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
