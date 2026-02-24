#!/bin/bash
# GitHub Pages Status Checker - Section 2 (25 points)
# Checks Pages enabled status and live status for all ai-village-agents repos

echo "=== GITHUB PAGES STATUS CHECK ==="
echo "Organization: ai-village-agents"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# Get all repos in the organization
REPOS=$(gh api /orgs/ai-village-agents/repos --paginate --jq '.[].name' | sort)
TOTAL_REPOS=$(echo "$REPOS" | wc -l)

echo "Total repositories: $TOTAL_REPOS"
echo ""

ENABLED_COUNT=0
LIVE_COUNT=0
BROKEN_PAGES=()

echo "Checking Pages status for each repository..."
echo ""

for REPO in $REPOS; do
    # Check if Pages is enabled via API
    PAGES_STATUS=$(gh api repos/ai-village-agents/$REPO/pages 2>&1)
    
    if echo "$PAGES_STATUS" | grep -q "404"; then
        # Pages not enabled
        echo "[$REPO] Pages: DISABLED"
    else
        ENABLED_COUNT=$((ENABLED_COUNT + 1))
        
        # Pages enabled - now check if it's live
        PAGES_URL="https://ai-village-agents.github.io/$REPO/"
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L "$PAGES_URL" --max-time 10)
        
        if [ "$HTTP_STATUS" = "200" ]; then
            LIVE_COUNT=$((LIVE_COUNT + 1))
            echo "[$REPO] Pages: ENABLED + LIVE (200 OK) - $PAGES_URL"
        else
            echo "[$REPO] Pages: ENABLED but BROKEN (HTTP $HTTP_STATUS) - $PAGES_URL"
            BROKEN_PAGES+=("$REPO (HTTP $HTTP_STATUS)")
        fi
    fi
done

echo ""
echo "=== SUMMARY ==="
echo "Total repositories: $TOTAL_REPOS"
echo "Pages enabled: $ENABLED_COUNT"
echo "Pages live (200 OK): $LIVE_COUNT"
echo ""

if [ ${#BROKEN_PAGES[@]} -gt 0 ]; then
    echo "Broken Pages (enabled but not returning 200 OK):"
    for BROKEN in "${BROKEN_PAGES[@]}"; do
        echo "  - $BROKEN"
    done
else
    echo "No broken pages detected!"
fi

echo ""
echo "=== SCORING BREAKDOWN ==="
echo "Total enabled count reported: 10 points"
echo "Total live count reported: 10 points"
echo "Broken pages list: 5 points"
echo "Section 2 Total: 25 points"
