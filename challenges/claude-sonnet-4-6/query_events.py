#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from typing import Any, Iterable, List, Optional

DATE_FMT = "%Y-%m-%d"


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_date(value: str, label: str) -> datetime:
    try:
        return datetime.strptime(value, DATE_FMT)
    except ValueError:
        raise ValueError(f"Invalid {label} date format: {value!r}. Expected YYYY-MM-DD")


def load_events(path: str) -> List[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}")

    if isinstance(data, list):
        events = data
    elif isinstance(data, dict) and "events" in data:
        events = data.get("events")
    else:
        raise ValueError("events.json must be a list or a dict with an 'events' key")

    if not isinstance(events, list):
        raise ValueError("'events' must be a list")

    for i, ev in enumerate(events):
        if not isinstance(ev, dict):
            raise ValueError(f"Event at index {i} is not an object")
    return events


def normalize_agents(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        return [value]
    return [str(value)]


def event_date(ev: dict, index: int) -> datetime:
    raw = ev.get("date")
    if not isinstance(raw, str):
        raise ValueError(f"Event at index {index} has invalid or missing 'date' field")
    try:
        return datetime.strptime(raw, DATE_FMT)
    except ValueError:
        raise ValueError(f"Event at index {index} has invalid date: {raw!r}")


def filter_events(
    events: List[dict],
    agent: Optional[str],
    category: Optional[str],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> List[dict]:
    out: List[dict] = []
    for i, ev in enumerate(events):
        if agent is not None:
            agents = normalize_agents(ev.get("agents"))
            if agent not in agents:
                continue
        if category is not None:
            if ev.get("category") != category:
                continue
        if date_from is not None or date_to is not None:
            d = event_date(ev, i)
            if date_from is not None and d < date_from:
                continue
            if date_to is not None and d > date_to:
                continue
        out.append(ev)
    return out


def sort_events(events: List[dict], mode: Optional[str]) -> List[dict]:
    if mode is None:
        return events
    reverse = False
    if mode == "date_desc":
        reverse = True
    elif mode == "date_asc":
        reverse = False
    else:
        raise ValueError("Invalid --sort value. Use 'date_asc' or 'date_desc'")

    def key_fn(item: dict, idx: int) -> datetime:
        return event_date(item, idx)

    indexed = list(enumerate(events))
    try:
        indexed.sort(key=lambda pair: key_fn(pair[1], pair[0]), reverse=reverse)
    except ValueError as exc:
        raise ValueError(str(exc))
    return [ev for _, ev in indexed]


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def format_table(events: List[dict]) -> str:
    header = "ID | Day | Date | Category | Title | Agents"
    lines = [header, "-" * len(header)]
    for i, ev in enumerate(events):
        ev_id = ev.get("id", "")
        date_raw = ev.get("date", "")
        day = ev.get("day", "")
        category = ev.get("category", "")
        title = ev.get("title", "")
        if not isinstance(title, str):
            title = str(title)
        title = truncate(title, 40)
        agents = ", ".join(normalize_agents(ev.get("agents")))
        line = f"{ev_id} | {day} | {date_raw} | {category} | {title} | {agents}"
        lines.append(line)
    lines.append(f"Total: {len(events)}")
    return "\n".join(lines)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Query and filter events.json")
    parser.add_argument("path", help="Path to events.json")
    parser.add_argument("--agent", help="Filter events by agent name")
    parser.add_argument("--category", help="Filter events by category")
    parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="date_to", help="End date YYYY-MM-DD")
    parser.add_argument("--limit", type=int, help="Limit to first N results")
    parser.add_argument("--format", choices=["json", "table"], default="json")
    parser.add_argument("--count", action="store_true", help="Print only count")
    parser.add_argument("--sort", choices=["date_asc", "date_desc"], help="Sort by date")

    args = parser.parse_args(argv)

    try:
        events = load_events(args.path)
        date_from = parse_date(args.date_from, "--from") if args.date_from else None
        date_to = parse_date(args.date_to, "--to") if args.date_to else None
        if date_from and date_to and date_from > date_to:
            raise ValueError("--from must be earlier than or equal to --to")

        events = filter_events(events, args.agent, args.category, date_from, date_to)
        events = sort_events(events, args.sort)
        if args.limit is not None:
            if args.limit < 0:
                raise ValueError("--limit must be >= 0")
            events = events[: args.limit]

        if args.count:
            print(len(events))
            return 0

        if args.format == "json":
            json.dump(events, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
        else:
            print(format_table(events))
        return 0
    except (FileNotFoundError, ValueError) as exc:
        eprint(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
