# Challenge #6 Submission — Claude Opus 4.6

## Village Event Log Query Engine

A Python 3 CLI tool for querying `events.json` from the `village-event-log` repository.

### Usage

```bash
python query_events.py /path/to/events.json [options]
```

### Options

| Flag | Description | Example |
|------|-------------|---------|
| `--agent NAME` | Filter by agent name (exact match) | `--agent "Claude Opus 4.5"` |
| `--category CAT` | Filter by category | `--category "project-launch"` |
| `--from DATE` | Start date (inclusive, YYYY-MM-DD) | `--from 2025-04-02` |
| `--to DATE` | End date (inclusive, YYYY-MM-DD) | `--to 2025-04-10` |
| `--limit N` | Limit number of results | `--limit 5` |
| `--format FMT` | Output format: `json` or `table` | `--format table` |
| `--count` | Show only count of matching events | `--count` |
| `--sort ORDER` | Sort by date: `date_asc` or `date_desc` | `--sort date_desc` |
| `--help` | Show help text | |

### Examples

```bash
# Count events by Claude Opus 4.5
python query_events.py events.json --agent "Claude Opus 4.5" --count

# First 3 project-launch events, newest first, table format
python query_events.py events.json --category "project-launch" --limit 3 --sort date_desc --format table

# Events from the first week
python query_events.py events.json --from 2025-04-02 --to 2025-04-09 --format json
```

### Requirements

- Python 3.x (standard library only, no pip dependencies)
