#!/bin/bash
#
# Challenge #4 Section 2: GitHub Pages Status Checker
# Verifies GitHub Pages status for all 38 ai-village-agents repos.
# Expected: 35 repos with Pages enabled, 3 repos not enabled
# Not enabled: village-challenges, friction-coefficient-research, village-collab-graph
# Points: 25 pts

echo "============================================================"
echo "CHALLENGE #4 - SECTION 2: GITHUB PAGES STATUS CHECKER"
echo "Execution time: $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC"
echo "============================================================"
echo ""

# All 38 repos from ai-village-agents org
REPOS=(
    "agent-ecosystem-analysis"
    "ai-ecosystem-research"
    "ai-research-collab"
    "airesearchagency-website"
    "challenges-website"
    "claude-opus-4-newsletter"
    "community-contributions"
    "events-viewer"
    "friction-coefficient-research"
    "github-pages-test"
    "juice-shop-automation-suite"
    "llm-benchmark-suite"
    "llm-benchmark-tracker"
    "llm-memory-experiments"
    "open-ics"
    "persona-portfolio"
    "project-hub"
    "project-phoenix"
    "repo-health-dashboard"
    "resonance"
    "resonance-collective"
    "shared-bookmarks"
    "village-challenges"
    "village-chronicle"
    "village-collab-graph"
    "village-directory"
    "village-event-log"
    "village-internal"
    "village-memory"
    "village-newsletter"
    "village-playbook"
    "village-prompt-library"
    "village-pulse"
    "village-simulation"
    "village-static"
    "village-stories"
    "village-wiki"
    "virtualyoutuber"
)

# Known repos without Pages enabled (Day 328 baseline)
NOT_ENABLED=("village-challenges" "friction-coefficient-research" "village-collab-graph")

pages_enabled=0
pages_not_enabled=0
pages_error=0

echo "Checking ${#REPOS[@]} repositories..."
echo ""
echo "STATUS | REPO"
echo "-------|-----"

for repo in "${REPOS[@]}"; do
    # Check if Pages is serving by hitting the GitHub Pages URL
    url="https://ai-village-agents.github.io/${repo}/"
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")
    
    if [[ "$status" == "200" || "$status" == "301" || "$status" == "302" ]]; then
        echo " ✅    | $repo (HTTP $status)"
        ((pages_enabled++))
    elif [[ "$status" == "404" ]]; then
        echo " ❌    | $repo (Pages not enabled/404)"
        ((pages_not_enabled++))
    else
        echo " ⚠️    | $repo (HTTP $status - check manually)"
        ((pages_error++))
    fi
done

echo ""
echo "============================================================"
echo "RESULTS SUMMARY"
echo "============================================================"
echo "Total repos checked:    ${#REPOS[@]}"
echo "Pages ENABLED:          $pages_enabled"
echo "Pages NOT ENABLED:      $pages_not_enabled"
echo "Errors/Unknown:         $pages_error"
echo ""
echo "Day 328 Baseline: 35 enabled, 3 not enabled"
echo ""

# Verify against baseline
if [[ $pages_enabled -eq 35 && $pages_not_enabled -eq 3 ]]; then
    echo "✅ STATUS: MATCHES BASELINE"
    exit 0
else
    echo "⚠️  STATUS: DIFFERS FROM BASELINE"
    echo "   Expected: 35 enabled, 3 not enabled"
    echo "   Actual:   $pages_enabled enabled, $pages_not_enabled not enabled"
    exit 1
fi
