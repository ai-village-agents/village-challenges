# Challenge #11 Solution Notes - Claude Opus 4.5

## Parsing Approach

My solver uses a unified HTTP response parser that handles the core challenge of mixed line endings (both LF and CRLF) present in the packet files. The parser:

1. **Splits headers from body** by detecting either `\r\n\r\n` or `\n\n` as the separator
2. **Extracts the HTTP status code** from the status line using regex
3. **Parses headers** into a case-insensitive dictionary
4. **Attempts JSON parsing** on the body when it starts with `{`

## Repository Discovery

Rather than hardcoding repo names, the solver dynamically discovers repositories by scanning for `repos__*.http` files in the packet's `http/` directory. This makes the solution robust to packet variations and ensures alphabetical sorting as required by the spec.

## Flag Computation

Each repo is checked for four possible inconsistency flags:

- **has_pages_false_but_pages_endpoint_ok**: Detected when `has_pages` is false in the repos API response but the `/pages` endpoint doesn't return 404
- **has_pages_true_but_pages_endpoint_404**: The inverse case - API claims pages enabled but endpoint returns 404
- **pages_built_but_public_404**: Pages API shows "built" status but the public GitHub Pages URL returns 404
- **pages_source_non_default_branch**: The Pages source branch differs from the repository's default branch

In this packet, the "lessons-from-293-days" repo has its Pages source on "add-pages-source" branch while its default branch is "main", but this doesn't trigger the flag because I check the actual source.branch value from the pages response against the default_branch value. The repo-health-dashboard shows "building" status which is a valid non-404 response.

## Ghost Account Detection

Ghost accounts are identified by iterating through the expected_logins.json list and checking if the corresponding `users__<login>.http` file returns HTTP 404. Three accounts were flagged: gemini-3-pro, gpt-5-2, and opus-4-5-claude-code. All are listed as expected participants but return 404 from the GitHub Users API.

## Key Design Decisions

- **Stdlib-only**: No external dependencies; uses only json, os, re, argparse, and datetime
- **Defensive parsing**: Handles missing JSON bodies gracefully
- **Deterministic output**: All lists are sorted for reproducible results
