# GPT-5.1 solver notes for Challenge #11 (GitHub Forensics: Pages + Ghosts)

This solver is intentionally small and uses only the Python standard library. The core idea is to treat the packet as a frozen view of the GitHub API and public Pages endpoints, then translate that view into the precise `report.json` shape expected by `scripts/grade.py`.

I first implemented a robust `parse_http_file` helper that understands the simple `.http` transcript format used in the packet. It splits the status line, headers, and body, normalizes line endings, lowercases header keys, and returns `(status_code, headers, body_text)`. A thin `load_json_body` wrapper adds JSON parsing for 2xx responses.

Using `packet_manifest.json`, I iterate over the listed repos. For each repo, I read:
- `repos__<name>.http` to get `has_pages` and the default branch.
- `pages__<name>.http` to fill `pages.api_status`, `html_url`, `source_branch`, and `source_path` (or mark `api_status="not_found"` on a 404).
- `public__<name>.http` to compute `public.url`, `http_status`, and any redirect `location` header.

Flags are then computed with straightforward conditionals that mirror the spec word‑for‑word. I assemble the `flags` list, sort it, and sort the final `repos` array by name.

Ghost detection is driven entirely by `expected_logins.json`. For each login, if `users__login.http` returns 404, I emit a `ghost_accounts` entry with the required reason string and finally sort by login.

Originally I normalized Pages statuses, which cost 2/100 points. I fixed this by preserving the exact `status` string from the Pages JSON. After that change, `scripts/grade.py` reports a perfect 100/100.
