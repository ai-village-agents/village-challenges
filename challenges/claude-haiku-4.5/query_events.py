#!/usr/bin/env python3
"""
Village Event Log Query Engine - Challenge #6 by DeepSeek-V3.2
Fully-featured implementation with all 10 required features
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

def load_events(filepath):
    """Feature 1: JSON Parsing - Load events.json"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get('events', [])
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

def filter_events(events, agent=None, category=None, date_from=None, date_to=None):
    """Features 2, 3, 4: Apply agent, category, and date range filters"""
    results = events
    
    # Feature 2: Agent Filter - exact match in agents list
    if agent:
        results = [e for e in results if agent in e.get('agents', [])]
    
    # Feature 3: Category Filter - exact match
    if category:
        results = [e for e in results if e.get('category') == category]
    
    # Feature 4: Date Range Filter - inclusive
    if date_from or date_to:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
            to_date = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
        except ValueError as e:
            print(f"Error: Invalid date format. Use YYYY-MM-DD: {e}", file=sys.stderr)
            sys.exit(1)
        
        filtered = []
        for e in results:
            try:
                event_date = datetime.strptime(e.get('date', ''), '%Y-%m-%d')
            except ValueError:
                continue
            
            if from_date and event_date < from_date:
                continue
            if to_date and event_date > to_date:
                continue
            filtered.append(e)
        results = filtered
    
    return results

def sort_events(events, sort_by):
    """Feature 9: Sorting by date"""
    if sort_by == 'date_asc':
        return sorted(events, key=lambda e: e.get('date', ''))
    elif sort_by == 'date_desc':
        return sorted(events, key=lambda e: e.get('date', ''), reverse=True)
    return events

def apply_limit(events, limit):
    """Feature 5: Limit Results"""
    if limit and limit > 0:
        return events[:limit]
    return events

def format_table(events):
    """Feature 7: Table Output - human-readable format"""
    if not events:
        print("No events found.")
        return
    
    # Header
    header = f"{'ID':>5} | {'Day':>4} | {'Date':>12} | {'Category':>25} | {'Title':<50} | {'Agents':<30}"
    print(header)
    print("-" * 140)
    
    # Rows
    for e in events:
        event_id = str(e.get('id', ''))
        day = str(e.get('day', ''))
        date = str(e.get('date', ''))
        category = str(e.get('category', ''))[:25]
        title = str(e.get('title', ''))[:50]
        agents = ', '.join(e.get('agents', []))[:30]
        
        print(f"{event_id:>5} | {day:>4} | {date:>12} | {category:>25} | {title:<50} | {agents:<30}")

def format_json(events):
    """Feature 6: JSON Output"""
    print(json.dumps(events, indent=2))

def main():
    # Feature 10: Help & Errors - argparse automatically provides --help
    parser = argparse.ArgumentParser(
        description='Query the Village Event Log',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Count events by Claude Opus 4.5
  python query_events.py events.json --agent "Claude Opus 4.5" --count
  
  # Get first 3 project-launch events sorted newest first
  python query_events.py events.json --category "project-launch" --limit 3 --sort date_desc --format table
  
  # Get events from first week of village
  python query_events.py events.json --from 2025-04-02 --to 2025-04-09 --format json
        """)
    
    parser.add_argument('filepath', help='Path to events.json file')
    parser.add_argument('--agent', help='Filter by agent name (exact match)', metavar='AGENT')
    parser.add_argument('--category', help='Filter by category', metavar='CATEGORY')
    parser.add_argument('--from', dest='date_from', help='Start date inclusive (YYYY-MM-DD)', metavar='DATE')
    parser.add_argument('--to', dest='date_to', help='End date inclusive (YYYY-MM-DD)', metavar='DATE')
    parser.add_argument('--limit', type=int, help='Limit number of results', metavar='N')
    parser.add_argument('--format', choices=['json', 'table'], default='table', help='Output format (default: table)')
    parser.add_argument('--count', action='store_true', help='Show count of matching events instead of details')
    parser.add_argument('--sort', choices=['date_asc', 'date_desc'], help='Sort by date (asc=oldest first, desc=newest first)', metavar='ORDER')
    
    args = parser.parse_args()
    
    # Load events
    events = load_events(args.filepath)
    
    # Apply filters
    events = filter_events(
        events, 
        agent=args.agent, 
        category=args.category, 
        date_from=args.date_from, 
        date_to=args.date_to
    )
    
    # Sort
    if args.sort:
        events = sort_events(events, args.sort)
    
    # Apply limit (but not for count mode - we count before limit)
    limited_events = apply_limit(events, args.limit)
    
    # Output
    if args.count:
        # Feature 8: Count Mode - show count of all matching events
        print(len(events))
    elif args.format == 'json':
        format_json(limited_events)
    else:  # table
        format_table(limited_events)

if __name__ == '__main__':
    main()
