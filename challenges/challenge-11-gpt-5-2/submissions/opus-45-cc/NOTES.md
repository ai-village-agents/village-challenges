# C11 GitHub Forensics: Parsing Approach

## HTTP Response Parsing

The solver handles raw HTTP responses with mixed line endings (LF/CRLF) by using regex-based splitting. The key challenge was correctly separating headers from body using `\r?\n\r?\n` pattern to find the blank line delimiter.

Status codes are extracted from the first line using pattern matching on `HTTP/X.X NNN`. Headers are parsed into a case-insensitive dictionary for flexible lookup (e.g., `Location` vs `location`).

## Repo Analysis

For each repository, three HTTP transcript files are processed:
- `repos__*.http`: Extracts `has_pages` boolean and `default_branch` for flag computation
- `pages__*.http`: Extracts API status (preserving exact values like "building"), source branch/path, and html_url
- `public__*.http`: Extracts HTTP status code and Location header for redirect detection

## Flag Computation

Four inconsistency flags are computed based on cross-referencing the three data sources:
1. `has_pages_false_but_pages_endpoint_ok`: Repo API says no pages, but pages endpoint returns 200
2. `has_pages_true_but_pages_endpoint_404`: Repo API says has pages, but pages endpoint returns 404
3. `pages_built_but_public_404`: Pages API says built, but public URL returns 404
4. `pages_source_non_default_branch`: Pages source branch differs from repo default branch

## Ghost Detection

Users listed in `expected_logins.json` are checked against their `users__*.http` transcripts. Any 404 response indicates a "ghost account" - an expected participant whose GitHub account doesn't resolve via the API.

## Edge Cases

- The `pages.api_status` preserves the exact value from the API response (including "building"), rather than normalizing to "built"/"not_found"
- Empty or missing Location headers are represented as `null`
