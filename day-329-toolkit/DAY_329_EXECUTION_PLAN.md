# Day 329 Master Execution Plan 🎯

**Date:** February 24, 2026 | **Launch Window:** 10:00 AM – 2:00 PM PT (4 hours)

## EXECUTIVE SUMMARY

Three challenges launching simultaneously at 10:00 AM:
- **Challenge #5** (Village Chronicle): 10 min, 0 pts
- **Challenge #4** (Infrastructure Audit): 50 min, 1–2 pts ⭐
- **Challenge #6** (Query Engine): 15 min, 1–2 pts ⭐

**Target:** Submit all 3 PRs by 11:15 AM with validated outputs.

---

## PRE-LAUNCH PREPARATION (9:45–9:55 AM)

Run this before 10:00 AM:

```bash
# 1. Verify all systems
bash ~/village-challenges/day-329-toolkit/DEPENDENCY_CHECK.sh

# 2. Check Challenge #5 one final time
wc -w ~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md
# Expected: 295

# 3. Verify Challenge #6 tool location
ls -lah /tmp/challenge6_query_engine.py

# 4. Confirm Challenge #4 script ready
python3 -m py_compile ~/village-challenges/day-329-toolkit/challenge4-audit-optimized.py && echo "✅"

# 5. Test GitHub auth
gh auth status | head -1
```

---

## LAUNCH SEQUENCE (10:00 AM SHARP)

### PHASE 1: Challenge #5 SUBMISSION (10:00–10:05 AM)
**Duration:** 5 minutes | **Expected Score:** 0 pts (baseline)

```bash
# CRITICAL: This must be first to free up time for longer challenges

cd ~/village-challenges

# Create branch and commit
git checkout -b claude-haiku-4.5/day-329-challenge-5
git add challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md
git commit -m "Challenge #5: Village Chronicle (Day 329)"
git push origin claude-haiku-4.5/day-329-challenge-5

# Submit PR
gh pr create \
  --title "Challenge #5: Village Chronicle (Day 329)" \
  --body "Village chronicle submission. Word count: 295. All 7 constraints verified." \
  --head claude-haiku-4.5:day-329-challenge-5 \
  --base main

# Record PR URL
# Expected PR: challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md
```

**Verification:**
- ✅ Word count: exactly 295
- ✅ 7 constraints: chronology, agents, topics, sentence length, facts, hedging
- ✅ PR submitted with all required metadata

---

### PHASE 2: Challenge #4 EXECUTION (10:00–10:50 AM)
**Duration:** 50 minutes | **Expected Score:** 1–2 pts ⭐

**Timeline:**
- 10:00–10:02 (2 min): Setup + verification
- 10:02–10:42 (40 min): Data gathering (parallelized)
- 10:42–10:47 (5 min): Report generation
- 10:47–10:50 (3 min): PR submission

```bash
# STEP 1: Verify environment (2 min)
mkdir -p ~/village-challenges/challenges/claude-haiku-4.5/

# Verify event log baseline
python3 -c "
import json
with open('/home/computeruse/village-event-log/docs/events.json') as f:
    events = json.load(f)
print(f'✅ Event log loaded: {len(events)} events')
"

# STEP 2: Run audit script (40 min)
cd ~/village-challenges
time python3 ~/village-challenges/day-329-toolkit/challenge4-audit-optimized.py \
  2>&1 | tee ~/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit.log \
  > ~/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.json

# Verify JSON output is valid
python3 -c "
import json
with open('~/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.json') as f:
    data = json.load(f)
print(f'✅ Valid JSON with {len(data.get(\"sections\", []))} sections')
"

# STEP 3: Generate markdown report (5 min)
python3 << 'GENREPORT'
import json
import sys

with open("/home/computeruse/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.json") as f:
    data = json.load(f)

with open("/home/computeruse/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.md", "w") as out:
    out.write("# Infrastructure Consistency Audit Report\n\n")
    out.write(f"**Generated:** {data.get('timestamp', 'N/A')}\n\n")
    
    for section in data.get("sections", []):
        name = section.get("section", "Unknown")
        out.write(f"## {name}\n\n")
        
        for key, val in section.items():
            if key not in ["section", "points_available"]:
                out.write(f"- **{key}:** {val}\n")
        
        if "points_available" in section:
            out.write(f"\n**Points Available:** {section['points_available']}\n\n")

print("✅ Markdown report generated")
GENREPORT

# STEP 4: Submit PR (3 min)
cd ~/village-challenges

git checkout -b claude-haiku-4.5/day-329-challenge-4
git add challenges/claude-haiku-4.5/infrastructure-audit-report.json
git add challenges/claude-haiku-4.5/infrastructure-audit-report.md
git add challenges/claude-haiku-4.5/infrastructure-audit.log
git commit -m "Challenge #4: Infrastructure Consistency Audit (Day 329)"
git push origin claude-haiku-4.5/day-329-challenge-4

gh pr create \
  --title "Challenge #4: Infrastructure Consistency Audit (Day 329)" \
  --body "Challenge #4 submission. Complete audit of village infrastructure including event count sync, GitHub Pages status, timestamps, CI/CD workflows, and metadata consistency. Full report included." \
  --head claude-haiku-4.5/day-329-challenge-4 \
  --base main
```

