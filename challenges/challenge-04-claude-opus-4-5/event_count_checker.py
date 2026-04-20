#!/usr/bin/env python3
"""
Challenge #4 Section 1: Event Count Sync Checker
Verifies that village-event-log and village-chronicle have matching event counts.
Expected: 487 events in both repositories (as of Day 328 verification).
Points: 30 pts
"""

import json
import subprocess
import sys
from datetime import datetime

def fetch_json_from_github(repo, file_path):
    """Fetch JSON file from GitHub raw content."""
    url = f"https://raw.githubusercontent.com/ai-village-agents/{repo}/main/{file_path}"
    try:
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True, text=True, timeout=30
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def count_events(data):
    """Count events from JSON data structure."""
    if isinstance(data, dict):
        if "events" in data:
            return len(data["events"])
        elif "error" in data:
            return -1
    elif isinstance(data, list):
        return len(data)
    return -1

def main():
    print("=" * 60)
    print("CHALLENGE #4 - SECTION 1: EVENT COUNT SYNC CHECKER")
    print(f"Execution time: {datetime.utcnow().isoformat()}Z UTC")
    print("=" * 60)
    print()
    
    # Fetch village-event-log events.json
    print("[1/2] Fetching village-event-log/events.json...")
    event_log_data = fetch_json_from_github("village-event-log", "events.json")
    event_log_count = count_events(event_log_data)
    print(f"      village-event-log count: {event_log_count}")
    
    # Fetch village-chronicle events.json
    print("[2/2] Fetching village-chronicle/events.json...")
    chronicle_data = fetch_json_from_github("village-chronicle", "events.json")
    chronicle_count = count_events(chronicle_data)
    print(f"      village-chronicle count: {chronicle_count}")
    
    print()
    print("-" * 60)
    print("RESULTS:")
    print("-" * 60)
    
    if event_log_count == chronicle_count and event_log_count > 0:
        print(f"✅ SYNC VERIFIED: Both repos have {event_log_count} events")
        status = "PASS"
    elif event_log_count < 0 or chronicle_count < 0:
        print("❌ ERROR: Could not fetch event data")
        status = "ERROR"
    else:
        print(f"❌ MISMATCH DETECTED:")
        print(f"   village-event-log:   {event_log_count} events")
        print(f"   village-chronicle:   {chronicle_count} events")
        print(f"   Difference:          {abs(event_log_count - chronicle_count)} events")
        status = "FAIL"
    
    print()
    print(f"Expected count (Day 328 baseline): 487 events")
    if event_log_count == 487 and chronicle_count == 487:
        print("✅ Counts match Day 328 baseline")
    else:
        print(f"⚠️  Counts have changed from Day 328 baseline")
    
    print()
    print(f"STATUS: {status}")
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
