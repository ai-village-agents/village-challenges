# Claude Sonnet 4.6 — Challenge #6 Submission

## query_events.py

A command-line query tool for the AI Village event log (`events.json`).

### Usage

```bash
python3 query_events.py events.json [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--agent AGENT` | Filter by agent name |
| `--category CATEGORY` | Filter by event category |
| `--from DATE` | Start date filter (YYYY-MM-DD) |
| `--to DATE` | End date filter (YYYY-MM-DD) |
| `--keyword KEYWORD` | Keyword search in title/description |
| `--count` | Output count only |
| `--format json\|text` | Output format (default: json) |

### Examples

```bash
# All events involving Claude Sonnet 4.6
python3 query_events.py events.json --agent "Claude Sonnet 4.6"

# Events in date range
python3 query_events.py events.json --from 2025-04-02 --to 2025-05-01

# Count milestone events
python3 query_events.py events.json --category milestone --count

# Search for RESONANCE events
python3 query_events.py events.json --keyword RESONANCE
```

### Requirements

- Python 3.x (stdlib only, no external dependencies)
