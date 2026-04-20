# Forensics Notes - Gemini 3 Pro

## Approach
My solution uses a custom HTTP parser (stdlib `json` and string manipulation) to process the raw packet files. 
1.  **Parsing**: Each `.http` file was split into headers and body. The body was parsed as JSON where applicable (status 200).
2.  **State Reconstruction**: For each repo, I triangulated the state from three sources:
    -   `repos__*.http`: Provided the `default_branch` and `has_pages` setting.
    -   `pages__*.http`: Provided the internal build status (`built`, `building`, etc.) and source config.
    -   `public__*.http`: Provided the external reality (200 OK vs 404).

## Edge Cases
-   **Pages 404 vs Not Found**: Distinct handling for when the Pages endpoint itself returns 404 (Pages disabled/never built) versus when it returns 200 but status is `null`.
-   **Ghost Detection**: strictly followed the rule: `users__<login>.http` == 404 AND login in `expected_logins.json`.

## Inconsistency Flags
Implemented logic to strictly match the requested flags, comparing `has_pages` boolean against the presence/absence of the Pages endpoint, and the build status against the public URL reachability.
