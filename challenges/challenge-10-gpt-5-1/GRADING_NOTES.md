# Grading Guidance — Challenge #10

## How to grade
- Use `scripts/validate_mini_events.py` as the only numeric source of truth. Run it on the submitted `*-mini-events-fixed.json` to obtain the score (Checks passed: X/10) and the PASS/FAIL status for each check.
- Do not adjust the score based on implementation style, narrative choices, or how the data is modeled, as long as the invariants are satisfied.
- Confirm the submitter also provided `*-validation-notes.md`; that file is pass/fail on existence and basic coherence only.
- If the validator exits successfully and reports 10/10, the submission passes the technical bar regardless of subjective impressions. If fewer checks pass, the numeric output is the grade.

## Interpreting each check
- `schema_valid` — Fails on any JSON Schema violation. If this fails, no manual partial credit; the validator’s PASS/FAIL stands.
- `metadata_totals_match` — `metadata.total_events` must exactly equal `len(events)` and be an integer. Any mismatch is a fail.
- `metadata_max_id_match` — Requires `metadata.max_id` to be an integer equal to the maximum `id` in events. If events are empty, it fails by design.
- `metadata_days_covered_match` — Compares `metadata.days_covered` to the count of distinct integer `day` values. Non-integer days are ignored for the count but will likely fail elsewhere; rely on the validator result.
- `ids_unique_and_sequential` — All `id` values must be positive integers, unique, and span a gap-free range from the minimum observed id through the maximum. The minimum may be any positive integer (not necessarily 1), but there can be no gaps inside the range.
- `day_date_consistency` — For each event, `date` must match the canonical mapping from `day` starting at 2025-04-02 (Day 1). Non-integer days or non-string dates are treated as mismatches. This is strict: no alternate calendars or offsets.
- `categories_valid` — `metadata.categories` must be present and non-empty. Every event category must appear in that list. Extra categories inside events cause failure; extra categories in metadata with no events are allowed.
- `privacy_emails_ok` — Flags any email-like string in descriptions, agents, or links unless it ends with `@agentvillage.org` or is `[redacted-email]`. Other domains (e.g., gmail.com) are not allowed. Mail-like patterns in surprising places (e.g., `mailto:` links) still count. The check only sees strings matching the regex; obfuscated forms without `@` will not be caught.
- `last_updated_day_consistent` — `metadata.last_updated_day` must be an integer equal to the maximum `day` across events. If events are empty, it fails.
- `events_sorted_by_day_then_id` — The `events` array must already be sorted by `(day, id)`. Any out-of-order pair fails, even if the content otherwise passes.

## Handling edge and borderline cases
- Submissions with `Checks passed: 10/10` pass regardless of unusual modeling choices, phrasing, or event text, provided nothing else in the rubric disqualifies them.
- If the validator output is below 10/10, use exactly that score; do not override based on intuition. Encourage resubmission if allowed.
- For `ids_unique_and_sequential`, accept any positive starting id as long as the sequence has no gaps (e.g., ids 5–12 inclusive are fine; 5,6,8 is not).
- For `privacy_emails_ok`, only email-like patterns matter. Addresses ending with `@agentvillage.org` or the literal `[redacted-email]` are permitted even if they look odd; other domains or unredacted emails fail.
- For `metadata_days_covered_match`, remember the validator counts distinct integer `day` values; stray non-integer days do not contribute to the count but may trip other checks.
- Sorting is pure order: even a single swapped pair fails `events_sorted_by_day_then_id` while other checks may still pass.

## Validation notes file
- Existence of `*-validation-notes.md` is required, but it is not scored for style. Check that it exists and is basically coherent (readable text referencing what was fixed). Do not grade writing quality or length beyond that.

## Grading posture
- Stay strictly aligned to the validator’s invariants; do not introduce subjective criteria about narrative, tone, or how the agent fixed the data.
- If the validator fails to run due to missing files or crashes, the submission does not meet the bar until it can produce a valid PASS/FAIL report.
- When in doubt on close calls, default to the validator output. The challenge is intentionally mechanical: reward satisfying the invariants, not creativity.
