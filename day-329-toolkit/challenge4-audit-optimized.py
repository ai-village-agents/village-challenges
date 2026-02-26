#!/usr/bin/env python3
"""
Challenge #4: Infrastructure Consistency Audit (Optimized with Parallelization)
Scoring: 100 points across 5 dimensions
- Event Count Sync: 30 pts
- GitHub Pages: 25 pts
- Timestamp Audit: 20 pts
- CI/CD Status: 15 pts
- Metadata Consistency: 10 pts

Runtime: ~50 min total (2 setup + 40 data gathering + 5 report + 3 PR)
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
ORG = "ai-village-agents"
MAX_WORKERS = 4  # Parallelization: 4 concurrent API calls
VILLAGE_EVENT_LOG_PATH = "/home/computeruse/village-event-log/docs/events.json"
VILLAGE_CHRONICLE_PATH = "/home/computeruse/village-challenges/docs/village-chronicle.json"

def log(msg, level="INFO"):
    """Unified logging with timestamp"""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {level}: {msg}", file=sys.stderr)

def section(title):
    """Print section header"""
    log(f"\n{'='*60}\n{title}\n{'='*60}\n", "SECTION")

# ============================================================================
# SECTION 1: EVENT COUNT SYNC (30 points)
# ============================================================================

def load_events_from_file(filepath):
    """Load events from JSON file with error handling"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        # Handle both array and dict structures
        if isinstance(data, dict) and 'events' in data:
            return data['events']
        return data if isinstance(data, list) else []
    except Exception as e:
        log(f"Error loading {filepath}: {e}", "ERROR")
        return []

def check_event_counts():
    """Section 1: Verify event count consistency"""
    section("SECTION 1: EVENT COUNT SYNC (30 pts)")
    
    # Load event logs
    event_log_events = load_events_from_file(VILLAGE_EVENT_LOG_PATH)
    chronicle_events = load_events_from_file(VILLAGE_CHRONICLE_PATH)
    
    event_log_count = len(event_log_events)
    chronicle_count = len(chronicle_events)
    discrepancy = abs(event_log_count - chronicle_count)
    
    log(f"village-event-log: {event_log_count} events")
    log(f"village-chronicle: {chronicle_count} events")
    log(f"Discrepancy: {discrepancy} events")
    
    result = {
        "section": "Event Count Sync",
        "event_log_count": event_log_count,
        "chronicle_count": chronicle_count,
        "discrepancy": discrepancy,
        "synced": discrepancy == 0,
        "points_available": 30
    }
    
    return result

# ============================================================================
# SECTION 2: GITHUB PAGES STATUS (25 points)
# ============================================================================

def check_github_pages_status(repo):
    """Check GitHub Pages status for a single repo with parallelization"""
    try:
        url = f"https://api.github.com/repos/{ORG}/{repo}/pages"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            return {"repo": repo, "status": "enabled", "url": data.get("html_url", "N/A")}
        elif resp.status_code == 404:
            return {"repo": repo, "status": "disabled", "url": "N/A"}
        else:
            return {"repo": repo, "status": "error", "url": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"repo": repo, "status": "error", "url": str(e)}

def check_pages_status():
    """Section 2: Check GitHub Pages deployment status"""
    section("SECTION 2: GITHUB PAGES STATUS (25 pts)")
    
    try:
        # Get list of repos
        result = subprocess.run(
            ["gh", "repo", "list", ORG, "--limit", "50", "--json", "name"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            log(f"Error fetching repos: {result.stderr}", "ERROR")
            return {"section": "GitHub Pages", "error": result.stderr}
        
        repos = [r["name"] for r in json.loads(result.stdout)]
        log(f"Found {len(repos)} repos in {ORG}")
        
        # Parallel check for Pages status
        pages_results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_github_pages_status, repo): repo for repo in repos}
            for future in as_completed(futures):
                try:
                    pages_results.append(future.result())
                except Exception as e:
                    log(f"Thread error for {futures[future]}: {e}", "ERROR")
        
        enabled = [r for r in pages_results if r["status"] == "enabled"]
        disabled = [r for r in pages_results if r["status"] == "disabled"]
        errors = [r for r in pages_results if r["status"] == "error"]
        
        log(f"Pages enabled: {len(enabled)}")
        log(f"Pages disabled: {len(disabled)}")
        log(f"Errors: {len(errors)}")
        
        return {
            "section": "GitHub Pages",
            "total_repos": len(repos),
            "enabled": len(enabled),
            "disabled": len(disabled),
            "errors": len(errors),
            "enabled_repos": [r["repo"] for r in enabled],
            "points_available": 25
        }
    except Exception as e:
        log(f"Fatal error in Pages check: {e}", "ERROR")
        return {"section": "GitHub Pages", "error": str(e)}

