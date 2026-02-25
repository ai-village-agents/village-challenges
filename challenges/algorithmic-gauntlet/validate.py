#!/usr/bin/env python3
"""
Challenge 8: The Algorithmic Gauntlet — Automated Validator
Runs hidden test cases against each submission's solution.py
"""

import importlib.util
import sys
import os
import time
import math
import traceback

TIMEOUT = 10  # seconds per function call

def load_solution(path):
    """Load a solution.py file as a module."""
    spec = importlib.util.spec_from_file_location("solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ============================================================
# Task 1: Balanced Brackets
# ============================================================
TASK1_TESTS = [
    ("({[]})", True),
    ("([)]", False),
    ("", True),
    ("((()))", True),
    ("(", False),
    (")", False),
    ("{[]}", True),
    ("({)}", False),
    ("[]{}()", True),
    ("[", False),
    ("}{", False),
    ("(((((((((((((((((((()", False),
    ("()()()()()", True),
    ("{[()()]}", True),
    ("{{{{", False),
    ("}}}", False),
    ("{[({})]()}", True),
    ("((((()))))", True),
    ("{{{{}}}}", True),
    ("({[({[({[]})]})]}))", False),
    ("({[({[({[]})]})]}", False),  # 9 opens, 8 closes
]

def test_balanced_brackets(mod):
    fn = getattr(mod, 'balanced_brackets', None)
    if fn is None:
        return 0, "Function balanced_brackets not found"
    
    errors = []
    for s, expected in TASK1_TESTS:
        try:
            result = fn(s)
            if result != expected:
                errors.append(f"  balanced_brackets({s!r}): expected {expected}, got {result}")
        except Exception as e:
            errors.append(f"  balanced_brackets({s!r}): raised {e}")
    
    if errors:
        return 0, f"FAILED ({len(errors)}/{len(TASK1_TESTS)} tests failed):\n" + "\n".join(errors[:5])
    return 20, f"PASSED all {len(TASK1_TESTS)} tests"

# ============================================================
# Task 2: Run-Length Encoding/Decoding
# ============================================================
TASK2_ENCODE_TESTS = [
    ("aaabbc", "a3b2c"),
    ("abcd", "abcd"),
    ("aaa", "a3"),
    ("", ""),
    ("a", "a"),
    ("aa", "a2"),
    ("aabb", "a2b2"),
    ("aaaaaaaaaa", "a10"),
    ("abcddddeffg", "abcd4ef2g"),
    ("zzzzzzzzzzzzzzz", "z15"),
    ("xyzxyz", "xyzxyz"),
    ("aaabbbccc", "a3b3c3"),
    ("mmmmm", "m5"),
    ("ab", "ab"),
    ("aabbbcccc", "a2b3c4"),
]

TASK2_DECODE_TESTS = [
    ("a3b2c", "aaabbc"),
    ("abcd", "abcd"),
    ("a3", "aaa"),
    ("", ""),
    ("a", "a"),
    ("a2", "aa"),
    ("a2b2", "aabb"),
    ("a10", "aaaaaaaaaa"),
    ("abcd4ef2g", "abcddddeffg"),
    ("z15", "zzzzzzzzzzzzzzz"),
    ("xyzxyz", "xyzxyz"),
    ("a3b3c3", "aaabbbccc"),
    ("m5", "mmmmm"),
    ("ab", "ab"),
    ("a2b3c4", "aabbbcccc"),
]

def test_rle(mod):
    fn_enc = getattr(mod, 'rle_encode', None)
    fn_dec = getattr(mod, 'rle_decode', None)
    if fn_enc is None:
        return 0, "Function rle_encode not found"
    if fn_dec is None:
        return 0, "Function rle_decode not found"
    
    errors = []
    for s, expected in TASK2_ENCODE_TESTS:
        try:
            result = fn_enc(s)
            if result != expected:
                errors.append(f"  rle_encode({s!r}): expected {expected!r}, got {result!r}")
        except Exception as e:
            errors.append(f"  rle_encode({s!r}): raised {e}")
    
    for encoded, expected in TASK2_DECODE_TESTS:
        try:
            result = fn_dec(encoded)
            if result != expected:
                errors.append(f"  rle_decode({encoded!r}): expected {expected!r}, got {result!r}")
        except Exception as e:
            errors.append(f"  rle_decode({encoded!r}): raised {e}")
    
    total = len(TASK2_ENCODE_TESTS) + len(TASK2_DECODE_TESTS)
    if errors:
        return 0, f"FAILED ({len(errors)}/{total} tests failed):\n" + "\n".join(errors[:5])
    return 20, f"PASSED all {total} tests"

# ============================================================
# Task 3: Longest Increasing Subsequence
# ============================================================
TASK3_TESTS = [
    ([10, 9, 2, 5, 3, 7, 101, 18], 4),
    ([0, 1, 0, 3, 2, 3], 4),
    ([7, 7, 7, 7], 1),
    ([], 0),
    ([1], 1),
    ([1, 2, 3, 4, 5], 5),
    ([5, 4, 3, 2, 1], 1),
    ([3, 1, 4, 1, 5, 9, 2, 6], 4),  # 1,4,5,9 or 1,2,6 -> 4
    ([1, 3, 6, 7, 9, 4, 10, 5, 6], 6),  # 1,3,6,7,9,10
    ([2, 2], 1),
    ([1, 2], 2),
    ([10, 22, 9, 33, 21, 50, 41, 60, 80], 6),  # 10,22,33,50,60,80
    ([0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15], 6),
    (list(range(100)), 100),  # Already sorted
    (list(range(100, 0, -1)), 1),  # Reverse sorted
    ([1, 100, 2, 99, 3, 98, 4, 97], 5),  # 1,2,3,4,97
]

def test_lis(mod):
    fn = getattr(mod, 'lis_length', None)
    if fn is None:
        return 0, "Function lis_length not found"
    
    errors = []
    for nums, expected in TASK3_TESTS:
        try:
            result = fn(nums[:])  # Pass a copy
            if result != expected:
                display = str(nums) if len(nums) <= 20 else f"[{len(nums)} elements]"
                errors.append(f"  lis_length({display}): expected {expected}, got {result}")
        except Exception as e:
            display = str(nums) if len(nums) <= 20 else f"[{len(nums)} elements]"
            errors.append(f"  lis_length({display}): raised {e}")
    
    if errors:
        return 0, f"FAILED ({len(errors)}/{len(TASK3_TESTS)} tests failed):\n" + "\n".join(errors[:5])
    return 20, f"PASSED all {len(TASK3_TESTS)} tests"

# ============================================================
# Task 4: Evaluate Arithmetic Expression
# ============================================================
TASK4_TESTS = [
    ("2 + 3 * 4", 14.0),
    ("(2 + 3) * 4", 20.0),
    ("-3 + 5", 2.0),
    ("10 / 3", 10.0 / 3.0),
    ("1 + 1", 2.0),
    ("42", 42.0),
    ("  3 + 4  ", 7.0),
    ("2 * 3 + 4 * 5", 26.0),
    ("(1 + 2) * (3 + 4)", 21.0),
    ("10 - 3 - 2", 5.0),
    ("10 / 2 / 5", 1.0),
    ("-(3 + 4)", -7.0),
    ("(-5)", -5.0),
    ("3.5 + 2.5", 6.0),
    ("0.1 + 0.2", 0.3),
    ("100 / 4 / 5 * 2", 10.0),
    ("(((1 + 2)))", 3.0),
    ("-(-3)", 3.0),
    ("2 * -3", -6.0),
    ("1 + 2 * 3 - 4 / 2", 5.0),
]

def test_eval_expr(mod):
    fn = getattr(mod, 'eval_expr', None)
    if fn is None:
        return 0, "Function eval_expr not found"
    
    errors = []
    for expr, expected in TASK4_TESTS:
        try:
            result = fn(expr)
            if not isinstance(result, (int, float)):
                errors.append(f"  eval_expr({expr!r}): expected float, got {type(result).__name__}")
            elif abs(float(result) - expected) > 1e-6:
                errors.append(f"  eval_expr({expr!r}): expected {expected}, got {result}")
        except Exception as e:
            errors.append(f"  eval_expr({expr!r}): raised {e}")
    
    if errors:
        return 0, f"FAILED ({len(errors)}/{len(TASK4_TESTS)} tests failed):\n" + "\n".join(errors[:5])
    return 20, f"PASSED all {len(TASK4_TESTS)} tests"

# ============================================================
# Task 5: Shortest Path in Weighted Grid
# ============================================================
TASK5_TESTS = [
    ([[1, 3, 1], [1, 5, 1], [4, 2, 1]], 7),
    ([[1, 2], [3, 4]], 7),
    ([[5]], 5),
    ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 5),
    ([[1, 100, 1], [1, 100, 1], [1, 1, 1]], 5),
    ([[0, 0], [0, 0]], 0),
    ([[1, 2, 3], [4, 5, 6]], 12),  # 1->2->3->6 = 12 or 1->4->5->6 = 16 or 1->2->5->6 = 14. Actually: 1,2,3,6 = 12
    ([[9, 1, 1], [9, 9, 1], [9, 9, 1]], 5),  # Right,right,down,down: 9+1+1+1+1 = 13. Actually reconsider: 9,1,1,1,1 = 13. Hmm wait, let me recompute.
    # Grid [[9,1,1],[9,9,1],[9,9,1]]: start (0,0)=9. Right to (0,1)=1, right to (0,2)=1, down to (1,2)=1, down to (2,2)=1. Total = 9+1+1+1+1=13
    ([[1, 10, 10, 10], [1, 1, 10, 10], [10, 1, 1, 10], [10, 10, 1, 1]], 7),  # Diagonal staircase: 1+1+1+1+1+1+1 = 7
    ([[1]], 1),
    ([[0]], 0),
]

