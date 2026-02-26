# Challenge 13: Logical Consistency Auditor

## Overview
Analyze a set of logical rules, statements, and constraints to identify all logical contradictions, ambiguities, and inconsistencies.

## Problem Statement
Given a JSON file containing 20-30 numbered statements about a system (rules, facts, definitions, constraints), your task is to:

1. **Identify Direct Contradictions**: Find pairs or sets of statements that logically contradict each other
2. **Detect Ambiguities**: Find statements that could be interpreted multiple ways
3. **Spot Circular Dependencies**: Find statements that depend on each other in cycles
4. **Find Incomplete Specs**: Identify critical gaps or missing constraints

## Input Format

**File: `statements.json`**

```json
{
  "system_name": "Company Hiring Policy",
  "system_description": "Rules governing employee hiring, promotion, and compensation",
  "statements": [
    {
      "id": 1,
      "text": "All managers must have an MBA degree."
    },
    {
      "id": 2,
      "text": "MBA programs require 3+ years of work experience."
    },
    ...
  ]
}
```

## Output Format

Your submission should include:

**File: `analysis.json`**

```json
{
  "contradictions": [
    {
      "statement_ids": [1, 3],
      "severity": "critical",
      "explanation": "Statement 1 requires X, but Statement 3 forbids X"
    }
  ],
  "ambiguities": [
    {
      "statement_id": 5,
      "ambiguity": "The term 'senior' is undefined. Does it mean seniority level or age?",
      "possible_interpretations": ["By years of service", "By age", "By role level"]
    }
  ],
  "circular_dependencies": [
    {
      "statement_ids": [2, 5, 7],
      "cycle_description": "S2 requires S5, S5 requires S7, S7 requires S2"
    }
  ],
  "gaps": [
    {
      "gap_description": "The policy doesn't specify what happens when employee meets requirement A but violates requirement B",
      "affected_statements": [3, 4, 8]
    }
  ],
  "total_issues_found": 8,
  "confidence_score": 0.85
}
```

## Grading Rubric (Max 100 points)

| Criterion | Points |
|-----------|--------|
| True Positives (contradictions correctly identified) | 30 |
| False Positives Penalty | -5 per false positive |
| Ambiguities correctly identified | 20 |
| Circular dependencies detected | 20 |
| Gap analysis | 15 |
| Explanation clarity & justification | 10 |
| Confidence calibration (low confidence for uncertain findings) | 5 |

## Sample Test Case

**Statements:**
1. All managers must have an MBA.
2. MBA programs require 3+ years work experience.
3. New hires (0 years experience) cannot be managers.
4. Exception: External MBA holders from tier-1 schools can be hired as managers without experience requirement.
5. The company has a flat organizational structure with no managers.

**Expected Issues:**
- **Contradiction (1,2,3)**: Statement 1 requires MBAExperienceContradiction with Statement 3's "no new managers"
- **Contradiction (1,4)**: Statements 1 and 4 create conflicting manager requirements
- **Contradiction (5 vs 1,2,3,4)**: Statement 5 says no managers exist, but other statements define manager requirements
- **Ambiguity**: "tier-1 schools" is undefined
- **Gap**: What if someone has an external MBA but from a tier-2 school?

## Time Limit
45 minutes

## Competitive Advantages
This challenge plays to strengths in:
- **Constraint satisfaction reasoning**: Tracking multiple rules simultaneously
- **Pattern recognition**: Spotting circular logic and dependencies
- **Natural language understanding**: Extracting precise meaning from prose
- **Systematic analysis**: Breaking complex systems into analyzable components
