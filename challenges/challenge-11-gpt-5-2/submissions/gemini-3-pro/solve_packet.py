from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple


def parse_http(path: Path) -> Tuple[int, Dict[str, str], str]:
    """
    Parse a raw HTTP transcript (status line + headers + optional body).

    Returns (status_code, headers_lowercased, body_text).
    Handles either LF or CRLF separators between the headers and body.
    """
    text = path.read_text("utf-8", errors="replace")

    status_match = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    if not status_match:
        raise ValueError(f"Could not locate HTTP status line in {path}")
    status = int(status_match.group(1))

    sep_match = re.search(r"\r?\n\r?\n", text)
    if sep_match:
        header_part = text[: sep_match.start()]
        body = text[sep_match.end() :]
    else:
        header_part = text
        body = ""

    headers: Dict[str, str] = {}
    header_lines = header_part.splitlines()
    for line in header_lines[1:]:
        if not line.strip() or ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()

    return status, headers, body


def load_json_body(path: Path) -> Tuple[int, Dict[str, str], Dict]:
    status, headers, body = parse_http(path)
    return status, headers, json.loads(body)


def build_repo_record(repo: str, http_dir: Path, public_base: str) -> Dict:
    repo_status, _, repo_obj = load_json_body(http_dir / f"repos__{repo}.http")
    has_pages = bool(repo_obj.get("has_pages"))
    default_branch = repo_obj.get("default_branch")

    pages_path = http_dir / f"pages__{repo}.http"
    pages_status, _, pages_body = parse_http(pages_path)
    if pages_status == 404:
        pages = {
            "api_status": "not_found",
            "html_url": None,
            "source_branch": None,
            "source_path": None,
        }
    else:
        pages_obj = json.loads(pages_body)
        pages = {
            "api_status": pages_obj.get("status"),
            "html_url": pages_obj.get("html_url"),
            "source_branch": (pages_obj.get("source") or {}).get("branch"),
            "source_path": (pages_obj.get("source") or {}).get("path"),
        }

    public_status, public_headers, _ = parse_http(http_dir / f"public__{repo}.http")
    public = {
        "url": f"{public_base}{repo}/",
        "http_status": public_status,
        "location": public_headers.get("location"),
    }

    flags = []
    if (not has_pages) and pages_status != 404:
        flags.append("has_pages_false_but_pages_endpoint_ok")
    if has_pages and pages_status == 404:
        flags.append("has_pages_true_but_pages_endpoint_404")
    if pages.get("api_status") == "built" and public.get("http_status") == 404:
        flags.append("pages_built_but_public_404")
    if pages.get("source_branch") and default_branch and pages["source_branch"] != default_branch:
        flags.append("pages_source_non_default_branch")

    return {
        "repo": repo,
        "has_pages": has_pages,
        "default_branch": default_branch,
        "pages": pages,
        "public": public,
        "flags": sorted(flags),
    }


def detect_ghosts(expected_logins_path: Path, http_dir: Path) -> list[Dict[str, str]]:
    expected_logins = json.loads(expected_logins_path.read_text("utf-8"))
    ghosts = []
    for login in expected_logins:
        status, _, _ = parse_http(http_dir / f"users__{login}.http")
        if status == 404:
            ghosts.append(
                {
                    "login": login,
                    "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
                }
            )
    ghosts.sort(key=lambda g: g["login"])
    return ghosts


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse offline GitHub packet into a JSON report.")
    parser.add_argument("--packet", required=True, help="Path to packet directory (contains http/ etc.)")
    parser.add_argument("--out", required=True, help="Path to write the generated report.json")
    args = parser.parse_args()

    packet_dir = Path(args.packet)
    http_dir = packet_dir / "http"

    manifest_path = packet_dir / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    public_base = manifest.get("public_base", "")

    repos = [build_repo_record(repo, http_dir, public_base) for repo in manifest.get("repos", [])]
    repos.sort(key=lambda r: r["repo"])

    ghosts = detect_ghosts(packet_dir / "expected_logins.json", http_dir)

    report = {
        "packet_version": manifest.get("packet_version", "v1"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repos": repos,
        "ghost_accounts": ghosts,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), "utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
