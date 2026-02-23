# Challenge #11 - Submission Notes

## Parsing Approach

My solution (`solve_packet.py`) is designed as a robust, offline parser for the provided GitHub forensics packet. It operates by systematically processing the raw HTTP transcripts to reconstruct the state of repositories and user accounts without making any network calls.

### HTTP Transcript Parsing
The core of the solution is the `parse_http` function. It reads the `.http` files using UTF-8 encoding (with error replacement for safety) and splits the content into status line, headers, and body.
- **Header/Body Separation:** I implemented a flexible regex (`\r?\n\r?\n`) to detect the blank line separator, ensuring compatibility with both CRLF (Windows) and LF (Unix) line endings.
- **Status Code Extraction:** The script extracts the numeric status code from the first line using a regex that looks for the `HTTP/x.x` prefix.
- **Headers:** Headers are parsed into a dictionary with lowercase keys to ensure case-insensitive lookups (e.g., for the `Location` header).

### Data Reconstruction
The script iterates through the repositories listed in `packet_manifest.json`. For each repository, it triangulates data from three sources:
1. **`repos__*.http`:** Provides the `default_branch` and the API's claimed `has_pages` status.
2. **`pages__*.http`:** Determines the actual Pages build status (`api_status`). A 404 response here is explicitly handled to map to a `not_found` status with null attributes.
3. **`public__*.http`:** Checks the live availability of the Pages site via the HTTP status code.

### Inconsistency Flagging
The script strictly implements the logic for the four inconsistency flags. It compares the boolean `has_pages` against the presence of the `/pages` endpoint, checks if a "built" page is actually reachable (200 OK vs 404), and verifies if the Pages source branch matches the repository's default branch.

### Ghost Account Detection
Finally, the script validates user presence against `expected_logins.json`. It parses the corresponding `users__*.http` file for each login. If the status is 404, the user is flagged as a "ghost account" with the specific reason string required by the spec.

This approach ensures strict adherence to the challenge requirements, handling edge cases like missing files or unexpected line endings gracefully while producing the exact JSON structure and sorting required for full points.
