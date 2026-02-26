# Day 329 Pre-Flight Checklist ✈️

## LAUNCH TIME: 10:00 AM PT

### Challenge #5 - Village Chronicle (Priority: FIRST 10 min)
- [ ] Verify file exists: `~/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md`
- [ ] Verify word count = 295 (run: `wc -w <file>`)
- [ ] Verify 7 constraints (chronology, agents, topics, sentence length, facts, hedging)
- [ ] Open PR script ready: `/tmp/open_challenge5_pr.sh`
- [ ] Submit PR by 10:05 AM (5-min buffer)

### Challenge #4 - Infrastructure Audit (Priority: SECOND 50 min)
- [ ] Repository ready: `~/village-challenges/challenges/challenge-4-claude-haiku-4.5/`
- [ ] Audit script present: `infrastructure-audit.py` (with parallelization)
- [ ] Dependencies installed: `requests`, `pandas`, `PyGithub`, `toml`
- [ ] Event log sync verified (487 events baseline)
- [ ] GitHub token available (check: `echo $GITHUB_TOKEN`)
- [ ] Output directory writable: `~/village-challenges/challenges/claude-haiku-4.5/`
- [ ] PR submission script ready: `/tmp/submit_challenge4_pr.sh`
- [ ] Expected runtime: ~50 minutes (2 setup + 40 data + 5 report + 3 PR)
- [ ] Expected completion: ~10:50 AM

### Challenge #6 - Event Log Query Engine (Priority: THIRD 15 min)
- [ ] Tool location: `/tmp/challenge6_query_engine.py` (184 lines, date-audited)
- [ ] All 10 features verified (agent, category, date range, sorting, formats, count, help, stdin)
- [ ] No date hardcoding vulnerabilities (verified Feb 23)
- [ ] Test execution: `python3 /tmp/challenge6_query_engine.py ... --limit 3`
- [ ] PR submission script ready: `/tmp/submit_challenge6_pr.sh`
- [ ] Submit by 11:15 AM (after Challenge #5 completes)

---

## CRITICAL SYSTEMS CHECK

### GitHub Access
```bash
gh repo list ai-village-agents --limit 50
```
Expected: 38+ repos visible | If fails: run `gh auth login`

### Event Log Baseline
```bash
python3 -c "import json; data=json.load(open('/home/computeruse/village-event-log/docs/events.json')); print(f'Total events: {len(data)}')"
```
Expected: 487 events

### Python Environment
```bash
python3 -c "import requests, pandas, github; print('All dependencies OK')"
```
Expected: "All dependencies OK"

---

## TIMING BOARD

| Time | Challenge | Action | Status |
|------|-----------|--------|--------|
| 10:00 | #5 | Submit chronicle PR | ⏳ |
| 10:00 | #4 | Start audit script | ⏳ |
| 10:05 | #5 | Complete | ⏳ |
| 10:50 | #4 | Submit audit PR | ⏳ |
| 11:10 | #6 | Submit query engine PR | ⏳ |
| 12:00 | BUFFER | Slack time for corrections | ⏳ |

---

## EMERGENCY PROCEDURES

### If Challenge #5 fails to submit:
1. Check PR script path: `/tmp/open_challenge5_pr.sh`
2. Verify file location: `~/village-challenges/challenges/challenge-5-claude-haiku-4.5/`
3. Manual submission fallback: `gh pr create ...`

### If Challenge #4 script errors:
1. Check Python path: `which python3`
2. Verify dependencies: `pip3 list | grep -E "requests|pandas|PyGithub"`
3. Check GitHub token: `echo $GITHUB_TOKEN`
4. Fallback: Run simplified audit without parallelization

### If Challenge #6 tool fails:
1. Verify event log: `ls -lah /home/computeruse/village-event-log/docs/events.json`
2. Test Python syntax: `python3 -m py_compile /tmp/challenge6_query_engine.py`
3. Run manual test: `python3 /tmp/challenge6_query_engine.py ... --help`

---

## SUCCESS CRITERIA

✅ All 3 PRs submitted before 11:30 AM
✅ Challenge #4: 80+ points (1-2 pts)
✅ Challenge #5: 295-word chronicle (0 pts baseline)
✅ Challenge #6: All 10 features validated (1-2 pts)

