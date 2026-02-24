#!/usr/bin/env python3

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Pattern

Event = Dict[str, Any]


def parse_date_arg(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Use YYYY-MM-DD.") from exc


def parse_regex(value: str) -> Pattern[str]:
    try:
        return re.compile(value)
    except re.error as exc:
        raise argparse.ArgumentTypeError(f"Invalid regex '{value}': {exc}") from exc


def parse_event_date(raw_value: Any) -> Optional[date]:
    if isinstance(raw_value, date):
        return raw_value
    if isinstance(raw_value, str):
        date_part = raw_value.split("T", 1)[0]
        try:
            return date.fromisoformat(date_part)
        except ValueError:
            return None
    return None


@dataclass
class QueryOptions:
    file: Path
    agent: Optional[str]
    category: Optional[str]
    date: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]
    limit: Optional[int]
    count: bool
    sort: Optional[str]
    output: str
    search: Optional[Pattern[str]]


def normalize_agents(event: Event) -> List[str]:
    if "agents" in event:
        agents_val = event.get("agents")
        if isinstance(agents_val, list):
            return [str(agent) for agent in agents_val]
        if agents_val is None:
            return []
        return [str(agents_val)]

    agent = event.get("agent")
    return [str(agent)] if agent is not None else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query village event logs.")
    parser.add_argument(
        "--file",
        default="village-event-log/events.json",
        help="Path to the events.json file.",
    )
    parser.add_argument("--agent", help="Filter by agent name.")
    parser.add_argument("--category", help="Filter by event category.")
    parser.add_argument("--date", type=parse_date_arg, help="Filter by date (YYYY-MM-DD).")
    parser.add_argument(
        "--start-date",
        dest="start_date",
        type=parse_date_arg,
        help="Filter for events on or after this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        dest="end_date",
        type=parse_date_arg,
        help="Filter for events on or before this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--search",
        type=parse_regex,
        help="Regex search within the event description.",
    )
    parser.add_argument("--limit", type=int, help="Limit number of results.")
    parser.add_argument("--count", action="store_true", help="Print count only.")
    parser.add_argument(
        "--sort",
        choices=["date", "date_asc", "date_desc", "agent", "category"],
        help="Sort results by the specified field.",
    )
    parser.add_argument(
        "--output",
        choices=["json", "csv", "table"],
        default="table",
        help="Output format.",
    )
    return parser.parse_args()


def load_events(path: Path) -> List[Event]:
    try:
        with path.open() as f:
            data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Events file not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Failed to parse JSON: {exc}")

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "events" in data and isinstance(data["events"], list):
        return data["events"]

    sys.exit("Unsupported events.json format. Expected a list or an object with an 'events' list.")


def filter_events(events: Iterable[Event], options: QueryOptions) -> List[Event]:
    results: List[Event] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if options.agent and options.agent not in normalize_agents(event):
            continue
        if options.category and str(event.get("category", "")) != options.category:
            continue
        if options.search:
            description = str(event.get("description", ""))
            if not options.search.search(description):
                continue

        event_date = parse_event_date(event.get("date"))
        if options.date and event_date != options.date:
            continue
        if event_date:
            if options.start_date and event_date < options.start_date:
                continue
            if options.end_date and event_date > options.end_date:
                continue
        elif options.start_date or options.end_date or options.date:
            continue

        results.append(event)
    return results


def sort_events(events: List[Event], sort_key: str) -> List[Event]:
    if sort_key in ("date", "date_asc", "date_desc"):
        reverse = sort_key == "date_desc"
        return sorted(
            events,
            key=lambda e: parse_event_date(e.get("date")) or date.min,
            reverse=reverse,
        )
    return sorted(events, key=lambda e: str(e.get(sort_key, "")))


def print_table(events: List[Event]) -> None:
    if not events:
        print("No events found.")
        return

    headers = ["date", "agents", "category"]
    rows = []
    for event in events:
        agents = ", ".join(normalize_agents(event))
        rows.append(
            [str(event.get("date", "")), agents, str(event.get("category", ""))]
        )
    widths = [max(len(row[idx]) for row in rows + [headers]) for idx in range(len(headers))]

    def fmt_row(row: List[str]) -> str:
        return " | ".join(val.ljust(widths[idx]) for idx, val in enumerate(row))

    separator = "-+-".join("-" * width for width in widths)
    print(fmt_row(headers))
    print(separator)
    for row in rows:
        print(fmt_row(row))


def print_csv(events: List[Event]) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow(["date", "agents", "category", "description"])
    for event in events:
        agents = ", ".join(normalize_agents(event))
        writer.writerow(
            [
                str(event.get("date", "")),
                agents,
                str(event.get("category", "")),
                str(event.get("description", "")),
            ]
        )


def main() -> None:
    args = parse_args()
    options = QueryOptions(
        file=Path(args.file),
        agent=args.agent,
        category=args.category,
        date=args.date,
        start_date=args.start_date,
        end_date=args.end_date,
        limit=args.limit,
        count=args.count,
        sort=args.sort,
        output=args.output,
        search=args.search,
    )

    events = load_events(options.file)
    events = filter_events(events, options)

    if options.sort:
        events = sort_events(events, options.sort)
    if options.limit is not None and options.limit >= 0:
        events = events[: options.limit]

    if options.count:
        print(len(events))
        return

    if options.output == "json":
        json.dump(events, sys.stdout, indent=2)
        print()
    elif options.output == "csv":
        print_csv(events)
    else:
        print_table(events)


if __name__ == "__main__":
    main()
