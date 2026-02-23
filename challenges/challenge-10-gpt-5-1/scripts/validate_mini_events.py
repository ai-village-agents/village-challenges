#!/usr/bin/env python
"""Reference validator for Challenge #10 — Canonical Consistency Gauntlet.

Usage:

  python challenges/challenge-10-gpt-5-1/scripts/validate_mini_events.py \
    challenges/challenge-10-gpt-5-1/[agent-name]-mini-events-fixed.json

This script:
- Validates the input JSON against mini-events.schema.json
- Enforces additional invariants inspired by village-event-log
- Prints a 10-check PASS/FAIL report with a numeric score
"""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    print("ERROR: jsonschema package not installed. Install with 'pip install jsonschema' and retry.")
    sys.exit(1)


CHECK_NAMES = [
    "schema_valid",
    "metadata_totals_match",
    "metadata_max_id_match",
    "metadata_days_covered_match",
    "ids_unique_and_sequential",
    "day_date_consistency",
    "categories_valid",
    "privacy_emails_ok",
    "last_updated_day_consistent",
    "events_sorted_by_day_then_id",
]


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse JSON from {path}: {e}")


def compute_expected_date_for_day(day: int) -> str:
    """Canonical day→date mapping: Day 1 = 2025-04-02."""
    if day < 1:
        raise ValueError(f"Day must be >= 1, got {day}")
    start = date(2025, 4, 2)
    return (start + timedelta(days=day - 1)).isoformat()


EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")


def check_schema_valid(data, schema, results):
    name = "schema_valid"
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        results[name] = (False, f"JSON Schema validation failed: {e.message}")
    else:
        results[name] = (True, "JSON Schema validation passed.")


def check_metadata_totals(data, results):
    name = "metadata_totals_match"
    metadata = data.get("metadata", {})
    events = data.get("events", [])
    total_events = metadata.get("total_events")
    if not isinstance(total_events, int):
        results[name] = (False, "metadata.total_events is missing or not an integer.")
        return
    if total_events != len(events):
        results[name] = (
            False,
            f"metadata.total_events={total_events} but len(events)={len(events)}.",
        )
    else:
        results[name] = (True, "metadata.total_events matches len(events).")


def check_metadata_max_id(data, results):
    name = "metadata_max_id_match"
    metadata = data.get("metadata", {})
    events = data.get("events", [])
    max_id_meta = metadata.get("max_id")
    if not isinstance(max_id_meta, int):
        results[name] = (False, "metadata.max_id is missing or not an integer.")
        return
    if not events:
        results[name] = (False, "No events present to compare with metadata.max_id.")
        return
    max_id_actual = max(e.get("id", 0) for e in events)
    if max_id_meta != max_id_actual:
        results[name] = (
            False,
            f"metadata.max_id={max_id_meta} but actual max id={max_id_actual}.",
        )
    else:
        results[name] = (True, "metadata.max_id matches actual maximum event id.")


def check_metadata_days_covered(data, results):
    name = "metadata_days_covered_match"
    metadata = data.get("metadata", {})
    events = data.get("events", [])
    days_meta = metadata.get("days_covered")
    if not isinstance(days_meta, int):
        results[name] = (False, "metadata.days_covered is missing or not an integer.")
        return
    distinct_days = {e.get("day") for e in events if isinstance(e.get("day"), int)}
    if days_meta != len(distinct_days):
        results[name] = (
            False,
            f"metadata.days_covered={days_meta} but distinct event days={len(distinct_days)}.",
        )
    else:
        results[name] = (True, "metadata.days_covered matches number of distinct event days.")


def check_ids_unique_and_sequential(data, results):
    name = "ids_unique_and_sequential"
    events = data.get("events", [])
    ids = [e.get("id") for e in events]
    if any(not isinstance(i, int) or i < 1 for i in ids):
        results[name] = (False, "All event ids must be positive integers.")
        return
    unique_ids = set(ids)
    if len(unique_ids) != len(ids):
        results[name] = (False, "Event ids are not unique.")
        return
    min_id, max_id = min(unique_ids), max(unique_ids)
    expected = set(range(min_id, max_id + 1))
    if unique_ids != expected:
        results[name] = (
            False,
            f"Event ids are not sequential from {min_id} to {max_id} without gaps.",
        )
    else:
        results[name] = (True, "Event ids are unique and sequential with no gaps.")


def check_day_date_consistency(data, results):
    name = "day_date_consistency"
    events = data.get("events", [])
    mismatches = []
    for e in events:
        day = e.get("day")
        date_str = e.get("date")
        if not isinstance(day, int) or not isinstance(date_str, str):
            mismatches.append(e.get("id"))
            continue
        expected = compute_expected_date_for_day(day)
        if date_str != expected:
            mismatches.append(e.get("id"))
    if mismatches:
        results[name] = (
            False,
            f"Day/date mismatches detected for event ids: {sorted(mismatches)}.",
        )
    else:
        results[name] = (True, "All events have day/date values consistent with canonical mapping.")


