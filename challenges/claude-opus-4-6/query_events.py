#!/usr/bin/env python3
"""
Village Event Log Query Engine
Challenge #6 submission by Claude Opus 4.6

A command-line query tool for filtering, sorting, and formatting
events from the AI Village event log.

Usage:
    python query_events.py /path/to/events.json [options]

Options:
    --agent NAME        Filter events by agent name (exact match)
    --category CAT      Filter events by category
    --from DATE         Filter events from this date (YYYY-MM-DD, inclusive)
    --to DATE           Filter events to this date (YYYY-MM-DD, inclusive)
    --limit N           Limit number of returned events
    --format FMT        Output format: 'json' or 'table' (default: table)
    --count             Return only the count of matching events
    --sort ORDER        Sort events: 'date_asc' or 'date_desc'
    --help              Show this help message
"""

import argparse
import json
import sys
from datetime import datetime


def load_events(filepath):
    """Load and parse events.json, returning the events list."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle both list format and dict-with-events format
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'events' in data:
        return data['events']
    else:
        print("Error: Unexpected JSON structure. Expected list or dict with 'events' key.", file=sys.stderr)
        sys.exit(1)


def filter_by_agent(events, agent_name):
    """Filter events where agent_name appears in the agents field."""
    result = []
    for e in events:
        agents = e.get('agents', '')
        if agent_name in agents:
            result.append(e)
    return result


def filter_by_category(events, category):
    """Filter events by exact category match."""
    return [e for e in events if e.get('category') == category]


def filter_by_date_range(events, from_date=None, to_date=None):
    """Filter events by inclusive date range (YYYY-MM-DD strings)."""
    result = []
    for e in events:
        event_date = e.get('date', '')
        if not event_date:
            continue
        if from_date and event_date < from_date:
            continue
        if to_date and event_date > to_date:
            continue
        result.append(e)
    return result


def sort_events(events, order):
    """Sort events by date. order: 'date_asc' or 'date_desc'."""
    if order == 'date_asc':
        return sorted(events, key=lambda e: (e.get('date', ''), e.get('id', 0)))
    elif order == 'date_desc':
        return sorted(events, key=lambda e: (e.get('date', ''), e.get('id', 0)), reverse=True)
    else:
        print(f"Error: Invalid sort order '{order}'. Use 'date_asc' or 'date_desc'.", file=sys.stderr)
        sys.exit(1)


def format_agents(agents):
    """Format agents field for table display."""
    if isinstance(agents, list):
        return ', '.join(agents[:3])
        # Truncate if too many agents
    elif isinstance(agents, str):
        return agents[:50]
    return ''


def output_json(events):
    """Output events as JSON to stdout."""
    print(json.dumps(events, indent=2, ensure_ascii=False))


def output_table(events):
    """Output events as a human-readable table."""
    if not events:
        print("No events found.")
        return

    # Define columns
    headers = ['ID', 'Day', 'Date', 'Category', 'Title', 'Agents']

    # Calculate column widths
    rows = []
    for e in events:
        agents_str = format_agents(e.get('agents', ''))
        title = e.get('title', '')
        if len(title) > 50:
            title = title[:47] + '...'
        if len(agents_str) > 40:
            agents_str = agents_str[:37] + '...'
        rows.append([
            str(e.get('id', '')),
            str(e.get('day', '')),
            e.get('date', ''),
            e.get('category', ''),
            title,
            agents_str
        ])

    # Calculate widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Print header
    header_line = ' | '.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print('-+-'.join('-' * w for w in widths))

    # Print rows
    for row in rows:
        print(' | '.join(cell.ljust(widths[i]) for i, cell in enumerate(row)))


def validate_date(date_str):
    """Validate date format YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)


def create_parser():
    """Create argument parser with help text."""
    parser = argparse.ArgumentParser(
        prog='query_events.py',
        description='Village Event Log Query Engine - Filter, sort, and format AI Village events.',
        epilog='Examples:\n'
               '  python query_events.py events.json --agent "Claude Opus 4.5" --count\n'
               '  python query_events.py events.json --category "project-launch" --limit 3 --sort date_desc --format table\n'
               '  python query_events.py events.json --from 2025-04-02 --to 2025-04-09 --format json\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('events_file', help='Path to events.json file')
    parser.add_argument('--agent', help='Filter events by agent name (exact match in agents list)')
    parser.add_argument('--category', help='Filter events by category (exact match)')
    parser.add_argument('--from', dest='from_date', help='Filter events from this date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--to', dest='to_date', help='Filter events to this date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--limit', type=int, help='Limit number of returned events')
    parser.add_argument('--format', dest='output_format', choices=['json', 'table'], default='table',
                        help='Output format: json or table (default: table)')
    parser.add_argument('--count', action='store_true', help='Return only the count of matching events')
    parser.add_argument('--sort', choices=['date_asc', 'date_desc'],
                        help='Sort events by date: date_asc (oldest first) or date_desc (newest first)')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Load events
    events = load_events(args.events_file)

    # Apply filters
    if args.agent:
        events = filter_by_agent(events, args.agent)

    if args.category:
        events = filter_by_category(events, args.category)

    if args.from_date:
        validate_date(args.from_date)
    if args.to_date:
        validate_date(args.to_date)
    if args.from_date or args.to_date:
        events = filter_by_date_range(events, args.from_date, args.to_date)

    # Apply sorting
    if args.sort:
        events = sort_events(events, args.sort)

    # Apply limit
    if args.limit is not None:
        if args.limit < 0:
            print("Error: --limit must be a non-negative integer.", file=sys.stderr)
            sys.exit(1)
        events = events[:args.limit]

    # Output
    if args.count:
        print(len(events))
    elif args.output_format == 'json':
        output_json(events)
    else:
        output_table(events)


if __name__ == '__main__':
    main()
