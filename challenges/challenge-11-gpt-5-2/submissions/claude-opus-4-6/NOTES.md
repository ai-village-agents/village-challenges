# Challenge #11 Solver Notes — Claude Opus 4.6

## Parsing Approach

The solver reads the offline HTTP packet directory and processes three types of transcripts for each of the eight repos in the manifest: the GitHub API repo endpoint (`repos__*.http`), the Pages API endpoint (`pages__*.http`), and the public GitHub Pages HEAD response (`public__*.http`). Additionally, it processes user endpoint transcripts (`users__*.http`) for ghost detection.

Each HTTP transcript is parsed by first extracting the status code from the `HTTP/` status line using a regex, then locating the blank line separator (handling both LF and CRLF line endings) to split headers from the JSON body. For HEAD responses (public endpoints), only the status code and optional `Location` header are extracted since there is no JSON body.

## Edge Cases Handled

**Mixed line endings:** The parser uses `\r?\n\r?\n` to find the header-body separator, which correctly handles both LF-only and CRLF transcripts. Several files in the packet mix conventions (LF status line, CRLF headers).

**Non-standard Pages status:** The repo-health-dashboard has `"status": "building"` rather than `"built"`, which the solver preserves faithfully. The grader accepts this because the spec only checks `api_status` against the actual packet data, not a fixed enum.

**Non-default branch Pages source:** The lessons-from-293-days repo has `default_branch: "add-pages-source"` and Pages source on that same branch, so no `pages_source_non_default_branch` flag is raised despite the unusual branch name.

**Ghost detection:** Three of four expected logins (gpt-5-2, opus-4-5-claude-code, gemini-3-pro) return 404, while claude-sonnet-4-6 returns 200. The exact reason string from the spec is used verbatim.

**Sorting:** Both `repos` (alphabetical by name) and `ghost_accounts` (alphabetical by login) are sorted as required by the spec.

## Result

All eight repos analyzed, three ghost accounts detected, zero inconsistency flags. Score: 100/100.
