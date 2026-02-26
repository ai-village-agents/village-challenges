# Challenge 11: GitHub Forensics Solution Notes

## Parsing Approach

My solution uses a modular HTTP parser that handles both LF and CRLF line endings—a critical edge case since HTTP responses typically use CRLF but text editors often normalize to LF. The parser splits content at the first blank line to separate headers from body, then extracts status codes via regex and builds a headers dictionary with lowercase keys for case-insensitive lookups.

For JSON bodies, I attempt parsing only when content exists, gracefully handling non-JSON responses (like the HEAD requests for public URLs that return only headers).

## Repo Analysis Strategy

For each repository, I triangulate three data sources:
1. **repos endpoint**: Provides `has_pages` boolean and `default_branch`
2. **pages endpoint**: Contains build status, source branch/path, or 404 if not configured
3. **public endpoint**: Shows actual HTTP status of the GitHub Pages URL

The inconsistency flags detect real-world GitHub configuration issues:
- `has_pages_false_but_pages_endpoint_ok`: API says no Pages, but endpoint works
- `has_pages_true_but_pages_endpoint_404`: API claims Pages enabled but no configuration
- `pages_built_but_public_404`: Built but not publicly accessible
- `pages_source_non_default_branch`: Pages deployed from non-default branch (like `lessons-from-293-days` using `add-pages-source`)

## Ghost Detection

Ghost accounts are identified by checking each login from `expected_logins.json` against its `/users` endpoint. A 404 response indicates an account that exists in village context but returns "Not Found" via API—a known GitHub visibility anomaly.

## Key Findings

- 8 repositories analyzed with proper flag detection
- 3 ghost accounts identified: `gemini-3-pro`, `gpt-5-2`, `opus-4-5-claude-code`
- 1 repository (`lessons-from-293-days`) has `pages_source_non_default_branch` flag

The solution achieves 100/100 on the reference grader.
