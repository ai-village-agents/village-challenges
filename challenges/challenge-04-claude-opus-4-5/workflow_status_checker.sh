#!/bin/bash
#
# Challenge #4 Section 4: CI/CD Workflow Status Checker
# Checks GitHub Actions workflow status for key repositories.
# Points: 15 pts

echo "============================================================"
echo "CHALLENGE #4 - SECTION 4: CI/CD WORKFLOW STATUS CHECKER"
echo "Execution time: $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC"
echo "============================================================"
echo ""

# Key repos with GitHub Actions workflows
REPOS_WITH_WORKFLOWS=(
    "village-event-log"
    "village-chronicle"
    "repo-health-dashboard"
    "open-ics"
    "village-collab-graph"
)

check_workflow_status() {
    local repo=$1
    echo "----------------------------------------"
    echo "Repository: $repo"
    echo "----------------------------------------"
    
    # Get latest workflow runs using gh CLI
    echo "Latest workflow runs:"
    gh run list --repo "ai-village-agents/$repo" --limit 5 2>/dev/null | head -10
    
    if [[ $? -ne 0 ]]; then
        echo "⚠️  Could not fetch workflow data (no workflows or API error)"
    fi
    echo ""
}

# Check each repo
for repo in "${REPOS_WITH_WORKFLOWS[@]}"; do
    check_workflow_status "$repo"
done

echo "============================================================"
echo "WORKFLOW SUMMARY BY REPO"
echo "============================================================"
echo ""

for repo in "${REPOS_WITH_WORKFLOWS[@]}"; do
    echo "📁 $repo:"
    # Get unique workflow names and their latest status
    gh run list --repo "ai-village-agents/$repo" --limit 10 --json name,status,conclusion,createdAt 2>/dev/null | \
        python3 -c "
import json, sys
try:
    runs = json.load(sys.stdin)
    seen = set()
    for run in runs:
        name = run.get('name', 'Unknown')
        if name not in seen:
            seen.add(name)
            status = run.get('status', '?')
            conclusion = run.get('conclusion', '?') or 'in_progress'
            created = run.get('createdAt', '?')[:19]
            icon = '✅' if conclusion == 'success' else ('🔄' if conclusion == 'in_progress' else '❌')
            print(f'   {icon} {name}: {conclusion} ({created})')
except Exception as e:
    print(f'   ⚠️  Error parsing workflow data: {e}')
" 2>/dev/null || echo "   ⚠️  No workflow data available"
    echo ""
done

echo "============================================================"
echo "STATUS: CHECK COMPLETE"
echo "============================================================"
