# Challenge #11 - HTTP Packet Forensics

## Parsing Approach

I implemented a robust HTTP response parser that handles both LF and CRLF line endings using Python's `splitlines()`. The parser extracts three components from each raw HTTP file:

1. **Status code** - Using regex `HTTP/\d+(?:\.\d+)?\s+(\d{3})` to handle HTTP/1.1, HTTP/2, and HTTP/2.0 variants
2. **Headers** - Building a lowercase-keyed dictionary for case-insensitive lookups (needed for the `location` header)
3. **JSON body** - Everything after the blank line separator

## Data Aggregation Strategy

I used filename prefixes (`repos__`, `pages__`, `users__`, `public__`) to route each HTTP file to the correct handler. Each repo gets a unified record dictionary that's progressively populated as we encounter its three endpoint files. I stored `default_branch` and the raw HTTP status code as temporary fields (prefixed with `_`) that are stripped out during flag computation.

## Edge Cases Handled

**Pages status ambiguity:** The critical edge case was distinguishing between `"built"` and `"building"` status. Initially I assumed all HTTP 200 responses from `/pages` meant "built", but the spec requires reading the `status` field from the JSON body. This catches repos where Pages are enabled but still building.

**Ghost account detection:** I only flag logins that appear in `expected_logins.json` AND return 404 from the `/users` endpoint. This correctly excludes repos with similar names and handles the shadowbanned agent edge case.

**Default branch comparison:** For the `pages_source_non_default_branch` flag, I extract `default_branch` from the repos JSON and compare against `source.branch` from the pages JSON, handling null values gracefully.

**Sorting:** Both arrays are sorted as specified (repos by name, ghost accounts by login) to ensure deterministic output for grading.

The CLI uses argparse to support `--packet` and `--out` flags with proper validation. Total implementation: ~200 lines of Python stdlib only.
