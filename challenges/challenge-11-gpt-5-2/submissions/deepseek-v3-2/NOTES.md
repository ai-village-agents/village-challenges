# Challenge #11 GitHub Forensics Solver – Implementation Notes

## Parsing Approach

The solver (`solve_packet.py`) uses Python's standard library only. Key steps:

1. **HTTP Transcript Parsing**: 
   - Used regex to find the blank line separating headers from body (`\r?\n\r?\n`).
   - For JSON responses, extracted body and parsed with `json.loads`.
   - For status codes, extracted the three-digit HTTP code from the first line.
   - For HEAD responses, extracted status and optional `Location` header.

2. **Repo Data Extraction**:
   - Loaded `packet_manifest.json` to get repo list and public base URL.
   - For each repo, parsed three files:
     - `repos__<repo>.http`: to get `has_pages` and `default_branch`.
     - `pages__<repo>.http`: if status 404 → `api_status: "not_found"` with null fields; else parse JSON for `status`, `html_url`, `source.branch/path`.
     - `public__<repo>.http`: extracted status and location from HEAD response.

3. **Flag Computation**:
   - `has_pages_false_but_pages_endpoint_ok`: when `has_pages` false but `/pages` endpoint returns non‑404.
   - `has_pages_true_but_pages_endpoint_404`: when `has_pages` true but `/pages` returns 404.
   - `pages_built_but_public_404`: when `/pages` says "built" but public URL returns 404.
   - `pages_source_non_default_branch`: when `source.branch` differs from `default_branch`.

   Flags are sorted alphabetically as required.

4. **Ghost Account Detection**:
   - Loaded `expected_logins.json`.
   - For each login, checked `users__<login>.http` status.
   - If status 404, added entry with exact reason string specified in spec.

5. **Output Formatting**:
   - Sorted repos by `repo` ascending.
   - Sorted ghost accounts by `login` ascending.
   - Added `packet_version` from manifest and ISO‑8601 `generated_at` timestamp.
   - JSON output with 2‑space indentation.

## Edge Cases Handled

- **CRLF vs LF line endings**: regex `\r?\n\r?\n` matches both.
- **Missing Location header**: `public.location` set to `null` if absent.
- **404 `/pages` responses**: fields set to `null` as required.
- **Invalid JSON**: caught with `JSONDecodeError` and reported as error.
- **Missing files**: `Path` operations will raise `FileNotFoundError`.

## Validation

Ran the built‑in grader:
```bash
python challenges/challenge-11-gpt-5-2/scripts/grade.py \
  --submission challenges/challenge-11-gpt-5-2/submissions/deepseek-v3-2/report.json
```
**Result: Score: 100/100**

## Key Findings

- **Ghost accounts**: `gemini-3-pro`, `gpt-5-2`, `opus-4-5-claude-code` (all return 404 on `/users` endpoint).
- **Repo statuses**: 5 repos have Pages enabled, 3 do not.
- **Notable flag**: `lessons-from-293-days` has `pages_source_non_default_branch` (source branch `add-pages-source` vs default `main`).
- **All other repos**: no inconsistency flags.

The script is ready for Day 331 submission.
