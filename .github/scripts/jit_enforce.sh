#!/usr/bin/env bash
set -euo pipefail
# Inputs: $GITHUB_EVENT_PATH, repository checkout at PR HEAD
PR_CREATED=$(jq -r '.pull_request.created_at' "$GITHUB_EVENT_PATH")
BASE_REF=$(jq -r '.pull_request.base.ref' "$GITHUB_EVENT_PATH")
HEAD_REF=$(jq -r '.pull_request.head.ref' "$GITHUB_EVENT_PATH")
# Normalize PR created time to epoch
pr_epoch=$(python3 - <<PY
import sys,datetime
from dateutil import parser
print(int(parser.isoparse(sys.argv[1]).timestamp()))
PY
"$PR_CREATED") || pr_epoch=0
# Identify touched top-level challenge dirs
# Compare against base ref; fetch full history to be safe
 git fetch --no-tags --depth=0 origin "$BASE_REF" >/dev/null 2>&1 || true
changed=$(git diff --name-only "origin/$BASE_REF"...HEAD | awk -F/ '/^live-challenge-[^/]+\//{print $1}' | sort -u)
if [ -z "$changed" ]; then
  echo "No live-challenge-* paths touched; skipping JIT enforcement."
  exit 0
fi
rc=0
for ch in $changed; do
  man="launches/$ch/manifest.json"
  if [ ! -f "$man" ]; then
    echo "ERROR: Missing launch manifest $man for $ch" >&2
    rc=1; continue
  fi
  start=$(jq -r '.start_time' "$man")
  if [ -z "$start" ] || [ "$start" = "null" ]; then
    echo "ERROR: $man missing start_time" >&2
    rc=1; continue
  fi
  start_epoch=$(python3 - <<PY
import sys,datetime
from dateutil import parser
print(int(parser.isoparse(sys.argv[1]).timestamp()))
PY
"$start")
  echo "[$ch] start_time=$start (epoch $start_epoch); pr_created=$PR_CREATED (epoch $pr_epoch)"
  if [ "$pr_epoch" -lt "$start_epoch" ]; then
    echo "ERROR: PR was created before start_time for $ch" >&2
    rc=1
  fi
  # Check commits that touch the challenge dir
  git rev-list --no-merges --reverse HEAD -- "$ch" | while read -r sha; do
    ts=$(git show -s --format=%cI "$sha")
    ce=$(python3 - <<PY
import sys,datetime
from dateutil import parser
print(int(parser.isoparse(sys.argv[1]).timestamp()))
PY
"$ts")
    if [ "$ce" -lt "$start_epoch" ]; then
      echo "ERROR: Commit $sha touching $ch has committer time $ts before start_time $start" >&2
      rc=1; break
    fi
  done
done
exit $rc
