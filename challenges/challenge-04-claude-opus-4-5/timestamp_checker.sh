#!/bin/bash
#
# Challenge #4 Section 3: Timestamp Audit
# Extracts latest commit metadata for 5 key repositories.
# Points: 20 pts

echo "============================================================"
echo "CHALLENGE #4 - SECTION 3: TIMESTAMP AUDIT"
echo "Execution time: $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC"
echo "============================================================"
echo ""

# Key repos for timestamp audit
KEY_REPOS=(
    "village-event-log"
    "village-chronicle"
    "village-directory"
    "repo-health-dashboard"
    "village-challenges"
)

echo "REPO | LATEST SHA | DATE | AUTHOR"
echo "-----|------------|------|-------"

for repo in "${KEY_REPOS[@]}"; do
    # Get latest commit info using GitHub API via curl
    info=$(curl -s "https://api.github.com/repos/ai-village-agents/$repo/commits/main" | \
        python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    sha = data.get('sha', 'N/A')[:7]
    date = data.get('commit', {}).get('author', {}).get('date', 'N/A')
    author = data.get('commit', {}).get('author', {}).get('name', 'N/A')
    print(f'{sha} | {date} | {author}')
except Exception as e:
    print(f'ERROR | {e}')
" 2>/dev/null)
    echo "$repo | $info"
done

echo ""
echo "============================================================"
echo "Day 328 Baseline Commits (for comparison):"
echo "============================================================"
echo "village-event-log   | 10e5be4 | 2026-02-20T21:54:46Z | Gemini 3 Pro"
echo "village-chronicle   | 530bb3d | 2026-02-21T09:24:49Z | github-actions[bot]"
echo "village-directory   | 701befb | 2026-02-20T20:47:36Z | Claude Opus 4.6"
echo "repo-health-dashboard| bc6bae1 | 2026-02-23T08:40:28Z | GitHub Action"
echo "village-challenges  | 23270a2 | 2026-02-23T20:31:16Z | claude-sonnet-45"
echo ""
echo "STATUS: CHECK COMPLETE"
