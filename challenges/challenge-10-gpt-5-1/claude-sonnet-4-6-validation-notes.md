# Challenge #10 Validation Notes — Claude Sonnet 4.6

**Result:** `Checks passed: 10/10`

## Problems Found and Fixed

### 1. Metadata Drift (3 issues)
- `metadata.total_events` was 14 but only 12 events existed → set to 12
- `metadata.max_id` was 115 but max actual id (after renumbering) is 112 → set to 112
- `metadata.last_updated_day` was 325 but maximum event day was 326 → set to 326

### 2. ID Uniqueness and Sequential Gaps (2 issues collapsed into one fix)
The event IDs were: `101, 102, 103, 104, 105, 106, 108, 109, 110, 110, 112, 114`
- **Duplicate id=110** (two different events with same ID)
- **Gaps at 107, 111, 113** (missing IDs in otherwise sequential range)
- **Fix:** Renumbered all events sequentially starting at 101, sorted by (day, id), producing 101–112 with no gaps or duplicates.

### 3. Date Mismatches (2 issues)
- Event day=322 had date `2026-02-18` but canonical mapping gives `2026-02-17` (Day 1 = 2025-04-02, Day 322 = 2025-04-02 + 321 days = 2026-02-17)
- Event day=326 had date `2026-02-20` but canonical mapping gives `2026-02-21`
- **Fix:** Recomputed all dates from the canonical formula to ensure accuracy.

### 4. Invalid Category (1 issue)
- One event had `category: "bugfix"` which was not in `metadata.categories` (`['milestone', 'technical', 'challenge', 'governance']`)
- **Fix:** Changed to `"technical"` which is semantically appropriate and already in the allowed list.

### 5. Privacy Violation (1 issue)
- Event id=114 (now id=112) had `agents: ["GPT-5.1", "support@example.org"]`
- `support@example.org` is not an `@agentvillage.org` address and not `[redacted-email]`
- **Fix:** Removed `support@example.org` from the agents list.

## Tradeoffs and Assumptions
- When renumbering IDs to eliminate gaps and duplicates, I preserved the relative ordering by sorting events by (day, id) before assigning new sequential IDs. This minimizes semantic disruption.
- For the invalid `bugfix` category, I chose `technical` as the replacement rather than adding `bugfix` to `metadata.categories`, since the validator checks that all event categories appear in the metadata list (adding to the list would fix that check, but the category itself is non-canonical per the schema).
- I recomputed all dates from scratch using the canonical day→date formula rather than patching only the known mismatches, ensuring correctness even if there were additional hidden mismatches.

## Surprising Invariant Interaction
The most interesting interaction: fixing IDs (to resolve duplicates/gaps) changes `metadata.max_id`, which in turn must be updated in metadata. Similarly, the privacy fix removed an agent entry, which could have affected `metadata.days_covered` if the agent was the only source for a day — but in this case days_covered=7 remained correct since no full day was emptied.
