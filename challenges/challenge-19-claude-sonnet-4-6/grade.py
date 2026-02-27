#!/usr/bin/env python3
"""
Grade a C19 Inference Engine submission.
Usage: python grade.py <agent-name>
Submission expected at: submissions/<agent-name>/submission.md
"""

import sys
import os
import re

def count_words(text):
    return len(text.split())

def load_submission(agent_name):
    path = f"submissions/{agent_name}/submission.md"
    if not os.path.exists(path):
        print(f"ERROR: Submission not found at {path}")
        sys.exit(1)
    with open(path) as f:
        return f.read()

def grade_task1(text):
    """Task 1: Formal Structure Analysis — 10 pts automated"""
    score = 0
    details = []
    
    arguments = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']
    
    for arg in arguments:
        # Check if argument subsection exists
        pattern = rf'###\s+{arg}\b'
        if re.search(pattern, text, re.IGNORECASE):
            score += 1
            details.append(f"  ✓ {arg} subsection found (+1)")
        else:
            details.append(f"  ✗ {arg} subsection missing (0)")
    
    # Check for Form:, Verdict:, Reason: labels in each argument block
    # Extract each argument block
    for i, arg in enumerate(arguments):
        next_arg = arguments[i+1] if i < len(arguments)-1 else None
        pattern = rf'###\s+{arg}(.*?)(?=###\s+(?:{next_arg})|## Task 2|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            block = match.group(1)
            has_form = bool(re.search(r'\bForm\s*:', block, re.IGNORECASE))
            has_verdict = bool(re.search(r'\bVerdict\s*:', block, re.IGNORECASE))
            has_reason = bool(re.search(r'\bReason\s*:', block, re.IGNORECASE))
            if has_form and has_verdict and has_reason:
                score += 1
                details.append(f"  ✓ {arg} has Form/Verdict/Reason labels (+1)")
            else:
                missing = []
                if not has_form: missing.append("Form")
                if not has_verdict: missing.append("Verdict")
                if not has_reason: missing.append("Reason")
                details.append(f"  ✗ {arg} missing labels: {', '.join(missing)} (0)")
        else:
            details.append(f"  ✗ {arg} block not parseable (0)")
    
    return score, details

def grade_task2(text):
    """Task 2: Hidden Assumption Excavation — 8 pts automated"""
    score = 0
    details = []
    
    # Find Task 2 section
    task2_match = re.search(r'## Task 2(.*?)(?=## Task 3|$)', text, re.DOTALL | re.IGNORECASE)
    if not task2_match:
        details.append("  ✗ Task 2 section not found (0/8)")
        return 0, details
    
    task2_text = task2_match.group(1)
    
    target_args = ['Alpha', 'Beta', 'Delta']
    for arg in target_args:
        # Find this argument's block in task 2
        pattern = rf'###\s+{arg}(.*?)(?=###\s+(?:Beta|Delta|Gamma|Epsilon)|## Task 3|$)'
        match = re.search(pattern, task2_text, re.IGNORECASE | re.DOTALL)
        if match:
            block = match.group(1)
            has_assumption = bool(re.search(r'\bAssumption\s*:', block, re.IGNORECASE))
            has_why = bool(re.search(r'\bWhy it matters\s*:', block, re.IGNORECASE))
            has_failure = bool(re.search(r'\bFailure case\s*:', block, re.IGNORECASE))
            
            if has_assumption and has_why and has_failure:
                score += 2
                details.append(f"  ✓ {arg} has all three labels (+2)")
            else:
                missing = []
                if not has_assumption: missing.append("Assumption")
                if not has_why: missing.append("Why it matters")
                if not has_failure: missing.append("Failure case")
                details.append(f"  ✗ {arg} missing: {', '.join(missing)} (0)")
        else:
            details.append(f"  ✗ {arg} block not found in Task 2 (0)")
    
    # Check word counts for all three (all must be 50-150 for 2 pts)
    all_in_range = True
    for arg in target_args:
        pattern = rf'###\s+{arg}(.*?)(?=###\s+(?:Beta|Delta|Gamma|Epsilon)|## Task 3|$)'
        match = re.search(pattern, task2_text, re.IGNORECASE | re.DOTALL)
        if match:
            wc = count_words(match.group(1))
            if not (50 <= wc <= 150):
                all_in_range = False
                details.append(f"  ✗ {arg} word count {wc} not in 50-150 range")
            else:
                details.append(f"  ✓ {arg} word count {wc} in range")
    
    if all_in_range:
        score += 2
        details.append("  ✓ All word counts in 50-150 range (+2)")
    
    return score, details

def grade_task3(text):
    """Task 3: Strength Calibration — 8 pts automated"""
    score = 0
    details = []
    
    task3_match = re.search(r'## Task 3(.*?)(?=## Task 4|$)', text, re.DOTALL | re.IGNORECASE)
    if not task3_match:
        details.append("  ✗ Task 3 section not found (0/8)")
        return 0, details
    
    task3_text = task3_match.group(1)
    
    # Check for 5 ratings in format "Alpha: X/10" etc.
    args = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']
    ratings_found = 0
    for arg in args:
        if re.search(rf'\b{arg}\s*:\s*\d+\s*/\s*10\b', task3_text, re.IGNORECASE):
            ratings_found += 1
    
    if ratings_found == 5:
        score += 4
        details.append(f"  ✓ All 5 ratings found in X/10 format (+4)")
    elif ratings_found >= 3:
        score += 2
        details.append(f"  ~ {ratings_found}/5 ratings found (+2)")
    else:
        details.append(f"  ✗ Only {ratings_found}/5 ratings found (0)")
    
    # Check for ranked list with < separators
    if re.search(r'Ranking.*?<.*?<.*?<.*?<', task3_text, re.IGNORECASE | re.DOTALL):
        score += 2
        details.append("  ✓ Ranked list with < separators found (+2)")
    else:
        details.append("  ✗ Ranked list with < separators not found (0)")
    
    # Check for justification labels
    has_strongest = bool(re.search(r'Strongest justification\s*:', task3_text, re.IGNORECASE))
    has_weakest = bool(re.search(r'Weakest justification\s*:', task3_text, re.IGNORECASE))
    
    if has_strongest and has_weakest:
        score += 2
        details.append("  ✓ Both justification labels found (+2)")
    elif has_strongest or has_weakest:
        score += 1
        details.append("  ~ Only one justification label found (+1)")
    else:
        details.append("  ✗ Justification labels missing (0)")
    
    return score, details

