# Challenge #11 Solver — NOTES

## Approach

My solver (`solve_packet.py`) is a pure-stdlib Python 3 script with zero network calls. It reads the offline packet directory, parses each raw HTTP transcript, and emits a normalised `report.json`.

### HTTP Transcript Parsing

The core challenge is reliable HTTP response parsing despite mixed CRLF/LF line endings. My approach:

1. **Normalise line endings first:** I read each file as raw bytes, replace `\r\n` and `\r` with `\n`, then decode as UTF-8. This eliminates all CRLF ambiguity before any further processing.
2. **Split on double newline:** After normalisation, `\n\n` reliably marks the boundary between headers and body.
3. **Status code extraction:** I match `^HTTP/\S+\s+(\d{3})` against the first line — this handles both `HTTP/2.0 200 OK` (full text) and `HTTP/2 404 ` (HEAD-style with trailing space, no reason phrase).
4. **Header parsing:** Key-value pairs split on the first `:`, lowercased for case-insensitive lookup. This correctly picks up `location:` from redirect responses.

### Pages API Mapping

For a `pages__<repo>.http` with status **404**, I map `api_status` → `"not_found"` and set `html_url`, `source_branch`, `source_path` all to `null`.

For **200** responses, I parse the JSON body directly: `api_status` comes from `status` (which may be `"built"` or `"building"`), and source fields come from `source.branch` / `source.path`.

### Flag Computation

All four flags are computed per the spec, then the array is `sorted()`:

- `has_pages_false_but_pages_endpoint_ok`: `has_pages=False` but pages HTTP status ≠ 404
- `has_pages_true_but_pages_endpoint_404`: `has_pages=True` but pages HTTP status = 404
- `pages_built_but_public_404`: `api_status="built"` but public HTTP status = 404
- `pages_source_non_default_branch`: source branch present and differs from `default_branch`

One edge case: `repo-health-dashboard` had `api_status="building"` (not `"built"`), so the `pages_built_but_public_404` flag did not fire for it — correctly.

### Ghost Detection

For each login in `expected_logins.json`, I parse the corresponding `users__<login>.http` and check the HTTP status. A **404** means the account is a ghost. In this packet, three of four expected logins returned 404: `gemini-3-pro`, `gpt-5-2`, and `opus-4-5-claude-code`. My own account (`claude-sonnet-4-6`) returned 200.

### Sorting

- `repos` sorted by `repo` key ascending (alphabetical)
- `ghost_accounts` sorted by `login` key ascending

### Verification

I ran the reference grader against my output:

```
Score: 100/100
```

All 8 repos and all 4 ghost inclusion/exclusion decisions were correct.
