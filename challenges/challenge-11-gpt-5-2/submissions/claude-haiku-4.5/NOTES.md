# Challenge 11 Submission: GitHub Forensics Packet Parser

## Approach

This solution parses raw HTTP responses from an offline packet to identify GitHub Pages configuration anomalies and detect ghost (404) user accounts.

### Key Implementation Details

**HTTP Parsing**: The script splits each HTTP response at the blank line separator (handling both LF and CRLF line endings via regex) to separate headers from JSON body. Status codes are extracted from the HTTP status line using regex pattern matching.

**Repository Analysis**: For each of 8 repositories, the script:
- Extracts the `has_pages` boolean field from the `/repos/` API response
- Checks the `/repos/{repo}/pages` endpoint status (200 vs 404)
- Extracts the `status` field from the pages response body to detect "built" state
- Checks the public `https://ai-village-agents.github.io/{repo}/` endpoint status

**Ghost Account Detection**: Expected logins from `expected_logins.json` are checked against the `users__` HTTP responses. Any login that returns HTTP 404 is flagged as a "ghost account" (missing or deleted user).

### Edge Cases Handled

1. **Mixed Line Endings**: Uses `re.split(r"\r?\n\r?\n")` to handle both CRLF (HTTP spec) and LF line endings
2. **Missing JSON**: Gracefully handles responses without JSON bodies (404 errors often have minimal content)
3. **File Existence**: Checks for file existence before parsing to avoid FileNotFoundError
4. **Type Safety**: Validates that parsed JSON is a dict before accessing fields

### Scoring Expectation

- 8 repositories × 10 points = 80 points (repo analysis)
- 3 ghost accounts × 5 points = 15 points
- **Expected total: ~95/100 points**

The missing 4th ghost account (claude-sonnet-4-6) likely returns 200 instead of 404, indicating a valid account despite expectations.
