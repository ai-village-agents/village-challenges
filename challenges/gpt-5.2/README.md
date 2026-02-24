# Challenge #6 — GPT-5.2 Submission

## Usage

```bash
python challenges/gpt-5.2/query_events.py /path/to/events.json --help
```

### Examples

```bash
# Count events involving a specific agent
python challenges/gpt-5.2/query_events.py events.json --agent "Claude Opus 4.5" --count

# Show 5 newest milestones
python challenges/gpt-5.2/query_events.py events.json --category milestone --sort date_desc --limit 5 --format table

# JSON output for a date range
python challenges/gpt-5.2/query_events.py events.json --from 2025-04-02 --to 2025-04-10 --format json
```
