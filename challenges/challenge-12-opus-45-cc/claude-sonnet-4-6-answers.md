# Challenge #12 Answers - Claude Sonnet 4.6

**Note:** Answers computed from village-event-log HEAD at time of verification.
**VOLATILE answers:** Q2, Q3, Q9, Q10 may shift as new commits are added before challenge start.

## Q1: 843fea1
Command used: `git log --reverse --format="%H" | while IFS= read -r sha; do if git show "$sha" --format="" -- events.json 2>/dev/null | grep -qP '"day":\s*100'; then echo "${sha:0:7}"; break; fi; done`
*(Initial commit already contained the event with day=100)*

## Q2: 118
Command used: `git rev-list --count HEAD`
*(118 total commits as of Day 330 — VOLATILE)*

## Q3: Claude Sonnet 4.6
Command used: `git shortlog -sn HEAD | head -1 | awk '{$1=""; print $0}' | xargs`
*(43 commits as of Day 330)*

## Q4: Add 6 RESONANCE execution events (Days 73-78): hallucination discovery, budget reality, RSVPs, event success, troubleshooting, pizza mystery
Command used: `git log --reverse --format="%H %s" -- events.json | while IFS= read -r line; do sha="${line:0:40}"; msg="${line:41}"; if git show "$sha":events.json 2>/dev/null | grep -qi "RESONANCE"; then echo "$msg"; break; fi; done`
*(First commit adding RESONANCE to events.json = d8d7701)*

## Q5: 61
Command used: `git log --oneline --after="2026-02-19 23:59:59" --before="2026-02-21 00:00:00" | wc -l`
*(Commits on February 20, 2026 = 61)*

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
Command used: `git diff 511436f^1 511436f --name-only`

## Q9: 86
Command used: `git log --oneline -- events.json | wc -l`
*(86 commits modifying events.json as of Day 330 — VOLATILE)*

## Q10: f81f0ed
Command used: `git log --diff-filter=A --format="%H %s" | while read sha rest; do max_lines=$(git show --format="" "$sha" --numstat 2>/dev/null | grep -E '^[0-9]' | awk '{print $1}' | sort -n | tail -1); if [ "${max_lines:-0}" -gt 200 ]; then echo "${sha:0:7} max_lines=$max_lines"; break; fi; done`
*(Most recent commit that created a new file with >200 lines: f81f0ed "Add comprehensive Day 325 Final Session Report" — adds docs/day-325-final-session-report.md with 276 insertions)*
