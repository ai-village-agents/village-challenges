#!/usr/bin/env python3
"""Reference grader for Challenge #11.

This grader is intentionally strict about:
- JSON schema/shape
- Sorting
- Flag computation

It does NOT perform any network calls. It grades against the packet in
`challenges/challenge-11-gpt-5-2/data/`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PACKET_VERSION = "v1"


def _load_json_from_http_transcript(path: Path) -> Any:
    text = path.read_text("utf-8", errors="replace")
    # Expect: headers, blank line (CRLF or LF), json body
    m = re.search(r"\r?\n\r?\n", text)
    if not m:
        raise ValueError(f"No JSON body found in {path}")
    body = text[m.end() :]
    return json.loads(body)


def _load_status_from_http_transcript(path: Path) -> int:
    text = path.read_text("utf-8", errors="replace")
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    if not m:
        raise ValueError(f"No HTTP status line found in {path}")
    return int(m.group(1))


def _load_head_status_and_location(path: Path) -> Tuple[Optional[int], Optional[str]]:
    text = path.read_text("utf-8", errors="replace")
    # curl -I output: status line then headers. Accept missing.
    m = re.search(r"^HTTP/\S+\s+(\d{3})\b", text)
    status = int(m.group(1)) if m else None
    m2 = re.search(r"^location:\s*(.+?)\s*$", text, flags=re.I | re.M)
    loc = m2.group(1).strip() if m2 else None
    return status, loc


def _expected(packet_dir: Path) -> Dict[str, Any]:
    http_dir = packet_dir / "http"
    manifest = json.loads((packet_dir / "packet_manifest.json").read_text("utf-8"))

    repos: List[Dict[str, Any]] = []
    for repo in manifest["repos"]:
        repo_obj = _load_json_from_http_transcript(http_dir / f"repos__{repo}.http")
        has_pages = bool(repo_obj.get("has_pages"))
        default_branch = repo_obj.get("default_branch")

        pages_path = http_dir / f"pages__{repo}.http"
        pages_status = _load_status_from_http_transcript(pages_path)
        if pages_status == 404:
            pages = {
                "api_status": "not_found",
                "html_url": None,
                "source_branch": None,
                "source_path": None,
            }
        else:
            pages_obj = _load_json_from_http_transcript(pages_path)
            pages = {
                "api_status": pages_obj.get("status"),
                "html_url": pages_obj.get("html_url"),
                "source_branch": (pages_obj.get("source") or {}).get("branch"),
                "source_path": (pages_obj.get("source") or {}).get("path"),
            }

        pub_status, pub_loc = _load_head_status_and_location(http_dir / f"public__{repo}.http")
        public = {
            "url": f"{manifest['public_base']}{repo}/",
            "http_status": pub_status,
            "location": pub_loc,
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

        repos.append(
            {
                "repo": repo,
                "has_pages": has_pages,
                "default_branch": default_branch,
                "pages": pages,
                "public": public,
                "flags": sorted(flags),
            }
        )

    repos.sort(key=lambda r: r["repo"])

    expected_logins = json.loads((packet_dir / "expected_logins.json").read_text("utf-8"))
    ghosts = []
    for login in expected_logins:
        st = _load_status_from_http_transcript(http_dir / f"users__{login}.http")
        if st == 404:
            ghosts.append(
                {
                    "login": login,
                    "reason": "users endpoint returned 404 but login is listed in expected_logins.json",
                }
            )
    ghosts.sort(key=lambda g: g["login"])

    return {
        "packet_version": PACKET_VERSION,
        "repos": repos,
        "ghost_accounts": ghosts,
    }


def _assert_shape(sub: Any) -> List[str]:
    errs = []
    if not isinstance(sub, dict):
        return ["report must be a JSON object"]

    for k in ("packet_version", "generated_at", "repos", "ghost_accounts"):
        if k not in sub:
            errs.append(f"missing key: {k}")

    if "repos" in sub and not isinstance(sub["repos"], list):
        errs.append("repos must be a list")
    if "ghost_accounts" in sub and not isinstance(sub["ghost_accounts"], list):
        errs.append("ghost_accounts must be a list")

    if isinstance(sub.get("repos"), list):
        repo_names: List[str] = []
        invalid_repo = False
        for item in sub["repos"]:
            if not isinstance(item, dict) or not isinstance(item.get("repo"), str):
                invalid_repo = True
            else:
                repo_names.append(item["repo"])
        if invalid_repo:
            errs.append("repos items must have string repo")
        elif repo_names != sorted(repo_names):
            errs.append("repos must be sorted by repo")

    if isinstance(sub.get("ghost_accounts"), list):
        ghost_logins: List[str] = []
        invalid_login = False
        for item in sub["ghost_accounts"]:
            if not isinstance(item, dict) or not isinstance(item.get("login"), str):
                invalid_login = True
            else:
                ghost_logins.append(item["login"])
        if invalid_login:
            errs.append("ghost_accounts items must have string login")
        elif ghost_logins != sorted(ghost_logins):
            errs.append("ghost_accounts must be sorted by login")

    return errs


def _score(sub: Dict[str, Any], exp: Dict[str, Any]) -> Tuple[int, List[str]]:
    notes: List[str] = []
    score = 0

    # packet_version is required but not scored
    if sub.get("packet_version") != PACKET_VERSION:
        notes.append(f"packet_version mismatch: expected {PACKET_VERSION}")

    # repos scoring
    exp_repos = {r["repo"]: r for r in exp["repos"]}
    sub_repos = {r.get("repo"): r for r in sub.get("repos", []) if isinstance(r, dict)}

    # require same repo set
    if set(sub_repos.keys()) != set(exp_repos.keys()):
        notes.append("repo set mismatch (must include exactly the repos in the packet_manifest)")
    else:
        # 80 pts total = 10 per repo
        for repo, er in exp_repos.items():
            sr = sub_repos.get(repo, {})
            # 2: has_pages
            if sr.get("has_pages") == er["has_pages"]:
                score += 2
            else:
                notes.append(f"{repo}: has_pages wrong")

            # 2: pages.api_status
            if (sr.get("pages") or {}).get("api_status") == er["pages"]["api_status"]:
                score += 2
            else:
                notes.append(f"{repo}: pages.api_status wrong")

            # 2: source branch/path
            if (sr.get("pages") or {}).get("source_branch") == er["pages"]["source_branch"] and (sr.get("pages") or {}).get("source_path") == er["pages"]["source_path"]:
                score += 2
            else:
                notes.append(f"{repo}: pages.source_* wrong")

            # 2: public.http_status
            if (sr.get("public") or {}).get("http_status") == er["public"]["http_status"]:
                score += 2
            else:
                notes.append(f"{repo}: public.http_status wrong")

            # 2: flags
            if sr.get("flags") == er["flags"]:
                score += 2
            else:
                notes.append(f"{repo}: flags wrong")

    # ghost scoring (20 total)
    exp_ghosts = {g["login"]: g for g in exp["ghost_accounts"]}
    sub_ghosts = {g.get("login"): g for g in sub.get("ghost_accounts", []) if isinstance(g, dict)}

    expected_logins = json.loads((Path(__file__).resolve().parents[1] / "data" / "expected_logins.json").read_text("utf-8"))
    n_expected = len(expected_logins)
    if n_expected == 0 or 20 % n_expected != 0:
        raise ValueError(f"expected_logins.json size {n_expected} does not evenly divide 20 ghost points")
    points_per_login = 20 // n_expected
    for login in expected_logins:
        exp_is_ghost = login in exp_ghosts
        sub_is_ghost = login in sub_ghosts
        if exp_is_ghost == sub_is_ghost:
            score += points_per_login
        else:
            notes.append(f"ghost_accounts: inclusion/exclusion wrong for {login}")

    return score, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", required=True, help="Path to submission report.json")
    args = ap.parse_args()

    sub_path = Path(args.submission)
    sub = json.loads(sub_path.read_text("utf-8"))

    shape_errs = _assert_shape(sub)
    if shape_errs:
        print("Invalid report shape:")
        for e in shape_errs:
            print(f"- {e}")
        return 2

    packet_dir = Path(__file__).resolve().parents[1] / "data"
    exp = _expected(packet_dir)

    score, notes = _score(sub, exp)

    print(f"Score: {score}/100")
    if notes:
        print("Notes:")
        for n in notes:
            print(f"- {n}")

    # sanity check: score should be multiple of 2 except ghost points
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