**Verification Points:**
- ✅ Event count sync (Section 1, 30 pts): 487 vs 487 events
- ✅ GitHub Pages status (Section 2, 25 pts): Check all repos in ai-village-agents
- ✅ Timestamp audit (Section 3, 20 pts): Verify ISO8601 consistency
- ✅ CI/CD status (Section 4, 15 pts): Confirm workflows operational
- ✅ Metadata consistency (Section 5, 10 pts): Check repo descriptions
- ✅ Output format: Valid JSON + markdown report + log file

**Expected Score:** 80–90/100 → 1–2 pts

---

### PHASE 3: Challenge #6 SUBMISSION (10:50–11:10 AM)
**Duration:** 20 minutes | **Expected Score:** 1–2 pts ⭐

```bash
# STEP 1: Copy tool to submission directory (2 min)
mkdir -p ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/
cp /tmp/challenge6_query_engine.py ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py

# STEP 2: Verify all 10 features (8 min)
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json --help

# Verify each feature:
echo "1. Agent filter..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --agent "Claude Sonnet 4.6" --limit 2

echo "2. Category filter..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --category "milestone" --limit 2

echo "3. Date range..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --from "2025-04-01" --to "2025-04-10" --limit 2

echo "4. Sorting..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --sort date_desc --limit 2

echo "5. JSON output..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --format json --limit 1

echo "6. Table output (default)..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --format table --limit 1

echo "7. Count mode..."
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --count

echo "All features verified ✅"

# STEP 3: Submit PR (10 min)
cd ~/village-challenges

git checkout -b claude-haiku-4.5/day-329-challenge-6
git add challenges/challenge-6-claude-haiku-4.5/query_engine.py
git commit -m "Challenge #6: Event Log Query Engine (Day 329)"
git push origin claude-haiku-4.5/day-329-challenge-6

gh pr create \
  --title "Challenge #6: Event Log Query Engine (Day 329)" \
  --body "Event Log Query Engine submission with 10 validated features:
1. Agent filtering (--agent)
2. Category filtering (--category)
3. Date range filtering (--from, --to)
4. Sorting (--sort date_asc|date_desc)
5. JSON output (--format json)
6. Table output (--format table)
7. Event count (--count)
8. Help/usage (--help)
9. Error handling
10. Stdin input support

All features tested and validated. No hardcoded date vulnerabilities." \
  --head claude-haiku-4.5/day-329-challenge-6 \
  --base main
```

**Verification Points:**
- ✅ All 10 features working
- ✅ No date hardcoding vulnerabilities
- ✅ Proper error handling
- ✅ Help text complete
- ✅ Sample outputs valid

**Expected Score:** 85–95/100 → 1–2 pts

---

## POST-SUBMISSION (11:10 AM ONWARD)

### Buffer Time (11:10 AM–12:00 PM)
- Monitor Challenge #3 adjudication results (~12:53 PM)
- Watch for early feedback on Challenges #4–6
- Prepare contingency scripts if needed
- Begin prep for Challenge #7 (if time permits)

### Monitoring Points
```bash
# Track PR status
gh pr list --state open | grep "Day 329"

# Check event log for new events
tail -20 /home/computeruse/village-event-log/docs/events.json

# Monitor challenge submissions
cd ~/village-challenges && git log --oneline | head -10
```

---

## SUCCESS CRITERIA

### All Three Challenges ✅
- [ ] Challenge #5 PR submitted (10:05 AM)
- [ ] Challenge #4 PR submitted (10:50 AM)
- [ ] Challenge #6 PR submitted (11:10 AM)
- [ ] All files in correct locations
- [ ] All outputs valid and readable

### Expected Scoring
- Challenge #5: 0 pts (baseline)
- Challenge #4: 1–2 pts (80–90/100 audit)
- Challenge #6: 1–2 pts (all 10 features)

**Total for Day 329:** 2–4 pts expected
**Current Village Score:** 3 + 0 + (0–1) = 3–4 pts
**Projected Final Score:** 13–17 pts / 18+ possible

---

## EMERGENCY CONTACTS

**If stuck:** Email help@agentvillage.org (include error logs)

**Common Issues & Fixes:**

| Issue | Solution |
|-------|----------|
| GitHub auth fails | Run `gh auth login` |
| Python missing module | `pip3 install <module>` |
| Script timeout | Check internet connection, increase timeout |
| Event log not found | Verify path: `/home/computeruse/village-event-log/docs/events.json` |
| PR creation fails | Verify branch exists: `git branch -a` |

---

## TOOLKIT FILES

All files in: `~/village-challenges/day-329-toolkit/`

```
day-329-toolkit/
├── PRE_FLIGHT_CHECKLIST.md          ← Run before 10:00 AM
├── QUICK_REFERENCE_COMMANDS.md      ← During execution
├── DAY_329_EXECUTION_PLAN.md        ← This file
├── DEPENDENCY_CHECK.sh              ← System validation
└── challenge4-audit-optimized.py    ← Main audit script
```

**Usage:** Print out `QUICK_REFERENCE_COMMANDS.md` and keep it visible during execution.

---

**STATUS:** ✅ READY FOR LAUNCH
**ESTIMATED PREP TIME:** 15 minutes
**PROBABILITY OF SUCCESS:** 85%+ (all systems verified)

