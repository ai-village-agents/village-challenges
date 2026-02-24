#!/usr/bin/env python3
"""
Village Event Log Query Engine
Challenge #6 Submission by Opus 4.5 (Claude Code)

A command-line tool for filtering, sorting, and formatting village event data.
"""

import argparse
import json
import sys
from datetime import datetime


def load_events(filepath):
    """Load and parse events.json file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('events', [])
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def filter_by_agent(events, agent_name):
    """Filter events by exact agent name match."""
    return [e for e in events if agent_name in e.get('agents', [])]


def filter_by_category(events, category):
    """Filter events by category."""
    return [e for e in events if e.get('category') == category]


def filter_by_date_range(events, from_date, to_date):
    """Filter events by date range (inclusive)."""
    filtered = []
    for e in events:
        event_date = e.get('date', '')
        if event_date:
            if from_date and event_date < from_date:
                continue
            if to_date and event_date > to_date:
                continue
            filtered.append(e)
    return filtered


def sort_events(events, sort_order):
    """Sort events by date."""
    if sort_order == 'date_asc':
        return sorted(events, key=lambda e: (e.get('date', ''), e.get('id', 0)))
    elif sort_order == 'date_desc':
        return sorted(events, key=lambda e: (e.get('date', ''), e.get('id', 0)), reverse=True)
    return events


def format_as_json(events):
    """Output events as JSON."""
    return json.dumps(events, indent=2)


def format_as_table(events):
    """Output events as a human-readable table."""
    if not events:
        return "No events found."
    
    # Header
    lines = []
    lines.append(f"{'ID':<6} {'Day':<5} {'Date':<12} {'Category':<20} {'Title':<40} {'Agents'}")
    lines.append("-" * 120)
    
    for e in events:
        event_id = str(e.get('id', ''))[:6]
        day = str(e.get('day', ''))[:5]
        date = str(e.get('date', ''))[:12]
        category = str(e.get('category', ''))[:20]
        title = str(e.get('title', ''))[:40]
        agents = ', '.join(e.get('agents', []))[:30]
        lines.append(f"{event_id:<6} {day:<5} {date:<12} {category:<20} {title:<40} {agents}")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Query tool for village-event-log events.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_events.py events.json --agent "Claude Opus 4.5" --count
  python query_events.py events.json --category "project-launch" --limit 3 --format table
  python query_events.py events.json --from 2025-04-02 --to 2025-04-09 --format json
        """
    )
    
    parser.add_argument('filepath', help='Path to events.json file')
    parser.add_argument('--agent', help='Filter by exact agent name')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--from', dest='from_date', help='Filter events from date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--to', dest='to_date', help='Filter events to date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--limit', type=int, help='Limit number of results')
    parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')
    parser.add_argument('--count', action='store_true', help='Return only count of matching events')
    parser.add_argument('--sort', choices=['date_asc', 'date_desc'], help='Sort by date (asc=oldest first, desc=newest first)')
    
    args = parser.parse_args()
    
    # Validate date formats if provided
    for date_arg, date_val in [('--from', args.from_date), ('--to', args.to_date)]:
        if date_val:
            try:
                datetime.strptime(date_val, '%Y-%m-%d')
            except ValueError:
                print(f"Error: Invalid date format for {date_arg}: {date_val}. Use YYYY-MM-DD.", file=sys.stderr)
                sys.exit(1)
    
    # Load events
    events = load_events(args.filepath)
    
    # Apply filters
    if args.agent:
        events = filter_by_agent(events, args.agent)
    
    if args.category:
        events = filter_by_category(events, args.category)
    
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
    elif args.format == 'json':
        print(format_as_json(events))
    elif args.format == 'table':
        print(format_as_table(events))


if __name__ == '__main__':
    main()
