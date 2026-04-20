# Challenge 12: Git Archaeology Sprint
## Submission by Claude Opus 4.5

---

### Q1: What is the SHA of the first commit that introduced the word "RESONANCE" (case-sensitive) in events.json?

**Answer:** `d8d7701`

**Command used:**
```bash
git log --all -p -- events.json | grep -B 50 "+.*RESONANCE" | grep "^commit" | tail -1
```

---

### Q2: How many total commits are in the repository?

**Answer:** `118`

**Command used:**
```bash
git rev-list --count HEAD
```

---

### Q3: Who authored the most commits in the repository?

**Answer:** `Claude Sonnet 4.6` (43 commits)

**Command used:**
```bash
git log --format='%an' | sort | uniq -c | sort -rn | head -1
```

---

### Q4: What is the first line of the commit message for the commit that first introduced "RESONANCE"?

**Answer:** `Add 6 RESONANCE execution events to Day 323`

**Command used:**
```bash
git log --oneline d8d7701 -1
git show d8d7701 --no-patch --format="%s"
```

---

### Q5: How many commits were made on February 20, 2026?

**Answer:** `61`

**Command used:**
```bash
git log --oneline --since='2026-02-20' --until='2026-02-21' | wc -l
```

---

### Q6: What is the date of the earliest commit in the repository?

**Answer:** `2026-02-19`

**Command used:**
```bash
git log --reverse --format="%ci" | head -1
```

---

### Q7: How many merge commits are in the repository?

**Answer:** `13`

**Command used:**
```bash
git log --merges --oneline | wc -l
```

---

### Q8: How many files were in commit 511436f?

**Answer:** `5` (docs/CODEOWNERS, docs/CONTRIBUTING.md, docs/ONBOARDING.md, docs/PHILOSOPHY.md, docs/TECHNICAL_OVERVIEW.md)

**Command used:**
```bash
git show 511436f --stat
git show 511436f --name-only
```

---

### Q9: How many commits modified events.json?

**Answer:** `86`

**Command used:**
```bash
git log --oneline -- events.json | wc -l
```

---

### Q10: What is the SHA of the most recent commit that added a file with more than 200 lines?

**Answer:** `f81f0ed`

**Command used:**
```bash
git log --diff-filter=A --format="" --numstat | awk '$1 > 200 {print $3}' | head -1
git log --diff-filter=A --oneline -- docs/day-325-final-session-report.md | head -1
```

**Verification:** Commit f81f0ed added docs/day-325-final-session-report.md with 276 lines.

---

## Summary of Answers

| Question | Answer |
|----------|--------|
| Q1 | d8d7701 |
| Q2 | 118 |
| Q3 | Claude Sonnet 4.6 |
| Q4 | Add 6 RESONANCE execution events to Day 323 |
| Q5 | 61 |
| Q6 | 2026-02-19 |
| Q7 | 13 |
| Q8 | 5 |
| Q9 | 86 |
| Q10 | f81f0ed |
