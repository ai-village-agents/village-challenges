#!/usr/bin/env python3
"""
CLI for querying events stored in a JSON file.

Usage:
    python query_events.py events.json [options]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from typing import Any, Dict, Iterable, List, Optional


def parse_date_arg(value: str) -> dt.date:
    """Parse an ISO date string into a date object for argparse."""
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date: {value!r}. Use YYYY-MM-DD.") from exc


def load_events(path: str) -> List[Dict[str, Any]]:
    """Load events from the given JSON file, ensuring the expected structure."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse JSON: {exc}")

    events = payload.get("events")
    if not isinstance(events, list):
        raise SystemExit("Invalid events file: missing 'events' list.")
    return events


def parse_event_date(event: Dict[str, Any]) -> Optional[dt.date]:
    """Extract and parse the event date, returning None when not parseable."""
    value = event.get("date")
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def event_matches(event: Dict[str, Any], agent: Optional[str], category: Optional[str], start: Optional[dt.date], end: Optional[dt.date]) -> bool:
    """Apply agent/category/date filters to a single event."""
    if agent:
        agents = event.get("agents")
        if not isinstance(agents, list):
            return False
        if agent not in agents:
            return False

    if category:
        event_category = event.get("category")
        if event_category != category:
            return False

    event_date = parse_event_date(event)
    if start and (event_date is None or event_date < start):
        return False
    if end and (event_date is None or event_date > end):
        return False

    return True


def sort_events(events: Iterable[Dict[str, Any]], sort_order: Optional[str]) -> List[Dict[str, Any]]:
    """Sort events by date ascending or descending."""
    if not sort_order:
        return list(events)

    reverse = sort_order == "date_desc"
    sentinel = dt.date.min

    def key(event: Dict[str, Any]) -> dt.date:
        return parse_event_date(event) or sentinel

    return sorted(events, key=key, reverse=reverse)


def format_table(events: List[Dict[str, Any]]) -> str:
    """Render events in a simple table."""
    columns = [
        ("id", lambda e: str(e.get("id", ""))),
        ("day", lambda e: "" if e.get("day") is None else str(e.get("day"))),
        ("date", lambda e: e.get("date", "")),
        ("category", lambda e: e.get("category", "")),
        ("title", lambda e: e.get("title", "")),
        ("agents", lambda e: ", ".join(str(item) for item in e["agents"]) if isinstance(e.get("agents"), list) else ""),
    ]

    widths = []
    for header, getter in columns:
        max_width = max(len(header), *(len(str(getter(event))) for event in events)) if events else len(header)
        widths.append(max_width)

    header_line = "  ".join(header.ljust(width) for (header, _), width in zip(columns, widths))
    separator = "  ".join("-" * width for width in widths)
    rows = [
        "  ".join(str(getter(event)).ljust(width) for (_, getter), width in zip(columns, widths))
        for event in events
    ]

    body = "\n".join(rows)
    return "\n".join([header_line, separator, body]) if events else header_line + "\n" + separator


def build_parser() -> argparse.ArgumentParser:
    """Set up the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Query events from a JSON file.")
    parser.add_argument("events_file", help="Path to events.json.")
    parser.add_argument("--agent", help="Filter by agent (exact match).")
    parser.add_argument("--category", help="Filter by category (exact match).")
    parser.add_argument("--from", dest="from_date", type=parse_date_arg, help="Filter events on/after this date (YYYY-MM-DD).")
    parser.add_argument("--to", dest="to_date", type=parse_date_arg, help="Filter events on/before this date (YYYY-MM-DD).")
    parser.add_argument("--limit", type=int, help="Limit the number of results returned.")
    parser.add_argument("--format", choices=["json", "table"], default="table", help="Output format.")
    parser.add_argument("--count", action="store_true", help="Return only the count of matching events.")
    parser.add_argument("--sort", choices=["date_asc", "date_desc"], help="Sort results by date.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.limit is not None and args.limit < 0:
        print("Error: --limit must be non-negative.", file=sys.stderr)
        return 1

    events = load_events(args.events_file)
    filtered = [
        event
        for event in events
        if event_matches(event, args.agent, args.category, args.from_date, args.to_date)
    ]

    sorted_events = sort_events(filtered, args.sort)
    limited_events = sorted_events[: args.limit] if args.limit is not None else sorted_events

    if args.count:
        print(len(filtered))
        return 0

    if args.format == "json":
        json.dump(limited_events, sys.stdout, indent=2)
        print()
    else:
        print(format_table(limited_events))

    return 0


if __name__ == "__main__":
    sys.exit(main())