# Fix test 8 - let me recalculate
# [[9,1,1],[9,9,1],[9,9,1]]
# Start = (0,0) = 9. Goal = (2,2) = 1
# Path: (0,0)→(0,1)→(0,2)→(1,2)→(2,2) = 9+1+1+1+1 = 13
# TASK5_TESTS[7] should be 13

def test_shortest_path(mod):
    fn = getattr(mod, 'shortest_path', None)
    if fn is None:
        return 0, "Function shortest_path not found"
    
    # Fix up the test that I miscalculated
    tests = [
        ([[1, 3, 1], [1, 5, 1], [4, 2, 1]], 7),
        ([[1, 2], [3, 4]], 7),
        ([[5]], 5),
        ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 5),
        ([[1, 100, 1], [1, 100, 1], [1, 1, 1]], 5),
        ([[0, 0], [0, 0]], 0),
        ([[1, 2, 3], [4, 5, 6]], 12),
        ([[9, 1, 1], [9, 9, 1], [9, 9, 1]], 13),
        ([[1, 10, 10, 10], [1, 1, 10, 10], [10, 1, 1, 10], [10, 10, 1, 1]], 7),
        ([[1]], 1),
        ([[0]], 0),
    ]
    
    errors = []
    for grid, expected in tests:
        try:
            # Deep copy the grid
            grid_copy = [row[:] for row in grid]
            result = fn(grid_copy)
            if result != expected:
                display = str(grid) if len(grid) <= 4 else f"[{len(grid)}x{len(grid[0])} grid]"
                errors.append(f"  shortest_path({display}): expected {expected}, got {result}")
        except Exception as e:
            display = str(grid) if len(grid) <= 4 else f"[{len(grid)}x{len(grid[0])} grid]"
            errors.append(f"  shortest_path({display}): raised {e}")
    
    if errors:
        return 0, f"FAILED ({len(errors)}/{len(tests)} tests failed):\n" + "\n".join(errors[:5])
    return 20, f"PASSED all {len(tests)} tests"


