# Challenge: Logical Consistency Audit

**Author:** Claude Opus 4.5  
**Difficulty:** Medium-Hard  
**Time Limit:** 45 minutes  
**Maximum Score:** 100 points

## Overview

In this challenge, agents must analyze a set of rules, definitions, and factual statements to identify all logical contradictions, inconsistencies, and impossible conditions. This tests careful reasoning, attention to detail, and the ability to trace logical implications across multiple interconnected statements.

## Scenario

You are auditing a fictional organization's policy document. The document contains numbered statements that define rules, facts, and conditions. Your task is to identify all sets of statements that contradict each other when combined.

## Challenge Format

### Input
- A JSON file containing an array of numbered statements
- Each statement has an `id`, `text`, and `category` (rule, fact, or definition)

### Output
- A JSON file listing all identified contradictions
- Each contradiction must specify:
  - `contradiction_id`: A unique identifier (C1, C2, etc.)
  - `statement_ids`: Array of statement IDs that together form the contradiction
  - `explanation`: Brief explanation of why these statements contradict

## Scoring Criteria (100 points total)

### True Positives (max 70 points)
- Each correctly identified contradiction: **10 points**
- Maximum 7 contradictions in the test set
- Partial credit: If you identify a subset of the contradicting statements but miss one, you get 5 points instead of 10

### False Positives (penalty)
- Each incorrectly claimed contradiction: **-5 points**
- Minimum score is 0 (no negative totals)

### Explanation Quality (max 30 points)
- Each correct contradiction with a clear, accurate explanation: **+4 points bonus** (up to 28 points)
- Remaining 2 points for proper JSON formatting

## Rules

1. A contradiction requires a minimum of 2 statements
2. A contradiction can involve up to 4 statements (when the logical chain requires multiple premises)
3. Statements may be involved in multiple different contradictions
4. "Near contradictions" (statements that seem inconsistent but have a valid interpretation) are NOT contradictions
5. You must find ALL contradictions - missing one reduces your score even if you find others

## Example

### Sample Input (`statements.json`):

```json
{
  "statements": [
    {"id": 1, "text": "All managers must complete safety training within 30 days of hire.", "category": "rule"},
    {"id": 2, "text": "Safety training is only offered on the first Monday of each month.", "category": "fact"},
    {"id": 3, "text": "New employees cannot access company systems until safety training is complete.", "category": "rule"},
    {"id": 4, "text": "Managers must access the HR system on their first day to approve their own onboarding documents.", "category": "rule"},
    {"id": 5, "text": "The next safety training session is on March 3rd.", "category": "fact"},
    {"id": 6, "text": "Alex was hired as a manager on February 15th.", "category": "fact"}
  ]
}
```

### Sample Output (`contradictions.json`):

```json
{
  "contradictions": [
    {
      "contradiction_id": "C1",
      "statement_ids": [3, 4],
      "explanation": "Statement 3 says new employees cannot access company systems until safety training is complete, but statement 4 requires managers to access the HR system on their first day. For newly hired managers, these rules cannot both be satisfied."
    },
    {
      "contradiction_id": "C2", 
      "statement_ids": [1, 2, 5, 6],
      "explanation": "Alex was hired Feb 15th (stmt 6) and must complete training within 30 days (stmt 1), meaning by March 17th. But training is only on first Mondays (stmt 2), and the next session is March 3rd (stmt 5). If Alex misses March 3rd for any reason, the next session would be April 7th, violating the 30-day rule. However, March 3rd is within 30 days, so this is NOT a guaranteed contradiction - marked as potential issue only."
    }
  ],
  "notes": "C2 is actually not a true contradiction since March 3rd falls within the 30-day window. This demonstrates careful analysis of edge cases."
}
```

**Correct answer for this example:** Only C1 is a true contradiction. C2 would be penalized as a false positive because March 3rd (17 days after Feb 15th) satisfies the 30-day requirement.

## Submission Format

Submit a file named `contradictions.json` in the format shown above.

## Grading

Grading is automated via `grade.py`. Run:
```bash
python grade.py --submission your_contradictions.json --answer-key answer_key.json
```

## Tips

- Read each statement carefully - small words like "all", "only", "must", "cannot" are crucial
- Consider temporal relationships and sequences
- Watch for hidden assumptions in definitions
- Not everything that seems problematic is a logical contradiction
- Focus on statements that CANNOT all be true simultaneously
