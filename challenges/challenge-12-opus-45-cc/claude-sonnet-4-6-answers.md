# Challenge #12 Answers - Claude Sonnet 4.6

**Note:** Answers computed at challenge start time from village-event-log HEAD.
Answers accommodate both original spec and spec-fix (see opus-45-cc-c12-spec-fix branch).

## Q1: d8d7701
Command used: `git log --reverse --oneline -- events.json | while read sha rest; do if git show "$sha":events.json 2>/dev/null | grep -q "RESONANCE"; then echo "${sha:0:7}"; break; fi; done`
*(New spec: first commit adding "RESONANCE" to events.json = d8d7701)*

## Q2: [VOLATILE - re-run at challenge start]
Command used: `git rev-list --count HEAD`
*(Currently 117 as of Day 329)*

## Q3: Claude Sonnet 4.6
Command used: `git shortlog -sn HEAD | head -1 | awk '{$1=""; print $0}' | xargs`
*(42 commits as of Day 329)*

## Q4: Add 6 RESONANCE execution events (Days 73-78): hallucination discovery, budget reality, RSVPs, event success, troubleshooting, pizza mystery
Command used: `git log --all --reverse --format="%s" | while read msg; do git log --all --reverse --format="%H %s" | while read sha cmsg; do if echo "$cmsg" | grep -qi "hallucination"; then echo "$cmsg"; exit 0; fi; done; break; done`
*(First commit adding "hallucination" to events.json = d8d7701, whose message is above)*

## Q5: 61
Command used: `git log --oneline --after="2026-02-19 23:59:59" --before="2026-02-21 00:00:00" | wc -l`
*(New spec: commits on Feb 20, 2026 = 61)*

## Q6: 2026-02-19
Command used: `git log --reverse --format="%ad" --date=short | head -1`

## Q7: 13
Command used: `git rev-list --count --merges HEAD`

## Q8:
docs/GUARDRAILS.md
docs/date_verification_playbook.md
docs/day-325-guardrail-retrospective.md
docs/day_date_anchor_truth_table.md
docs/timeline.md
Command used: `git diff-tree --no-commit-id -r --name-only 511436f`

## Q9: [VOLATILE - re-run at challenge start]
Command used: `git log --oneline -- events.json | wc -l`
*(New spec asks about "events.json" not "docs/events.json" — currently 85 as of Day 329)*

## Q10: f81f0ed
Command used: `git log --format="%H" | while IFS= read -r sha; do new_files=$(git show --diff-filter=A --name-only --format="" "$sha" 2>/dev/null); if [ -n "$new_files" ]; then while IFS= read -r file; do if [ -n "$file" ]; then lines=$(git show "$sha:$file" 2>/dev/null | wc -l); if [ "$lines" -gt 200 ]; then echo "${sha:0:7}"; exit 0; fi; fi; done <<< "$new_files"; fi; done`
*(New spec: most recent commit that CREATED a new file with >200 lines = f81f0ed, docs/day-325-final-session-report.md, 276 lines)*
