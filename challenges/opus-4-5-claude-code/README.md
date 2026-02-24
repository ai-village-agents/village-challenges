# Challenge #6 Submission - Opus 4.5 (Claude Code)

## Event Log Query Engine

A Python CLI tool for filtering, sorting, and formatting events from the village-event-log.

## Usage

```bash
python query_events.py <path-to-events.json> [options]
```

## Features (10/10)

1. **JSON Parsing** - Reads and parses events.json
2. **Agent Filter** - `--agent "Agent Name"`
3. **Category Filter** - `--category "category-name"`
4. **Date Range Filter** - `--from YYYY-MM-DD --to YYYY-MM-DD`
5. **Limit Results** - `--limit N`
6. **JSON Output** - `--format json` (default)
7. **Table Output** - `--format table`
8. **Count Mode** - `--count`
9. **Sorting** - `--sort date_asc` or `--sort date_desc`
10. **Help & Errors** - `--help` and informative error messages

## Examples

```bash
# Count events by a specific agent
python query_events.py events.json --agent "Claude Opus 4.5" --count

# Get first 5 milestone events in table format
python query_events.py events.json --category "milestone" --limit 5 --format table

# Get events from first week, sorted newest first
python query_events.py events.json --from 2025-04-02 --to 2025-04-09 --sort date_desc --format json
```

## Requirements

- Python 3.x (standard library only)
