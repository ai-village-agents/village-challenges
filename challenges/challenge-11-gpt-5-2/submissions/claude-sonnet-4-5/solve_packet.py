import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a packet report for GitHub Pages status."
    )
    parser.add_argument(
        "--packet",
        required=True,
        help="Path to the packet directory containing HTTP captures and expected_logins.json.",
    )
    parser.add_argument(
        "--out",
        default="report.json",
        help="Path to write the generated report JSON (default: report.json).",
    )
    return parser.parse_args()


def parse_http_response(raw_response):
    if not raw_response:
        raise ValueError("Empty HTTP response")

    # Normalize newlines so splitlines handles CRLF pairs.
    lines = raw_response.splitlines()
    if not lines:
        raise ValueError("HTTP response missing status line")

    status_line = lines[0].strip()
    status_match = re.match(r"HTTP/\d+(?:\.\d+)?\s+(\d{3})", status_line)
    if not status_match:
        raise ValueError(f"Malformed HTTP status line: {status_line}")
    status_code = int(status_match.group(1))

    headers = {}
    idx = 1
    total = len(lines)
    while idx < total:
        line = lines[idx]
        idx += 1
        if line.strip() == "":
            break
        if ":" not in line:
            # Ignore malformed header lines instead of failing outright.
            continue
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()

    body = "\n".join(lines[idx:]) if idx < total else ""
    return status_code, headers, body


def load_expected_logins(packet_path: Path):
    expected_path = packet_path / "expected_logins.json"
    if not expected_path.is_file():
        raise FileNotFoundError(f"expected_logins.json not found in {packet_path}")
    with expected_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("expected_logins.json must contain a JSON array of logins")
    return set(str(login) for login in data)


def ensure_repo_record(repos_map, slug):
    record = repos_map.get(slug)
    if record is None:
        record = {
            "repo": slug,
            "has_pages": False,
            "pages": {
                "api_status": "not_found",
                "html_url": None,
                "source_branch": None,
                "source_path": None,
            },
            "public": {
                "url": f"https://ai-village-agents.github.io/{slug}/",
                "http_status": None,
                "location": None,
            },
            "flags": [],
            "_default_branch": None,
            "_pages_status_code": None,
        }
        repos_map[slug] = record
    return record


def ingest_http_file(file_path: Path, repos_map, user_status_map):
    raw_response = file_path.read_text(encoding="utf-8")
    status_code, headers, body = parse_http_response(raw_response)
    name = file_path.name
    prefix, sep, remainder = name.partition("__")
    if sep != "__":
        return
    identifier = remainder.rsplit(".", 1)[0]

    if prefix == "repos":
        record = ensure_repo_record(repos_map, identifier)
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {}
        record["repo"] = payload.get("name", identifier)
        record["has_pages"] = bool(payload.get("has_pages", False))
        record["_default_branch"] = payload.get("default_branch")
    elif prefix == "pages":
        record = ensure_repo_record(repos_map, identifier)
        record["_pages_status_code"] = status_code
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {}
        if status_code == 200:
            record["pages"]["html_url"] = f"https://ai-village-agents.github.io/{identifier}/"
            record["pages"]["api_status"] = payload.get("status")
            source = payload.get("source") or {}
            record["pages"]["source_branch"] = source.get("branch")
            record["pages"]["source_path"] = source.get("path")
        elif status_code == 404:
            record["pages"]["api_status"] = "not_found"
            record["pages"]["html_url"] = None
            record["pages"]["source_branch"] = None
            record["pages"]["source_path"] = None
        else:
            record["pages"]["html_url"] = None
            record["pages"]["source_branch"] = None
            record["pages"]["source_path"] = None
    elif prefix == "public":
        record = ensure_repo_record(repos_map, identifier)
        record["public"]["http_status"] = status_code
        record["public"]["location"] = headers.get("location")
    elif prefix == "users":
        user_status_map[identifier] = status_code


def finalize_repo_flags(repos_map):
    for record in repos_map.values():
        pages_status = record.pop("_pages_status_code", None)
        default_branch = record.pop("_default_branch", None)
        has_pages = record["has_pages"]
        public_status = record["public"]["http_status"]
        source_branch = record["pages"]["source_branch"]

        if pages_status == 200 and not has_pages:
            record["flags"].append("has_pages_false_but_pages_endpoint_ok")
        if pages_status == 404 and has_pages:
            record["flags"].append("has_pages_true_but_pages_endpoint_404")
        if pages_status == 200 and public_status == 404:
            record["flags"].append("pages_built_but_public_404")
        if (
            pages_status == 200
            and source_branch
            and default_branch
            and source_branch != default_branch
        ):
            record["flags"].append("pages_source_non_default_branch")


def build_report(packet_path: Path, output_path: Path):
    expected_logins = load_expected_logins(packet_path)
    repos_map = {}
    user_status_map = {}

    for file_path in packet_path.rglob("*.http"):
        if not file_path.is_file():
            continue
        ingest_http_file(file_path, repos_map, user_status_map)

    finalize_repo_flags(repos_map)

    repos = sorted(repos_map.values(), key=lambda entry: entry["repo"])
    ghost_accounts = [
        {
            "login": login,
            "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
        }
        for login in sorted(expected_logins)
        if user_status_map.get(login) == 404
    ]

    report = {
        "packet_version": "v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repos": repos,
        "ghost_accounts": ghost_accounts,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def main():
    args = parse_args()
    packet_path = Path(args.packet).expanduser().resolve()
    if not packet_path.is_dir():
        raise NotADirectoryError(f"Packet directory not found: {packet_path}")

    output_path = Path(args.out).expanduser().resolve()
    build_report(packet_path, output_path)


if __name__ == "__main__":
    main()
