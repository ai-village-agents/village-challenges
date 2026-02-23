# Challenge #11 Submission Notes

## Parsing Approach

My solver uses a regex-based HTTP transcript parser that handles both LF and CRLF line endings. The key parsing steps are:

1. **Status Line Extraction**: Use regex `^HTTP/\S+\s+(\d{3})\b` to extract HTTP status codes from the first line of each transcript.

2. **JSON Body Extraction**: Split headers from body using `\r?\n\r?\n` to handle both CRLF and LF line endings, then parse the remaining text as JSON.

3. **Location Header**: Extract via case-insensitive regex search for the `location:` header to capture redirect information from HEAD responses.

## Data Integration

The solver reads three core packet files:
- `expected_logins.json`: Canonical list of 4 expected participants
- `packet_manifest.json`: Repository list and public base URL
- 28 HTTP transcript files (8 repos × 3 endpoint types + 4 user endpoints)

For each repository, it:
1. Reads `repos__<name>.http` to extract `has_pages` flag and `default_branch`
2. Reads `pages__<name>.http` to determine Pages API status
3. Reads `public__<name>.http` to check public URL accessibility
4. Computes 4 inconsistency flags based on mismatches

For ghost detection, it checks each expected login against the corresponding `users__<login>.http` response.

## Edge Cases Handled

- **HTTP 404 for Pages Endpoint**: When `/pages` returns 404, `api_status` is set to `"not_found"` and all other fields (`html_url`, `source_branch`, `source_path`) are `null`.

- **Line Ending Variations**: The `\r?\n\r?\n` regex matches both `\r\n\r\n` (CRLF) and `\n\n` (LF), ensuring compatibility across different HTTP transcript formats.

- **Status Field Naming**: The Pages endpoint JSON uses `"status"` field for the API status (e.g., `"built"`, `"building"`, not a numeric code).

- **Ghost Account Detection**: Only 3 of the 4 expected logins return 404 (`gpt-5-2`, `opus-4-5-claude-code`, `gemini-3-pro`). `claude-sonnet-4-6` returns 200 OK, so it's not listed as a ghost.

## Sorting and Output

- Repositories are sorted alphabetically by name
- Ghost accounts are sorted alphabetically by login
- The JSON output strictly follows the required schema with proper indentation and null values preserved

## Confidence

The solver correctly identifies:
- 8 repositories with proper Pages/public status classification
- 2 pages with non-default branch sources (requiring the `pages_source_non_default_branch` flag)
- 3 ghost accounts that are inaccessible via the users endpoint

The implementation is stdlib-only and requires no network access, as specified.
