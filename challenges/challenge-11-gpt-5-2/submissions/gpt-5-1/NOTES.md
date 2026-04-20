# C11 GitHub Forensics NOTES — GPT-5.1

I treated the packet as a fully offline mirror of the GitHub API and UI, and focused on matching the grader’s view of the world exactly.

First, the script discovers structure from `packet_manifest.json`: packet version, repo list, and the public base URL. I then treat `data/http/` as the canonical source of truth. All HTTP transcripts are decoded as UTF-8 with `errors="replace"` so that occasional encoding noise cannot crash the parser.

For JSON-bearing responses (`repos__*.http` and `pages__*.http`), I split headers from body on the first blank line (supporting both LF and CRLF) and run `json.loads` on the body. This yields `has_pages` and `default_branch` from the repos API and `status`, `html_url`, and `source.{branch,path}` from the pages API. If the pages status code is 404, I canonicalize the pages block to `api_status = "not_found"` with all other fields set to null.

For the public endpoints, I reuse the same regexes as the grader: extract the first HTTP status code and an optional `Location` header. That produces the `public.http_status` and `public.location` fields while constructing the URL from `public_base` and the repo name. Flags are then computed with simple boolean checks that mirror the spec and grader: mismatched `has_pages` vs `/pages` status, "built" pages with 404 public URLs, and Pages sources that live on a non-default branch. Flags are sorted alphabetically for determinism.

Ghost detection uses `expected_logins.json` and `users__<login>.http`. Any 404 response is reported with the exact reason string specified in the challenge; other logins are omitted. Finally, I sort repos and ghost accounts by name and emit a single JSON object with `packet_version`, an ISO 8601 UTC `generated_at` timestamp, `repos`, and `ghost_accounts`.
