#!/usr/bin/env python3
"""
Grader for Live Challenge 5: The Number Theory Gauntlet
Challenge Designer: Claude Opus 4.6

Usage: python3 grade.py <answer_file>
"""

import sys
import os

ANSWER_KEY = [
    "649",       # P1: 7^2026 mod 1000
    "8120",      # P2: smallest n where n! has exactly 2026 trailing zeros
    "820",       # P3: subsets of {1..12} with sum divisible by 5
    "3044",      # P4: sum of phi(1) + ... + phi(100)
    "14833",     # P5: D(8) = derangements of 8 (non-attacking rooks avoiding diagonal)
]

def grade(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return 0
    
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    # Remove trailing empty lines
    while lines and lines[-1] == '':
        lines.pop()
    
    total = 0
    for i in range(5):
        problem_num = i + 1
        expected = ANSWER_KEY[i]
        
        if i < len(lines):
            submitted = lines[i].strip()
            if submitted == expected:
                print(f"Problem {problem_num}: CORRECT ({submitted}) — 20/20")
                total += 20
            else:
                print(f"Problem {problem_num}: INCORRECT (submitted: '{submitted}', expected: '{expected}') — 0/20")
        else:
            print(f"Problem {problem_num}: MISSING — 0/20")
    
    print(f"\nTotal: {total}/100")
    return total

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <answer_file>")
        sys.exit(1)
    
    score = grade(sys.argv[1])
    sys.exit(0 if score == 100 else 1)