def grade_task4(text):
    """Task 4: Counterexample Construction — 8 pts automated"""
    score = 0
    details = []
    
    task4_match = re.search(r'## Task 4(.*?)(?=## Task 5|$)', text, re.DOTALL | re.IGNORECASE)
    if not task4_match:
        details.append("  ✗ Task 4 section not found (0/8)")
        return 0, details
    
    task4_text = task4_match.group(1)
    
    target_args = ['Alpha', 'Beta', 'Delta']
    
    for arg in target_args:
        # Look for "Counterexample: Alpha" style headers
        pattern = rf'###\s+Counterexample\s*:\s*{arg}(.*?)(?=###\s+Counterexample|## Task 5|$)'
        match = re.search(pattern, task4_text, re.IGNORECASE | re.DOTALL)
        if match:
            score += 1
            details.append(f"  ✓ Counterexample for {arg} found (+1)")
            
            # Check word count
            wc = count_words(match.group(1))
            if 60 <= wc <= 100:
                score += 1
                details.append(f"  ✓ {arg} counterexample word count {wc} in range (+1)")
            else:
                details.append(f"  ✗ {arg} counterexample word count {wc} not in 60-100 range (0)")
        else:
            details.append(f"  ✗ Counterexample for {arg} not found (0)")
    
    # Check correct labeling (2 pts) - all three must be present
    all_present = all(
        re.search(rf'###\s+Counterexample\s*:\s*{arg}', task4_text, re.IGNORECASE)
        for arg in target_args
    )
    if all_present:
        score += 2
        details.append("  ✓ All three counterexamples correctly labeled (+2)")
    else:
        details.append("  ✗ Not all counterexamples correctly labeled (0)")
    
    return score, details

def grade_task5(text):
    """Task 5: Synthesis — 6 pts automated"""
    score = 0
    details = []
    
    task5_match = re.search(r'## Task 5(.*?)$', text, re.DOTALL | re.IGNORECASE)
    if not task5_match:
        details.append("  ✗ Task 5 section not found (0/6)")
        return 0, details
    
    task5_text = task5_match.group(1)
    
    # Word count 200-300
    wc = count_words(task5_text)
    if 200 <= wc <= 300:
        score += 2
        details.append(f"  ✓ Word count {wc} in 200-300 range (+2)")
    else:
        details.append(f"  ✗ Word count {wc} not in 200-300 range (0)")
    
    # Check for Champion, Deceiver, Principle labels
    for label in ['Champion', 'Deceiver', 'Principle']:
        if re.search(rf'\b{label}\s*:', task5_text, re.IGNORECASE):
            score += 1
            details.append(f"  ✓ {label}: label found (+1)")
        else:
            details.append(f"  ✗ {label}: label missing (0)")
    
    # Check for validity/soundness vocabulary
    if re.search(r'\b(valid|invalid|sound|unsound)\b', task5_text, re.IGNORECASE):
        score += 1
        details.append("  ✓ Validity/soundness vocabulary present (+1)")
    else:
        details.append("  ✗ No validity/soundness vocabulary found (0)")
    
    return score, details

def main():
    if len(sys.argv) < 2:
        print("Usage: python grade.py <agent-name>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    text = load_submission(agent_name)
    
    print(f"\n{'='*60}")
    print(f"GRADING: {agent_name}")
    print(f"{'='*60}\n")
    
    total = 0
    
    print("## Task 1: Formal Structure Analysis (10 pts automated)")
    s1, d1 = grade_task1(text)
    for d in d1: print(d)
    print(f"  Task 1 Score: {s1}/10\n")
    total += s1
    
    print("## Task 2: Hidden Assumption Excavation (8 pts automated)")
    s2, d2 = grade_task2(text)
    for d in d2: print(d)
    print(f"  Task 2 Score: {s2}/8\n")
    total += s2
    
    print("## Task 3: Strength Calibration (8 pts automated)")
    s3, d3 = grade_task3(text)
    for d in d3: print(d)
    print(f"  Task 3 Score: {s3}/8\n")
    total += s3
    
    print("## Task 4: Counterexample Construction (8 pts automated)")
    s4, d4 = grade_task4(text)
    for d in d4: print(d)
    print(f"  Task 4 Score: {s4}/8\n")
    total += s4
    
    print("## Task 5: Synthesis (6 pts automated)")
    s5, d5 = grade_task5(text)
    for d in d5: print(d)
    print(f"  Task 5 Score: {s5}/6\n")
    total += s5
    
    print(f"{'='*60}")
    print(f"AUTOMATED TOTAL: {total}/40")
    print(f"Manual grading: /60")
    print(f"{'='*60}\n")
    print("Note: Manual grading criteria:")
    print("  - Accuracy (40%): Correct logical analysis")
    print("  - Precision (35%): Specific, non-generic reasoning")
    print("  - Insight (25%): Non-obvious observations and distinctions")

if __name__ == "__main__":
    main()
