#!/usr/bin/env python3
"""
Validation script for Challenge #6 - Village Event Log Query Engine
Run: python validate.py /path/to/query_events.py
"""

import json
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

def run_query(script_path, events_path, args):
    """Run query tool and return stdout"""
    cmd = [sys.executable, script_path, events_path] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1

def test_feature(script_path, events_path, feature_num, description, test_func):
    """Test a single feature"""
    print(f"Testing Feature {feature_num}: {description}")
    try:
        return test_func(script_path, events_path)
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py /path/to/query_events.py")
        sys.exit(1)
    
    script_path = Path(sys.argv[1]).resolve()
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        sys.exit(1)
    
    # Get events.json from village-event-log repo
    events_repo = Path.home() / "village-event-log"
    if not events_repo.exists():
        events_repo = Path.home() / "village-challenges" / ".." / "village-event-log"
        if not events_repo.exists():
            print("Error: village-event-log repo not found")
            sys.exit(1)
    
    events_path = events_repo / "events.json"
    if not events_path.exists():
        print(f"Error: events.json not found at {events_path}")
        sys.exit(1)
    
    # Load events for verification
    with open(events_path, 'r') as f:
        events = json.load(f)
    
    print(f"Validating {script_path.name} against {events_path}")
    print(f"Total events: {len(events)}")
    print("=" * 60)
    
    score = 0
    total_features = 10
    
    # Test 1: JSON Parsing (basic functionality)
    def test1(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path, ["--count"])
        if code != 0:
            print(f"  FAIL: Non-zero exit code ({code})")
            print(f"  stderr: {stderr[:200]}")
            return False
        try:
            count = int(stdout)
            expected = len(events)
            if count == expected:
                print(f"  PASS: Correct count {count}")
                return True
            else:
                print(f"  FAIL: Got {count}, expected {expected}")
                return False
        except ValueError:
            print(f"  FAIL: Output not integer: {stdout[:100]}")
            return False
    
    # Test 2: Agent Filter
    def test2(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path, 
            ['--agent', 'Claude Opus 4.5', '--count'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            count = int(stdout)
            # Count events with "Claude Opus 4.5" in agents field
            expected = sum(1 for e in events if 'Claude Opus 4.5' in e.get('agents', ''))
            if count == expected:
                print(f"  PASS: Correct count {count} for agent 'Claude Opus 4.5'")
                return True
            else:
                print(f"  FAIL: Got {count}, expected {expected}")
                return False
        except ValueError:
            print(f"  FAIL: Output not integer: {stdout[:100]}")
            return False
    
    # Test 3: Category Filter
    def test3(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path,
            ['--category', 'project-launch', '--count'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            count = int(stdout)
            expected = sum(1 for e in events if e.get('category') == 'project-launch')
            if count == expected:
                print(f"  PASS: Correct count {count} for category 'project-launch'")
                return True
            else:
                print(f"  FAIL: Got {count}, expected {expected}")
                return False
        except ValueError:
            print(f"  FAIL: Output not integer: {stdout[:100]}")
            return False
    
    # Test 4: Date Range Filter
    def test4(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path,
            ['--from', '2025-04-02', '--to', '2025-04-05', '--count'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            count = int(stdout)
            # Count events between dates
            expected = sum(1 for e in events 
                         if e.get('date') >= '2025-04-02' 
                         and e.get('date') <= '2025-04-05')
            if count == expected:
                print(f"  PASS: Correct count {count} for date range 2025-04-02 to 2025-04-05")
                return True
            else:
                print(f"  FAIL: Got {count}, expected {expected}")
                return False
        except ValueError:
            print(f"  FAIL: Output not integer: {stdout[:100]}")
            return False
    
    # Test 5: Limit Results
    def test5(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path,
            ['--limit', '3', '--format', 'json'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            data = json.loads(stdout)
            if isinstance(data, list) and len(data) == 3:
                print(f"  PASS: Returned exactly 3 events")
                return True
            else:
                print(f"  FAIL: Expected list of 3 events, got {type(data)} length {len(data) if isinstance(data, list) else 'N/A'}")
                return False
        except json.JSONDecodeError:
            print(f"  FAIL: Output not valid JSON")
            return False
    
    # Test 6: JSON Output format
    def test6(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path,
            ['--limit', '2', '--format', 'json'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            data = json.loads(stdout)
            if isinstance(data, list) and len(data) == 2:
                # Check each item has expected fields
                valid = all(isinstance(e, dict) and 'id' in e for e in data)
                if valid:
                    print(f"  PASS: Valid JSON output with 2 events")
                    return True
                else:
                    print(f"  FAIL: JSON missing required fields")
                    return False
            else:
                print(f"  FAIL: JSON not a list of 2 events")
                return False
        except json.JSONDecodeError:
            print(f"  FAIL: Output not valid JSON")
            return False
    
    # Test 7: Table Output format
    def test7(script_path, events_path):
        stdout, stderr, code = run_query(script_path, events_path,
            ['--limit', '2', '--format', 'table'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        # Basic check: table should have multiple lines and contain headers
        lines = stdout.strip().split('\n')
        if len(lines) >= 3:  # header + separator + at least 1 row
            # Check for common table indicators
            if any('ID' in line or 'id' in line for line in lines[:2]):
                print(f"  PASS: Table output appears valid")
                return True
            else:
                print(f"  FAIL: Table missing ID/header")
                return False
        else:
            print(f"  FAIL: Table too short: {len(lines)} lines")
            return False
    
    # Test 8: Count mode
    def test8(script_path, events_path):
        # Already tested in test1, but verify --count with other filters
        stdout, stderr, code = run_query(script_path, events_path,
            ['--category', 'project-launch', '--count'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            count = int(stdout)
            # Just verify it's an integer
            print(f"  PASS: --count returns integer: {count}")
            return True
        except ValueError:
            print(f"  FAIL: Output not integer: {stdout[:100]}")
            return False
    
    # Test 9: Sorting
    def test9(script_path, events_path):
        # Test ascending sort
        stdout, stderr, code = run_query(script_path, events_path,
            ['--limit', '3', '--sort', 'date_asc', '--format', 'json'])
        if code != 0:
            print(f"  FAIL: Non-zero exit code")
            return False
        try:
            data = json.loads(stdout)
            if len(data) < 2:
                print(f"  SKIP: Not enough data to test sorting")
                return True
            # Check dates are ascending
            dates = [e.get('date', '') for e in data]
            if dates == sorted(dates):
                print(f"  PASS: Dates sorted ascending correctly")
                return True
            else:
                print(f"  FAIL: Dates not sorted ascending")
                return False
        except json.JSONDecodeError:
            print(f"  FAIL: Output not valid JSON")
            return False
    
    # Test 10: Help & Errors
    def test10(script_path, events_path):
        # Test --help
        stdout, stderr, code = run_query(script_path, events_path, ['--help'])
        if code == 0 and stdout and len(stdout) > 50:
            print(f"  PASS: --help produces output")
            return True
        else:
            print(f"  FAIL: --help missing or empty")
            return False
    
    tests = [
        ("JSON Parsing (basic functionality)", test1),
        ("Agent Filter", test2),
        ("Category Filter", test3),
        ("Date Range Filter", test4),
        ("Limit Results", test5),
        ("JSON Output format", test6),
        ("Table Output format", test7),
        ("Count mode", test8),
        ("Sorting", test9),
        ("Help & Errors", test10),
    ]
    
    results = []
    for i, (desc, test_func) in enumerate(tests, 1):
        passed = test_feature(script_path, events_path, i, desc, test_func)
        results.append(passed)
        print()
    
    # Calculate score
    score = sum(results)
    print("=" * 60)
    print(f"SCORE: {score}/{total_features}")
    print(f"PASSED: {sum(results)}")
    print(f"FAILED: {total_features - sum(results)}")
    
    # Summary
    print("\nDetailed Results:")
    for i, (desc, passed) in enumerate(zip([t[0] for t in tests], results), 1):
        status = "PASS" if passed else "FAIL"
        print(f"  {i:2d}. {status} - {desc}")
    
    return 0 if score == total_features else 1

if __name__ == "__main__":
    sys.exit(main())
