# Day 329 Quick-Reference Command Cards ⚡

## CHALLENGE #5: VILLAGE CHRONICLE (10 min execution)

### Verify & Submit
```bash
# 1. Verify file exists and word count
wc -w ~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md

# 2. Expected output: 295 words exactly
# Output should show: 295 ...

# 3. Submit PR (using prepared script or manual)
cd ~/village-challenges
gh pr create \
  --title "Challenge #5: Village Chronicle (Day 329)" \
  --body "Day 329 Village Chronicle submission. Word count: 295. All 7 constraints verified." \
  --head claude-haiku-4.5:day-329-challenge-5 \
  --base main

# 4. Quick verification if needed
cat ~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md
```

---

## CHALLENGE #4: INFRASTRUCTURE AUDIT (50 min execution)

### Pre-Execution Checklist
```bash
# 1. Verify GitHub token
echo $GITHUB_TOKEN | head -c 20; echo "..."

# 2. Verify dependencies
python3 -c "import requests, json; print('✅ Dependencies OK')"

# 3. Verify event log
python3 -c "import json; print(f'Events: {len(json.load(open(\"/home/computeruse/village-event-log/docs/events.json\")))}')"

# 4. Verify gh CLI auth
gh auth status
```

### Run Audit
```bash
# 1. Create output directory
mkdir -p ~/village-challenges/challenges/claude-haiku-4.5/

# 2. Run optimized audit script (50 min runtime)
time python3 ~/village-challenges/day-329-toolkit/challenge4-audit-optimized.py \
  > ~/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.json 2>&1

# 3. Check output (should be valid JSON)
python3 -m json.tool ~/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.json | head -50

# 4. Generate markdown report from JSON
python3 << 'REPORT'
import json
with open("~/village-challenges/challenges/claude-haiku-4.5/infrastructure-audit-report.json") as f:
    data = json.load(f)
print("# Infrastructure Consistency Audit Report\n")
for section in data.get("sections", []):
    print(f"## {section.get('section', 'Unknown')}")
    for key, val in section.items():
        if key != 'section':
            print(f"- **{key}:** {val}")
    print()
REPORT

# 5. Submit PR
cd ~/village-challenges
gh pr create \
  --title "Challenge #4: Infrastructure Consistency Audit (Day 329)" \
  --body "Challenge #4 submission. Full audit report included." \
  --head claude-haiku-4.5:day-329-challenge-4 \
  --base main
```

---

## CHALLENGE #6: EVENT LOG QUERY ENGINE (15 min execution)

### Verify Tool
```bash
# 1. Check tool exists and is valid Python
python3 -m py_compile /tmp/challenge6_query_engine.py
echo "✅ Syntax OK"

# 2. Run help
python3 /tmp/challenge6_query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --help

# 3. Quick test (should return 3 recent events)
python3 /tmp/challenge6_query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --limit 3 --format table
```

### Submit PR
```bash
# 1. Verify tool location (must be in challenges dir for submission)
mkdir -p ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/
cp /tmp/challenge6_query_engine.py ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py

# 2. Test from new location
python3 ~/village-challenges/challenges/challenge-6-claude-haiku-4.5/query_engine.py \
  /home/computeruse/village-event-log/docs/events.json \
  --limit 3

# 3. Submit PR
cd ~/village-challenges
gh pr create \
  --title "Challenge #6: Event Log Query Engine (Day 329)" \
  --body "Challenge #6 submission. Query tool with 10 features: agent/category filters, date range, sorting, JSON/table output, count mode, help, and stdin support. All features tested and validated." \
  --head claude-haiku-4.5:day-329-challenge-6 \
  --base main
```

---

## EMERGENCY PROCEDURES

### Challenge #5 Stuck
```bash
# Check file location
ls -lah ~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md

# Re-verify word count (must be exactly 295)
wc -w ~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md

# Manual PR creation fallback
cd ~/village-challenges
git checkout -b claude-haiku-4.5/day-329-challenge-5
git add challenges/challenge-5-claude-haiku-4.5/
git commit -m "Challenge #5: Village Chronicle (Day 329)"
git push origin claude-haiku-4.5/day-329-challenge-5
```

### Challenge #4 Script Fails
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip3 install requests --upgrade
pip3 install PyGithub --upgrade

# Simplified fallback (without parallelization)
python3 << 'SIMPLE'
import json
import subprocess

# Just check event count (Section 1)
with open("/home/computeruse/village-event-log/docs/events.json") as f:
    count = len(json.load(f))
print(f"Event count: {count}")

# Check gh CLI
result = subprocess.run(["gh", "repo", "list", "ai-village-agents"], 
                       capture_output=True)
print(f"gh CLI: {'✅ OK' if result.returncode == 0 else '❌ Failed'}")
SIMPLE
```

### Challenge #6 Tool Not Found
```bash
# Verify file exists
ls -lah /tmp/challenge6_query_engine.py

# Check syntax
python3 -c "import ast; ast.parse(open('/tmp/challenge6_query_engine.py').read())"

# Test with explicit event log path
python3 /tmp/challenge6_query_engine.py /home/computeruse/village-event-log/docs/events.json --limit 3

# If all else fails, create minimal version
python3 << 'MINIMAL'
#!/usr/bin/env python3
import json
import sys
if len(sys.argv) < 2:
    print("Usage: script.py <event-log.json>")
    sys.exit(1)
with open(sys.argv[1]) as f:
    data = json.load(f)
print(f"Total events: {len(data)}")
MINIMAL
```

---

## SYSTEM VERIFICATION

### Pre-Day 329 Checklist (run at 9:55 AM)
```bash
#!/bin/bash
echo "🔍 Day 329 Pre-Flight System Check..."

# Check all dependencies
echo "1. Dependencies..."
python3 -c "import requests, json" && echo "  ✅ requests, json"
gh --version && echo "  ✅ gh CLI"

# Check all files exist
echo "2. Challenge files..."
[ -f ~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md ] && echo "  ✅ Challenge #5"
[ -f ~/village-challenges/day-329-toolkit/challenge4-audit-optimized.py ] && echo "  ✅ Challenge #4"
[ -f /tmp/challenge6_query_engine.py ] && echo "  ✅ Challenge #6"

# Check event log
echo "3. Event log..."
python3 -c "import json; print(f'  ✅ {len(json.load(open(\"/home/computeruse/village-event-log/docs/events.json\")))} events')"

# Check GitHub auth
echo "4. GitHub..."
gh auth status | head -1

echo "✅ Pre-flight check complete!"
```

