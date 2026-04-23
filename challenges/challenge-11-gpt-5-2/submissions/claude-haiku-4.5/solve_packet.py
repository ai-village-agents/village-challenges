from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


def parse_args() -> argparse.Namespace:
    base_packet = Path(__file__).resolve().parents[2] / "data"
    parser = argparse.ArgumentParser(description="Summarize HTTP packet contents.")
    parser.add_argument(
        "--packet",
        type=Path,
        default=base_packet,
        help="Packet directory containing expected_logins.json and http/ (default: ../data)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional output file for the JSON report (default: stdout).",
    )
    return parser.parse_args()


def parse_http_response(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    header_body = re.split(r"\r?\n\r?\n", text, maxsplit=1)
    headers_section = header_body[0]
    body = header_body[1] if len(header_body) > 1 else ""
    status_line = headers_section.splitlines()[0].strip() if headers_section.splitlines() else ""
    status_match = re.match(r"HTTP/\S+\s+(\d{3})", status_line)
    status_code = status_match.group(1) if status_match else None

    body_json = None
    stripped_body = body.strip()
    if stripped_body:
        try:
            body_json = json.loads(stripped_body)
        except json.JSONDecodeError:
            body_json = None

    return {"status": status_code, "body": body, "json": body_json}


def collect_repositories(http_dir: Path) -> list:
    repos = []
    for repo_file in sorted(http_dir.glob("repos__*.http")):
        name = repo_file.stem.split("repos__", 1)[1]
        repo_resp = parse_http_response(repo_file)
        has_pages_value = None
        if isinstance(repo_resp.get("json"), dict) and "has_pages" in repo_resp["json"]:
            has_pages_value = bool(repo_resp["json"].get("has_pages"))

        pages_file = http_dir / f"pages__{name}.http"
        pages_resp = parse_http_response(pages_file) if pages_file.exists() else {"status": None, "json": None}
        pages_status = pages_resp.get("status")
        pages_built = False
        if isinstance(pages_resp.get("json"), dict):
            pages_built = pages_resp["json"].get("status") == "built"

        public_file = http_dir / f"public__{name}.http"
        public_resp = parse_http_response(public_file) if public_file.exists() else {"status": None}
        public_status = public_resp.get("status")

        repos.append(
            {
                "name": name,
                "has_pages_field": has_pages_value,
                "pages_endpoint_status": pages_status,
                "public_pages_status": public_status,
                "pages_built": pages_built,
            }
        )
    return repos


def collect_ghost_accounts(http_dir: Path, packet_dir: Path) -> list:
    expected_logins_path = packet_dir / "expected_logins.json"
    expected_logins = json.loads(expected_logins_path.read_text(encoding="utf-8"))
    ghosts = []
    for login in expected_logins:
        user_file = http_dir / f"users__{login}.http"
        if not user_file.exists():
            continue
        user_resp = parse_http_response(user_file)
        if user_resp.get("status") == "404":
            ghosts.append(login)
    return ghosts


def main() -> None:
    args = parse_args()
    packet_dir = args.packet.expanduser().resolve()
    http_dir = packet_dir / "http"
    if not http_dir.is_dir():
        raise SystemExit(f"HTTP directory not found: {http_dir}")

    report = {
        "repositories": collect_repositories(http_dir),
        "ghost_accounts": collect_ghost_accounts(http_dir, packet_dir),
    }

    output = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
