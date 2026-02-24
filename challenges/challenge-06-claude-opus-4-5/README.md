# Village Event Log Query Engine

**Author:** Claude Opus 4.5  
**Challenge:** #6 - Day 329

## Usage

```bash
python query_events.py /path/to/events.json [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--agent NAME` | Filter by agent name (exact match) |
| `--category CAT` | Filter by event category |
| `--from DATE` | Filter from date (YYYY-MM-DD, inclusive) |
| `--to DATE` | Filter to date (YYYY-MM-DD, inclusive) |
| `--limit N` | Limit number of results |
| `--format {json,table}` | Output format (default: table) |
| `--count` | Output only count of matching events |
| `--sort {date_asc,date_desc}` | Sort by date |
| `--help` | Show help message |

## Examples

```bash
# Count events by Claude Opus 4.5
python query_events.py events.json --agent "Claude Opus 4.5" --count

# Get first 3 project-launch events sorted newest first
python query_events.py events.json --category "project-launch" --limit 3 --sort date_desc --format table

# Get events from first week of village
python query_events.py events.json --from 2025-04-02 --to 2025-04-09 --format json
```

## Features Implemented (10/10)

1. ✅ JSON Parsing - Read and parse events.json from file path
2. ✅ Agent Filter - Filter events by agent name
3. ✅ Category Filter - Filter events by category
4. ✅ Date Range Filter - Filter by date range (inclusive)
5. ✅ Limit Results - Limit number of returned events
6. ✅ JSON Output - Output in JSON format
7. ✅ Table Output - Human-readable table with ID, day, date, category, title, agents
8. ✅ Count Mode - Return only count of matching events
9. ✅ Sorting - Sort by date ascending or descending
10. ✅ Help & Errors - Help text and informative error messages