def check_categories_valid(data, results):
    name = "categories_valid"
    metadata = data.get("metadata", {})
    events = data.get("events", [])
    allowed = set(metadata.get("categories") or [])
    if not allowed:
        results[name] = (False, "metadata.categories is empty or missing.")
        return
    invalid = {}
    for e in events:
        cat = e.get("category")
        if cat not in allowed:
            invalid.setdefault(cat, 0)
            invalid[cat] += 1
    if invalid:
        parts = [f"{cat} ({count} events)" for cat, count in sorted(invalid.items())]
        results[name] = (
            False,
            "Found categories not listed in metadata.categories: " + ", ".join(parts),
        )
    else:
        results[name] = (True, "All event categories are present in metadata.categories.")


def check_privacy_emails_ok(data, results):
    name = "privacy_emails_ok"
    events = data.get("events", [])
    violations = []

    def record_violation(eid, value):
        violations.append((eid, value))

    for e in events:
        eid = e.get("id")
        # Check description text
        desc = e.get("description") or ""
        for match in EMAIL_PATTERN.findall(desc):
            if not (match.endswith("@agentvillage.org") or match == "[redacted-email]"):
                record_violation(eid, match)
        # Check agents list
        for a in e.get("agents") or []:
            for match in EMAIL_PATTERN.findall(a):
                if not (match.endswith("@agentvillage.org") or match == "[redacted-email]"):
                    record_violation(eid, match)
        # Check links (in case someone inlines a mailto or similar)
        for link in e.get("links") or []:
            for match in EMAIL_PATTERN.findall(link):
                if not (match.endswith("@agentvillage.org") or match == "[redacted-email]"):
                    record_violation(eid, match)

    if violations:
        formatted = ", ".join(
            f"id {eid}: {email}" for eid, email in violations
        )
        results[name] = (
            False,
            "Found non-@agentvillage.org or unredacted emails: " + formatted,
        )
    else:
        results[name] = (True, "All emails are @agentvillage.org or properly redacted.")


def check_last_updated_day_consistent(data, results):
    name = "last_updated_day_consistent"
    metadata = data.get("metadata", {})
    events = data.get("events", [])
    lud = metadata.get("last_updated_day")
    if not isinstance(lud, int):
        results[name] = (False, "metadata.last_updated_day is missing or not an integer.")
        return
    if not events:
        results[name] = (False, "No events present to compare with metadata.last_updated_day.")
        return
    max_day = max(e.get("day", 0) for e in events)
    if lud != max_day:
        results[name] = (
            False,
            f"metadata.last_updated_day={lud} but maximum event day={max_day}.",
        )
    else:
        results[name] = (True, "metadata.last_updated_day matches maximum event day.")


def check_events_sorted(data, results):
    name = "events_sorted_by_day_then_id"
    events = data.get("events", [])
    key = lambda e: (e.get("day", 0), e.get("id", 0))
    sorted_events = sorted(events, key=key)
    if events != sorted_events:
        results[name] = (
            False,
            "Events array is not sorted by (day, id).",
        )
    else:
        results[name] = (True, "Events are sorted by (day, id).")


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print("Usage: python challenges/challenge-10-gpt-5-1/scripts/validate_mini_events.py <path-to-mini-events.json>")
        return 1

    data_path = Path(argv[0]).resolve()
    if not data_path.is_file():
        print(f"ERROR: File not found: {data_path}")
        return 1

    script_path = Path(__file__).resolve()
    schema_path = script_path.parent.parent / "schema" / "mini-events.schema.json"
    if not schema_path.is_file():
        print(f"ERROR: Schema file not found at {schema_path}")
        return 1

    data = load_json(data_path)
    schema = load_json(schema_path)

    results = {}

    # Run checks
    check_schema_valid(data, schema, results)
    check_metadata_totals(data, results)
    check_metadata_max_id(data, results)
    check_metadata_days_covered(data, results)
    check_ids_unique_and_sequential(data, results)
    check_day_date_consistency(data, results)
    check_categories_valid(data, results)
    check_privacy_emails_ok(data, results)
    check_last_updated_day_consistent(data, results)
    check_events_sorted(data, results)

    # Ensure all expected checks present
    for name in CHECK_NAMES:
        if name not in results:
            results[name] = (False, "Check did not run (internal error).")

    passed = sum(1 for ok, _ in results.values() if ok)
    total = len(results)

    # Summary line first (as used in challenge scoring)
    print(f"Checks passed: {passed}/{total}")

    # Per-check breakdown in a stable order
    for name in CHECK_NAMES:
        ok, message = results[name]
        status = "PASS" if ok else "FAIL"
        print(f"- {name}: {status} - {message}")

    return 0 if passed == total else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
