#!/usr/bin/env python3
"""Village Event Log query tool.

Usage:
  python query_events.py /path/to/events.json [options]

Implements filtering, sorting, and formatting for AI Village events.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def parse_date(s: str) -> _dt.date:
    try:
        return _dt.date.fromisoformat(s)
    except Exception:
        raise argparse.ArgumentTypeError(f"Invalid date: {s!r}. Expected YYYY-MM-DD.")


def load_events(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Error: file not found: {path}")
    except PermissionError:
        raise SystemExit(f"Error: permission denied reading: {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Error: invalid JSON in {path}: {e}")

    if isinstance(obj, dict) and isinstance(obj.get("events"), list):
        events = obj["events"]
    elif isinstance(obj, list):
        events = obj
    else:
        raise SystemExit(
            "Error: expected events.json to be a list of events or an object with an 'events' array."
        )

    out: List[Dict[str, Any]] = []
    for ev in events:
        if isinstance(ev, dict):
            out.append(ev)
    return out


def ev_agents(ev: Dict[str, Any]) -> List[str]:
    a = ev.get("agents")
    if isinstance(a, list):
        return [x for x in a if isinstance(x, str)]
    a2 = ev.get("agents_involved")
    if isinstance(a2, list):
        return [x for x in a2 if isinstance(x, str)]
    return []


def filter_events(
    events: Sequence[Dict[str, Any]],
    agent: Optional[str],
    category: Optional[str],
    d_from: Optional[_dt.date],
    d_to: Optional[_dt.date],
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for ev in events:
        if agent is not None:
            if agent not in ev_agents(ev):
                continue
        if category is not None:
            if ev.get("category") != category:
                continue
        if d_from is not None or d_to is not None:
            ds = ev.get("date")
            if not isinstance(ds, str):
                continue
            try:
                d = _dt.date.fromisoformat(ds)
            except Exception:
                continue
            if d_from is not None and d < d_from:
                continue
            if d_to is not None and d > d_to:
                continue
        out.append(ev)
    return out


def sort_events(events: List[Dict[str, Any]], sort_mode: str) -> None:
    def key(ev: Dict[str, Any]):
        ds = ev.get("date")
        try:
            d = _dt.date.fromisoformat(ds) if isinstance(ds, str) else _dt.date.max
        except Exception:
            d = _dt.date.max
        ev_id = ev.get("id")
        try:
            ev_id_int = int(ev_id)
        except Exception:
            ev_id_int = 10**18
        return (d, ev_id_int)

    reverse = sort_mode == "date_desc"
    events.sort(key=key, reverse=reverse)


def format_table(events: Sequence[Dict[str, Any]]) -> str:
    # Required columns: ID, day, date, category, title, agents
    rows: List[List[str]] = []
    headers = ["ID", "day", "date", "category", "title", "agents"]
    rows.append(headers)

    for ev in events:
        ev_id = ev.get("id", "")
        day = ev.get("day", "")
        date = ev.get("date", "")
        cat = ev.get("category", "")
        title = ev.get("title", "")
        agents = ", ".join(ev_agents(ev))

        def s(x: Any) -> str:
            if x is None:
                return ""
            return str(x)

        rows.append([s(ev_id), s(day), s(date), s(cat), s(title), agents])

    # compute widths
    widths = [0] * len(headers)
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))

    out_lines: List[str] = []
    for idx, r in enumerate(rows):
        line = "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(r))
        out_lines.append(line.rstrip())
        if idx == 0:
            out_lines.append("  ".join("-" * widths[i] for i in range(len(headers))).rstrip())
    return "\n".join(out_lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="query_events.py",
        description="Query AI Village events.json with filters and output formats.",
    )
    p.add_argument("events_json", help="Path to village-event-log events.json")
    p.add_argument("--agent", help='Filter by agent name (exact match), e.g. --agent "Claude Opus 4.5"')
    p.add_argument("--category", help='Filter by category (exact match), e.g. --category "milestone"')
    p.add_argument("--from", dest="date_from", type=parse_date, help="Start date (inclusive), YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", type=parse_date, help="End date (inclusive), YYYY-MM-DD")
    p.add_argument("--limit", type=int, help="Limit number of returned events")
    p.add_argument("--format", choices=["json", "table"], default="table", help="Output format")
    p.add_argument("--count", action="store_true", help="Output only the count of matching events")
    p.add_argument("--sort", choices=["date_asc", "date_desc"], default="date_asc", help="Sort order")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.limit is not None and args.limit < 0:
        eprint("Error: --limit must be >= 0")
        return 2

    if args.date_from and args.date_to and args.date_from > args.date_to:
        eprint("Error: --from date must be <= --to date")
        return 2

    events = load_events(args.events_json)
    events = filter_events(events, args.agent, args.category, args.date_from, args.date_to)
    sort_events(events, args.sort)

    if args.limit is not None:
        events = events[: args.limit]

    if args.count:
        print(len(events))
        return 0

    if args.format == "json":
        print(json.dumps(events, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    print(format_table(events))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
