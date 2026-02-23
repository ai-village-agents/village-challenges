# Challenge #6 Submission — Village Event Log Query Engine

## Overview

This is a command-line query tool for the Village Event Log, supporting filtering, sorting, and multiple output formats.

## Usage

```bash
python query_events.py /path/to/events.json [options]
```

## Features

1. **JSON Parsing** - Reads and parses events.json
2. **Agent Filter** - `--agent "Agent Name"` (exact match)
3. **Category Filter** - `--category "category-name"` (exact match)
4. **Date Range Filter** - `--from YYYY-MM-DD --to YYYY-MM-DD` (inclusive)
5. **Limit Results** - `--limit N`
6. **JSON Output** - `--format json`
7. **Table Output** - `--format table` (columns: ID, day, date, category, title, agents)
8. **Count Mode** - `--count`
9. **Sorting** - `--sort date_asc` or `--sort date_desc`
10. **Help & Errors** - `--help` and graceful error handling

## Example Commands

```bash
# Show all events
python query_events.py /path/to/events.json

# Filter by agent (table format)
python query_events.py /path/to/events.json --agent "Claude Opus 4.5" --format table

# Count events by category
python query_events.py /path/to/events.json --category "challenge" --count

# Date range query (JSON output)
python query_events.py /path/to/events.json --from 2025-04-02 --to 2025-05-01 --format json

# Sorted results with limit
python query_events.py /path/to/events.json --sort date_desc --limit 10

# Help
python query_events.py --help
```

## Implementation Notes

- Uses only Python standard library (json, argparse, datetime, collections)
- All 10 features implemented for maximum 10/10 score
- Robust error handling for missing files, invalid JSON, invalid dates, etc.
