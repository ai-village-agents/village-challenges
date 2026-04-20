#!/usr/bin/env python3
"""
Grader for Live Challenge 4: The Cipher Chain
Deterministic scoring: 20 points per correctly decrypted puzzle.
"""

import sys
import os

ANSWERS = {
    1: "VIGENERE",
    2: "THE RAILS ARE FOUR",
    3: "KEYISMARCO",
    4: "ALPHABETSHIFTISTWELVE",
    5: "VILLAGE AGENTS SOLVE PUZZLES TOGETHER",
}

def normalize(s):
    """Normalize answer for comparison."""
    return s.strip().upper()

def grade(filepath):
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return 0

    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    total = 0
    results = []

    for i in range(1, 6):
        if i - 1 < len(lines):
            submitted = normalize(lines[i - 1])
            expected = normalize(ANSWERS[i])
            # For puzzle 4, accept with or without trailing X padding
            if i == 4:
                match = (submitted == expected or 
                         submitted == expected + "XXXX" or
                         submitted.rstrip('X') == expected)
            else:
                match = (submitted == expected)
            
            if match:
                total += 20
                results.append(f"  Puzzle {i}: ✅ CORRECT (+20)")
            else:
                results.append(f"  Puzzle {i}: ❌ WRONG (expected '{expected}', got '{submitted}')")
        else:
            results.append(f"  Puzzle {i}: ❌ MISSING")

    print(f"Score: {total}/100")
    print()
    for r in results:
        print(r)
    
    return total

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-answer.txt>")
        sys.exit(1)
    
    score = grade(sys.argv[1])
    sys.exit(0 if score == 100 else 1)
