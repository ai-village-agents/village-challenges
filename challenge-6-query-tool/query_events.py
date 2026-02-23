import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


def normalize_agents(event: Dict[str, Any]) -> List[str]:
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
    parser.add_argument("--date", help="Filter by date (YYYY-MM-DD).")
    parser.add_argument("--limit", type=int, help="Limit number of results.")
    parser.add_argument("--count", action="store_true", help="Print count only.")
    parser.add_argument(
        "--sort",
        choices=["date", "agent", "category"],
        help="Sort results by the specified field.",
    )
    parser.add_argument(
        "--output",
        choices=["json", "table"],
        default="table",
        help="Output format.",
    )
    return parser.parse_args()


def load_events(path: Path) -> List[Dict[str, Any]]:
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


def filter_events(events: Iterable[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for event in events:
        if args.agent and args.agent not in normalize_agents(event):
            continue
        if args.category and str(event.get("category")) != args.category:
            continue
        if args.date:
            date_val = str(event.get("date", ""))
            if not date_val.startswith(args.date):
                continue
        results.append(event)
    return results


def sort_events(events: List[Dict[str, Any]], sort_key: str) -> List[Dict[str, Any]]:
    return sorted(events, key=lambda e: str(e.get(sort_key, "")))


def print_table(events: List[Dict[str, Any]]) -> None:
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


def main() -> None:
    args = parse_args()
    events = load_events(Path(args.file))
    events = filter_events(events, args)

    if args.sort:
        events = sort_events(events, args.sort)
    if args.limit is not None and args.limit >= 0:
        events = events[: args.limit]

    if args.count:
        print(len(events))
        return

    if args.output == "json":
        json.dump(events, sys.stdout, indent=2)
        print()
    else:
        print_table(events)


if __name__ == "__main__":
    main()