# ============================================================================
# SECTION 3: TIMESTAMP AUDIT (20 points)
# ============================================================================

def check_timestamps():
    """Section 3: Verify timestamp consistency and format"""
    section("SECTION 3: TIMESTAMP AUDIT (20 pts)")
    
    events = load_events_from_file(VILLAGE_EVENT_LOG_PATH)
    
    timestamp_formats = {}
    errors = []
    
    for i, event in enumerate(events[:100]):  # Sample first 100 for speed
        try:
            ts = event.get("createdAt", "")
            if ts:
                # Check ISO format (YYYY-MM-DD...)
                if ts.startswith(("202", "201")):
                    fmt = "ISO8601"
                else:
                    fmt = "OTHER"
                timestamp_formats[fmt] = timestamp_formats.get(fmt, 0) + 1
        except Exception as e:
            errors.append(f"Event {i}: {e}")
    
    log(f"Timestamp formats: {timestamp_formats}")
    log(f"Parse errors: {len(errors)}")
    
    return {
        "section": "Timestamp Audit",
        "total_sampled": min(100, len(events)),
        "timestamp_formats": timestamp_formats,
        "parse_errors": len(errors),
        "consistent": len(timestamp_formats) <= 1,
        "points_available": 20
    }

# ============================================================================
# SECTION 4: CI/CD STATUS (15 points)
# ============================================================================

def check_workflows(repo):
    """Check workflow status for a single repo"""
    try:
        result = subprocess.run(
            ["gh", "workflow", "list", "-R", f"{ORG}/{repo}", "--json", "name,state"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            workflows = json.loads(result.stdout) if result.stdout else []
            return {"repo": repo, "workflows": len(workflows), "status": "ok"}
        else:
            return {"repo": repo, "workflows": 0, "status": "error"}
    except Exception as e:
        return {"repo": repo, "workflows": 0, "status": "error"}

def check_ci_cd_status():
    """Section 4: Verify CI/CD workflow status"""
    section("SECTION 4: CI/CD STATUS (15 pts)")
    
    # Check primary repos with workflows
    primary_repos = ["village-event-log", "village-challenges", "village-chronicle"]
    
    workflows_found = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_workflows, repo): repo for repo in primary_repos}
        for future in as_completed(futures):
            try:
                result = future.result()
                log(f"{result['repo']}: {result['workflows']} workflows")
                workflows_found += result['workflows']
            except Exception as e:
                log(f"Error checking {futures[future]}: {e}", "ERROR")
    
    return {
        "section": "CI/CD Status",
        "primary_repos_checked": len(primary_repos),
        "workflows_found": workflows_found,
        "operational": workflows_found > 0,
        "points_available": 15
    }

# ============================================================================
# SECTION 5: METADATA CONSISTENCY (10 points)
# ============================================================================

def check_metadata():
    """Section 5: Verify metadata consistency across repos"""
    section("SECTION 5: METADATA CONSISTENCY (10 pts)")
    
    try:
        result = subprocess.run(
            ["gh", "repo", "list", ORG, "--limit", "50", "--json", "name,description"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            log(f"Error fetching metadata: {result.stderr}", "ERROR")
            return {"section": "Metadata", "error": result.stderr}
        
        repos = json.loads(result.stdout)
        repos_with_desc = [r for r in repos if r.get("description")]
        
        log(f"Repos with descriptions: {len(repos_with_desc)}/{len(repos)}")
        
        return {
            "section": "Metadata Consistency",
            "total_repos": len(repos),
            "repos_with_description": len(repos_with_desc),
            "completeness_ratio": len(repos_with_desc) / len(repos) if repos else 0,
            "points_available": 10
        }
    except Exception as e:
        log(f"Fatal error in metadata check: {e}", "ERROR")
        return {"section": "Metadata", "error": str(e)}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all audit sections"""
    log("Challenge #4 Infrastructure Audit Started", "START")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "sections": []
    }
    
    # Run all sections
    results["sections"].append(check_event_counts())
    results["sections"].append(check_pages_status())
    results["sections"].append(check_timestamps())
    results["sections"].append(check_ci_cd_status())
    results["sections"].append(check_metadata())
    
    # Calculate summary
    total_points = sum(s.get("points_available", 0) for s in results["sections"])
    results["total_points_available"] = total_points
    
    # Output results as JSON
    print(json.dumps(results, indent=2))
    
    log("Challenge #4 Infrastructure Audit Completed", "END")
    return 0

if __name__ == "__main__":
    sys.exit(main())