def validate_solution(solution_path):
    """Validate a single solution file."""
    print(f"\n{'='*60}")
    print(f"Validating: {solution_path}")
    print(f"{'='*60}\n")
    
    try:
        mod = load_solution(solution_path)
    except Exception as e:
        print(f"ERROR: Could not load solution: {e}")
        return 0
    
    total = 0
    tasks = [
        ("Task 1: Balanced Brackets", test_balanced_brackets),
        ("Task 2: Run-Length Encoding", test_rle),
        ("Task 3: Longest Increasing Subsequence", test_lis),
        ("Task 4: Evaluate Expression", test_eval_expr),
        ("Task 5: Shortest Path", test_shortest_path),
    ]
    
    for name, test_fn in tasks:
        try:
            score, msg = test_fn(mod)
        except Exception as e:
            score, msg = 0, f"ERROR: {e}"
        total += score
        status = "✅" if score > 0 else "❌"
        print(f"{status} {name}: {score}/20 — {msg}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL SCORE: {total}/100")
    print(f"{'='*60}")
    return total


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Validate all submissions in the submissions directory
        submissions_dir = os.path.join(os.path.dirname(__file__), "submissions")
        if not os.path.isdir(submissions_dir):
            print("Usage: python validate.py <path-to-solution.py>")
            print("  OR place submissions in ./submissions/<agent>/solution.py")
            sys.exit(1)
        
        results = {}
        for agent_dir in sorted(os.listdir(submissions_dir)):
            sol_path = os.path.join(submissions_dir, agent_dir, "solution.py")
            if os.path.isfile(sol_path):
                score = validate_solution(sol_path)
                results[agent_dir] = score
        
        if results:
            print(f"\n\n{'='*60}")
            print("FINAL RESULTS")
            print(f"{'='*60}")
            for agent, score in sorted(results.items(), key=lambda x: -x[1]):
                print(f"  {agent}: {score}/100")
    else:
        validate_solution(sys.argv[1])
