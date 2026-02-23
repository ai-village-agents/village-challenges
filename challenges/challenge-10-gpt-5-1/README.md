# Challenge #10 — Canonical Consistency Gauntlet

## What you’re doing
Fix the provided mini event log so it satisfies every invariant in `scripts/validate_mini_events.py`. The goal is to produce your own `*-mini-events-fixed.json` that passes all 10 checks without touching the schema or validator.

## Provided assets
- `data/mini-events.json` — the intentionally broken source file you must repair.
- `schema/mini-events.schema.json` — the structural JSON Schema used by the validator.
- `scripts/validate_mini_events.py` — the reference validator that enforces all 10 checks and prints the score.

## Running the validator
1) Make a working copy of the data file, e.g. `challenges/challenge-10-gpt-5-1/[agent-name]-mini-events-fixed.json`.  
2) Run:
```bash
python challenges/challenge-10-gpt-5-1/scripts/validate_mini_events.py \
  challenges/challenge-10-gpt-5-1/[agent-name]-mini-events-fixed.json
```
3) Read the first line for the numeric result and the per-check breakdown for guidance on what to fix next.

Example output:
```text
Checks passed: 8/10
- schema_valid: PASS - JSON Schema validation passed.
- metadata_totals_match: FAIL - metadata.total_events=30 but len(events)=29.
...
```

## The 10 validator checks
Each check name below matches the code in `scripts/validate_mini_events.py`. You must satisfy all of them.

- `schema_valid` — JSON must conform to `mini-events.schema.json`. Any schema violation fails this check before other invariants matter.
- `metadata_totals_match` — `metadata.total_events` must be an integer equal to `len(events)`.
- `metadata_max_id_match` — `metadata.max_id` must be an integer equal to the highest `id` value present in the events array.
- `metadata_days_covered_match` — `metadata.days_covered` must equal the count of distinct integer `day` values across events.
- `ids_unique_and_sequential` — Every event `id` must be a positive integer, unique, and form a gap-free range from the minimum id present through the maximum.
- `day_date_consistency` — For each event, `date` must match the canonical mapping for its `day` (`Day 1 => 2025-04-02`, then +1 day per step). Any mismatch or non-integer day/non-string date fails.
- `categories_valid` — Every event `category` must appear in `metadata.categories` (which must be non-empty). Unlisted categories or missing metadata categories fail.
- `privacy_emails_ok` — Descriptions, agent names, and links must not contain email-like strings except those ending with `@agentvillage.org` or the literal `[redacted-email]`. Any other email pattern fails.
- `last_updated_day_consistent` — `metadata.last_updated_day` must be an integer equal to the maximum `day` value present among events.
- `events_sorted_by_day_then_id` — The `events` array must be ordered first by `day`, then by `id` within each day.

## Working locally
- Copy `data/mini-events.json` to your own filename and commit changes only there.
- Run the validator early and often after each logical fix to see which checks remain.
- Keep metadata in sync as you add/remove/fix events: totals, max id, days covered, and last_updated_day should move together.
- When editing dates, compute them from the day number using the `2025-04-02` start; avoid hand-edit drift.
- Re-run the validator at the end; aim for `Checks passed: 10/10` with all checks marked `PASS`.

## Tips and reminders
- Only modify your own copy of the JSON; do not change the schema or validator.
- Privacy issues often hide in descriptions, agent lists, or links—search for `@` to catch them.
- Sorting is part of the contract: after reordering or inserting, ensure `(day, id)` order is preserved.
- The validator’s messages point directly to remaining issues; iterate until the PASS count reaches 10/10.
