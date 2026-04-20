#!/usr/bin/env python3
"""
Village Event Log Query Engine
Challenge #6 - Day 329
Author: Claude Opus 4.5

A command-line tool to filter, sort, and format events from village-event-log.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

def load_events(filepath: str) -> List[Dict[str, Any]]:
    """Load and parse events.json from file path."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle both direct list and {"events": [...]} formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'events' in data:
        return data['events']
    else:
        print("Error: Invalid events.json structure", file=sys.stderr)
        sys.exit(1)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def filter_by_agent(events: List[Dict], agent: str) -> List[Dict]:
    """Filter events by agent name (exact match in agents list)."""
    filtered = []
    for event in events:
        agents = event.get('agents', [])
        if isinstance(agents, list) and agent in agents:
            filtered.append(event)
        elif isinstance(agents, str) and agents == agent:
            filtered.append(event)
    return filtered

def filter_by_category(events: List[Dict], category: str) -> List[Dict]:
    """Filter events by category (exact match)."""
    return [e for e in events if e.get('category') == category]

def filter_by_date_range(events: List[Dict], from_date: Optional[str], to_date: Optional[str]) -> List[Dict]:
    """Filter events by date range (inclusive)."""
    filtered = []
    
    from_dt = parse_date(from_date) if from_date else None
    to_dt = parse_date(to_date) if to_date else None
    
    if from_date and from_dt is None:
        print(f"Error: Invalid from date format: {from_date}. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)
    if to_date and to_dt is None:
        print(f"Error: Invalid to date format: {to_date}. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)
    
    for event in events:
        event_date_str = event.get('date', '')
        event_dt = parse_date(event_date_str)
        if event_dt is None:
            continue
        
        if from_dt and event_dt < from_dt:
            continue
        if to_dt and event_dt > to_dt:
            continue
        
        filtered.append(event)
    
    return filtered

def sort_events(events: List[Dict], sort_order: str) -> List[Dict]:
    """Sort events by date (ascending or descending)."""
    def get_date_key(event):
        date_str = event.get('date', '1970-01-01')
        dt = parse_date(date_str)
        return dt if dt else datetime(1970, 1, 1)
    
    if sort_order == 'date_asc':
        return sorted(events, key=get_date_key)
    elif sort_order == 'date_desc':
        return sorted(events, key=get_date_key, reverse=True)
    else:
        print(f"Error: Invalid sort order: {sort_order}. Use 'date_asc' or 'date_desc'.", file=sys.stderr)
        sys.exit(1)

def format_table(events: List[Dict]) -> str:
    """Format events as human-readable table."""
    if not events:
        return "No events found."
    
    # Define columns: ID, day, date, category, title, agents
    headers = ['ID', 'Day', 'Date', 'Category', 'Title', 'Agents']
    
    # Calculate column widths
    rows = []
    for e in events:
        agents = e.get('agents', [])
        if isinstance(agents, list):
            agents_str = ', '.join(str(a) for a in agents[:3])
            if len(agents) > 3:
                agents_str += '...'
        else:
            agents_str = str(agents)
        
        title = e.get('title', '')
        if len(title) > 40:
            title = title[:37] + '...'
        
        row = [
            str(e.get('id', '')),
            str(e.get('day', '')),
            str(e.get('date', '')),
            str(e.get('category', '')),
            title,
            agents_str
        ]
        rows.append(row)
    
    # Calculate widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    
    # Build table
    lines = []
    
    # Header
    header_line = ' | '.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    
    # Separator
    sep_line = '-+-'.join('-' * w for w in widths)
    lines.append(sep_line)
    
    # Rows
    for row in rows:
        row_line = ' | '.join(cell.ljust(widths[i]) for i, cell in enumerate(row))
        lines.append(row_line)
    
    return '\n'.join(lines)

def format_json(events: List[Dict]) -> str:
    """Format events as JSON."""
    return json.dumps(events, indent=2)

def main():
    parser = argparse.ArgumentParser(
        description='Village Event Log Query Engine - Query and filter village events',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s events.json --agent "Claude Opus 4.5" --count
  %(prog)s events.json --category "project-launch" --limit 3 --format table
  %(prog)s events.json --from 2025-04-02 --to 2025-04-09 --format json
        '''
    )
    
    parser.add_argument('events_file', help='Path to events.json file')
    parser.add_argument('--agent', help='Filter by agent name (exact match)')
    parser.add_argument('--category', help='Filter by event category')
    parser.add_argument('--from', dest='from_date', help='Filter from date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--to', dest='to_date', help='Filter to date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--limit', type=int, help='Limit number of results')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                        help='Output format (default: table)')
    parser.add_argument('--count', action='store_true', help='Output only count of matching events')
    parser.add_argument('--sort', choices=['date_asc', 'date_desc'],
                        help='Sort by date (date_asc=oldest first, date_desc=newest first)')
    
    args = parser.parse_args()
    
    # Feature 1: JSON Parsing
    events = load_events(args.events_file)
    
    # Feature 2: Agent Filter
    if args.agent:
        events = filter_by_agent(events, args.agent)
    
    # Feature 3: Category Filter
    if args.category:
        events = filter_by_category(events, args.category)
    
    # Feature 4: Date Range Filter
    if args.from_date or args.to_date:
        events = filter_by_date_range(events, args.from_date, args.to_date)
    
    # Feature 9: Sorting
    if args.sort:
        events = sort_events(events, args.sort)
    
    # Feature 5: Limit Results
    if args.limit is not None:
        if args.limit < 0:
            print("Error: Limit must be non-negative.", file=sys.stderr)
            sys.exit(1)
        events = events[:args.limit]
    
    # Feature 8: Count Mode
    if args.count:
        print(len(events))
        return
    
    # Feature 6 & 7: Output formatting
    if args.format == 'json':
        print(format_json(events))
    else:
        print(format_table(events))

if __name__ == '__main__':
    main()
