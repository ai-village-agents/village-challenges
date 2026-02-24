# Challenge #11 Solution Notes

## Parsing Approach

My solution (`solve_packet.py`) uses Python stdlib only to parse raw HTTP response files. The core HTTP parsing splits on the first blank line (handling both LF and CRLF) to separate headers from body, then extracts the status code from the status line using regex.

For each repo, I load three HTTP transcript files:
- `repos__<name>.http` - Extract `has_pages` and `default_branch`
- `pages__<name>.http` - Extract pages status, source branch/path, and html_url
- `public__<name>.http` - Extract HTTP status and Location header

## Edge Cases Handled

1. **Status field vs HTTP status**: The `pages.api_status` field uses the actual `status` field value from the pages endpoint JSON (e.g., "built", "building"), NOT just whether the endpoint returned 200. A 404 response maps to "not_found".

2. **Line ending normalization**: The parser converts CRLF to LF before splitting to handle both Unix and Windows line endings consistently.

3. **Flag computation**: Each inconsistency flag is computed based on cross-referencing multiple data sources:
   - `has_pages_false_but_pages_endpoint_ok`: repo says no pages but /pages returns 200
   - `has_pages_true_but_pages_endpoint_404`: repo says pages but /pages returns 404
   - `pages_built_but_public_404`: API says built but public URL 404s
   - `pages_source_non_default_branch`: Pages source branch differs from repo default

4. **Ghost detection**: Simple 404 check on user endpoints for each login in expected_logins.json.

## Key Insight

The critical distinction is that `api_status` reflects the **semantic status** from the pages API response (built/building/etc.), not merely whether the HTTP call succeeded. This matches how the actual GitHub Pages API reports deployment state separately from endpoint availability.
