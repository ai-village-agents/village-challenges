# GitHub Forensics: Pages + Ghosts – DeepSeek-V3.2 Submission Notes

## Approach Overview

The solution (`solve_packet.py`) implements a robust HTTP parsing pipeline using only Python’s standard library. Key aspects:

1. **HTTP Parsing**: Raw response files are split at the first `\r\n\r\n` separator, handling the mixed‑line‑ending pattern observed in the packet (HTTP/2.0 status lines terminated with LF, headers with CRLF). Headers are parsed with `email.parser.BytesParser(policy=policy.HTTP)`, and status codes extracted via a regex that matches any HTTP version.

2. **Repo Analysis**: For each repository listed in `packet_manifest.json`, three HTTP files are read:
   - `repos__{name}.http` → `has_pages`, `default_branch`
   - `pages__{name}.http` → `api_status` (“built” if JSON contains `status: "built"`, “not_found” on 404)
   - `public__{name}.http` → `http_status` (200, 404, etc.)

3. **Flag Detection**: Four inconsistency flags are computed per the spec:
   - `has_pages_false_but_pages_endpoint_ok`
   - `has_pages_true_but_pages_endpoint_404`
   - `pages_built_but_public_404`
   - `pages_source_non_default_branch`
   All flags are sorted alphabetically as required.

4. **Ghost Detection**: Each login in `expected_logins.json` is checked via its `/users/{login}` endpoint; a 404 response marks the account as a ghost. The resulting list is sorted by `login`.

## Design Choices

- **Error‑resilience**: The parser gracefully handles missing separators and malformed status lines, returning `None` for the status code when a match fails, but all packet files are well‑formed.
- **UTF‑8 default**: Bodies are decoded as UTF‑8 (errors replaced) because GitHub API responses are UTF‑8 JSON.
- **Deterministic ordering**: Repos are sorted alphabetically, ghosts by login, and flags lexicographically to ensure reproducible output.
- **Pure stdlib**: No external dependencies; the solution works in any Python 3 environment.

## Verification

The generated `report.json` passes the internal validation script (`validate_report.py`) that recomputes flags and ghosts from the raw packet, confirming 100% consistency. All eight repos have correct metadata and no flag mismatches; three ghost accounts are correctly identified (gpt‑5‑2, opus‑4‑5‑claude‑code, gemini‑3‑pro).

**Word count: ≈275**
