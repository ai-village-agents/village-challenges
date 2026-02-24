#!/usr/bin/env python3
"""
Event Count Checker for Challenge #4 Section 1
Verifies event counts across multiple village repositories
"""

import json
import subprocess
import sys

def get_json_from_repo(repo_name, file_path, branch='main'):
    """Fetch and parse JSON from a GitHub repo"""
    try:
        cmd = f"gh api repos/ai-village-agents/{repo_name}/contents/{file_path}?ref={branch}"
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None, f"API error: {result.stderr}"
        
        data = json.loads(result.stdout)
        if 'content' not in data:
            return None, "No content field in response"
        
        import base64
        content = base64.b64decode(data['content']).decode('utf-8')
        return json.loads(content), None
    except Exception as e:
        return None, str(e)

def check_event_counts():
    """Check event counts across all tracking repositories"""
    print("=" * 80)
    print("EVENT COUNT VERIFICATION - Challenge #4 Section 1")
    print("=" * 80)
    print()
    
    results = {}
    
    # Source 1: village-event-log events.json (metadata.total_events)
    print("Checking village-event-log...")
    data, error = get_json_from_repo('village-event-log', 'events.json')
    if error:
        print(f"  ERROR: {error}")
        results['village-event-log'] = {'count': None, 'error': error}
    else:
        count = data.get('metadata', {}).get('total_events')
        print(f"  ✓ metadata.total_events = {count}")
        results['village-event-log'] = {'count': count, 'error': None}
    print()
    
    # Source 2: village-chronicle events.json (array length)
    print("Checking village-chronicle...")
    data, error = get_json_from_repo('village-chronicle', 'docs/events.json')
    if error:
        print(f"  ERROR: {error}")
        results['village-chronicle'] = {'count': None, 'error': error}
    else:
        # Could be array or dict with events key
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict) and 'events' in data:
            count = len(data['events'])
        else:
            count = None
        print(f"  ✓ events array length = {count}")
        results['village-chronicle'] = {'count': count, 'error': None}
    print()
    
    # Source 3: repo-health-dashboard (check HTML/JSON display)
    print("Checking repo-health-dashboard...")
    # Try to get the index.html or data file
    data, error = get_json_from_repo('repo-health-dashboard', 'index.html')
    if error:
        # Try data.json or other files
        data2, error2 = get_json_from_repo('repo-health-dashboard', 'data.json')
        if error2:
            print(f"  WARNING: Could not fetch display files")
            results['repo-health-dashboard'] = {'count': None, 'error': 'No accessible data files'}
        else:
            # Parse JSON
            count = data2.get('total_events') or data2.get('event_count')
            print(f"  ✓ data.json event count = {count}")
            results['repo-health-dashboard'] = {'count': count, 'error': None}
    else:
        # HTML file - would need to parse, mark as manual check
        print(f"  → HTML file found, requires manual inspection")
        results['repo-health-dashboard'] = {'count': 'MANUAL_CHECK', 'error': None}
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for source, result in results.items():
        if result['error']:
            print(f"{source:30s} ERROR: {result['error']}")
        else:
            print(f"{source:30s} Count: {result['count']}")
    
    # Check for discrepancies
    counts = [r['count'] for r in results.values() if isinstance(r['count'], int)]
    if counts:
        if len(set(counts)) > 1:
            print()
            print("⚠️  DISCREPANCY DETECTED: Event counts do not match across sources")
            return 1
        else:
            print()
            print("✓ All sources report consistent event count")
            return 0
    else:
        print()
        print("⚠️  Unable to verify consistency - some sources unavailable")
        return 1

if __name__ == '__main__':
    sys.exit(check_event_counts())
