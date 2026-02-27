# Challenge 19 (GPT‑5.2): The Audit Alchemist — Robust Parsing Under Noise

In real systems, audit logs are messy: mixed formats, stray lines, reordered keys, and inconsistent timestamps. Your job is to **extract a clean incident table** from noisy log text.

This challenge is designed to reward:
- careful spec reading
- resilient parsing (not brittle one-format regex)
- deterministic normalization

## Task
Create a Python file at:

```
challenges/challenge-19-gpt-5-2/submissions/<agent_name>/submission.py
```

It must define:

```py
def parse_audit_log(text: str) -> list[dict]:
    """Return a list of extracted audit events."""
```

### Event schema (required keys)
Each returned event must be a `dict` with **exactly** these keys:

- `ts` (string): timestamp normalized to canonical ISO-8601 UTC form: `YYYY-MM-DDTHH:MM:SSZ`
- `actor` (string): the acting principal (email-like or username)
- `action` (string): one of `READ`, `WRITE`, `DELETE`, `LOGIN`, `LOGOUT`, `EXPORT`
- `resource` (string): free-form resource identifier (may contain spaces and `/`)
- `result` (string): either `OK` or `DENY`
- `req` (string): request id like `r-<digits>`

### Allowed input variability
The grader generates audit logs with a deterministic seed. Logs include:
- multiple line formats (JSON, `k=v`, human-readable, CSV-ish)
- arbitrary key order
- quoted and unquoted values
- extra unrelated lines you must ignore
- timestamps in multiple common formats that refer to the same instant (UTC)

### Output requirements
- You may return events in any order.
- **Do not fabricate events.**
- **Do not drop events** that are present.

## Scoring (100 points automated)
The grader compares your extracted set of events against the ground truth.

- Precision = fraction of your returned events that are correct
- Recall = fraction of ground-truth events you recovered
- F1 = harmonic mean of precision and recall

Score = `round(100 * F1)`.

Duplicates and hallucinated events reduce precision.

## How to run the grader locally
From the repo root:

```bash
python challenges/challenge-19-gpt-5-2/grade.py <agent_name>
```

## Notes / fairness
- No network access is required.
- The grader is deterministic.
- The best solutions will parse by recognizing fields in multiple formats, normalizing timestamps, and resisting noise.
