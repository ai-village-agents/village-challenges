#!/usr/bin/env python3
"""Query tool for the AI Village event log (events.json).

This is a preparation version for Challenge #6 (Village Event Log Query Engine).
It is designed to satisfy the challenge spec:

1. JSON Parsing       - positional path to events.json
2. Agent Filter       - --agent "Claude Opus 4.5"
3. Category Filter    - --category "project-launch"
4. Date Range Filter  - --from YYYY-MM-DD --to YYYY-MM-DD (inclusive)
5. Limit Results      - --limit N
6. JSON Output        - --format json
7. Table Output       - --format table (ID, day, date, category, title, agents)
8. Count Mode         - --count
9. Sorting            - --sort date_asc | date_desc
10. Help & Errors     - --help plus informative error messages.

Once the challenge window opens, this script can be moved into
challenges/gpt-5-1/query_events.py in the village-challenges repo.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Iterable, List, Optional


class ArgumentError(Exception):
    """Custom exception for argument-related problems."""


class Parser(argparse.ArgumentParser):
    """ArgumentParser that raises on error instead of exiting immediately."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ArgumentError(message)


@dataclass
class Event:
    raw: Dict[str, Any]
    parsed_date: date

    @property
    def id(self) -> Any:
        return self.raw.get("id")

    @property
    def day(self) -> Any:
        return self.raw.get("day")

    @property
    def category(self) -> Any:
        return self.raw.get("category")

    @property
    def title(self) -> Any:
        return self.raw.get("title")

    @property
    def agents(self) -> List[str]:
        """Return the canonical agents list.

        For Challenge #6 scoring, only the primary "agents" field is
        considered. Some historical events also have an "agents_involved"
        field, but the official validator filters solely on "agents", so we
        intentionally mirror that behavior here.
        """
        agents = self.raw.get("agents")
        if isinstance(agents, list):
            return [str(a) for a in agents]
        return []


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = Parser(
        description=(
            "Query AI Village events.json with filters, sorting, and multiple output formats."
        ),
        add_help=False,
    )

    parser.add_argument(
        "events_path",
        help="Path to events.json (from village-event-log)",
    )

    parser.add_argument(
        "--agent",
        metavar="NAME",
        help="Filter events by agent name (exact match in agents/agents_involved)",
    )
    parser.add_argument(
        "--category",
        metavar="CATEGORY",
        help="Filter events by category (exact match)",
    )
    parser.add_argument(
        "--from",
        dest="date_from",
        metavar="YYYY-MM-DD",
        help="Filter events on or after this date (inclusive)",
    )
    parser.add_argument(
        "--to",
        dest="date_to",
        metavar="YYYY-MM-DD",
        help="Filter events on or before this date (inclusive)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="Limit number of events returned (applied after filters & sorting)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        help="Output format: json or table (default: table)",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Print only the count of matching events (ignores --format/--limit)",
    )
    parser.add_argument(
        "--sort",
        choices=["date_asc", "date_desc"],
        help="Sort events by date (and id as a tiebreaker)",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit",
    )

    return parser.parse_args(argv)


def load_events(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: failed to parse JSON from {path}: {e}", file=sys.stderr)
        sys.exit(1)

    # village-event-log/events.json is an object with an "events" array,
    # but be tolerant of a bare array root.
    if isinstance(data, dict) and "events" in data:
        events = data["events"]
    else:
        events = data

    if not isinstance(events, list):
        print(
            "Error: expected 'events' to be a list (or top-level JSON array)",
            file=sys.stderr,
        )
        sys.exit(1)

    return events


def parse_iso_date(s: str, context: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        print(f"Error: invalid date '{s}' in {context}; expected YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)


def wrap_events(raw_events: List[Dict[str, Any]]) -> List[Event]:
    wrapped: List[Event] = []
    for ev in raw_events:
        if not isinstance(ev, dict):
            print("Error: each event must be a JSON object.", file=sys.stderr)
            sys.exit(1)
        raw_date = ev.get("date")
        if not isinstance(raw_date, str):
            print(
                f"Error: event missing string 'date' field (id={ev.get('id')!r}).",
                file=sys.stderr,
            )
            sys.exit(1)
        d = parse_iso_date(raw_date, f"event id={ev.get('id')!r}")
        wrapped.append(Event(raw=ev, parsed_date=d))
    return wrapped


def filter_events(
    events: Iterable[Event],
    agent: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[Event]:
    result: List[Event] = []
    for ev in events:
        if agent is not None:
            if agent not in ev.agents:
                continue
        if category is not None:
            if ev.category != category:
                continue
        if date_from is not None and ev.parsed_date < date_from:
            continue
        if date_to is not None and ev.parsed_date > date_to:
            continue
        result.append(ev)
    return result


def sort_events(events: List[Event], sort_key: Optional[str]) -> List[Event]:
    if not sort_key:
        return events

    reverse = sort_key == "date_desc"

    # Sort by (date, id) for stability; id may be missing or non-int, so use a
    # fallback that keeps ordering predictable.
    def key(ev: Event):
        ev_id = ev.id
        try:
            numeric_id = int(ev_id)
        except (TypeError, ValueError):
            numeric_id = 0
        return (ev.parsed_date, numeric_id)

    return sorted(events, key=key, reverse=reverse)


def apply_limit(events: List[Event], limit: Optional[int]) -> List[Event]:
    if limit is None:
        return events
    if limit <= 0:
        return []
    return events[:limit]


def events_to_json_serializable(events: Iterable[Event]) -> List[Dict[str, Any]]:
    return [ev.raw for ev in events]


def format_table(events: List[Event]) -> str:
    # Prepare rows for table output.
    headers = ["ID", "Day", "Date", "Category", "Title", "Agents"]
    rows: List[List[str]] = []

    for ev in events:
        agents_str = ", ".join(ev.agents) if ev.agents else ""
        rows.append(
            [
                str(ev.id if ev.id is not None else ""),
                str(ev.day if ev.day is not None else ""),
                ev.parsed_date.isoformat(),
                str(ev.category if ev.category is not None else ""),
                str(ev.title if ev.title is not None else ""),
                agents_str,
            ]
        )

    # Compute column widths.
    cols = list(zip(*([headers] + rows))) if rows else [headers]
    widths = [max(len(str(cell)) for cell in col) for col in cols]

    def format_row(row: List[str]) -> str:
        return " | ".join(cell.ljust(width) for cell, width in zip(row, widths))

    lines = [format_row(headers)]
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(format_row(row))

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> None:
    try:
        args = parse_args(argv)
    except ArgumentError as e:
        print(f"Argument error: {e}", file=sys.stderr)
        sys.exit(2)

    raw_events = load_events(args.events_path)
    wrapped = wrap_events(raw_events)

    date_from = parse_iso_date(args.date_from, "--from") if args.date_from else None
    date_to = parse_iso_date(args.date_to, "--to") if args.date_to else None

    filtered = filter_events(
        wrapped,
        agent=args.agent,
        category=args.category,
        date_from=date_from,
        date_to=date_to,
    )

    if args.count:
        print(len(filtered))
        return

    sorted_events = sort_events(filtered, args.sort)
    limited = apply_limit(sorted_events, args.limit)

    if args.format == "json":
        json.dump(events_to_json_serializable(limited), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        output = format_table(limited)
        print(output)


if __name__ == "__main__":  # pragma: no cover
    main()
