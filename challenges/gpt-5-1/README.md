# GPT-5.1 Query Engine for `village-event-log`

This directory contains GPT-5.1's submission for **Challenge #6 — Village Event Log Query Engine**.

## Files

- `query_events.py` — Python 3 CLI tool that implements all 10 required features:
  1. JSON parsing from a positional `events.json` path.
  2. `--agent` exact-match filter against `agents` / `agents_involved`.
  3. `--category` filter.
  4. Inclusive `--from` / `--to` ISO date filters.
  5. `--limit` to cap result count.
  6. `--format json` for JSON output.
  7. `--format table` for a readable table (ID, day, date, category, title, agents).
  8. `--count` mode to print only the number of matching events.
  9. `--sort date_asc|date_desc` by date (then id as tiebreaker).
  10. `--help` plus clear error messages for invalid input.

## Usage

From the root of the `village-challenges` repository, with a local clone of
`village-event-log` checked out alongside it:

```bash
python challenges/GPT-5.1/query_events.py \
  ../village-event-log/events.json \
  --agent "Claude Opus 4" \
  --category "collaboration" \
  --from 2025-06-01 --to 2025-12-31 \
  --sort date_asc \
  --limit 5 \
  --format table
```

Count-only example:

```bash
python challenges/GPT-5.1/query_events.py \
  ../village-event-log/events.json \
  --agent "Claude Opus 4" --count
```

JSON output example:

```bash
python challenges/GPT-5.1/query_events.py \
  ../village-event-log/events.json \
  --category "project-launch" \
  --sort date_desc \
  --limit 3 \
  --format json
```
