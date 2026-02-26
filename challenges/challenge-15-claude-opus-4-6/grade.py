#!/usr/bin/env python3
"""
Regex Golf Challenge — Grader
Validates submitted regex patterns against match/reject lists and computes scores.
Usage: python3 grade.py submissions/<agent-name>/answers.json
"""

import json
import re
import sys
import os

# Round definitions
ROUNDS = {
    "round1": {
        "name": "Round 1: Vowel Precision",
        "match": ["pit", "pat", "pet", "pot", "put"],
        "reject": ["pyt", "pst", "apt", "tap", "top", "tip", "spit", "past", "peat", "pout", "poet"],
        "par": 27,
    },
    "round2": {
        "name": "Round 2: Quantifier Basics",
        "match": ["ab", "aab", "aaab", "aaaab"],
        "reject": ["b", "a", "ba", "abb", "aabb", "abab", "aaba", "aaabb"],
        "par": 23,
    },
    "round3": {
        "name": "Round 3: Double Trouble",
        "match": ["aardvark", "balloon", "coffee", "llama", "succeed"],
        "reject": ["animal", "zebra", "falcon", "tiger", "primate", "gopher", "cobra", "puma", "ibex", "lemur"],
        "par": 29,
    },
    "round4": {
        "name": "Round 4: Email Validation",
        "match": ["a@b.c", "foo@bar.com", "x@y.zz", "test@mail.org"],
        "reject": ["@b.c", "a@b.", "a@.c", "foo@bar", "foo.bar@com", "a@@b.c", "a@b@c.d", "a@b.c.d", "@", "a@b"],
        "par": 32,
    },
    "round5": {
        "name": "Round 5: Deja Vu",
        "match": ["abab", "cdcd", "xyxy", "abcabc", "xyzxyz", "aaaa"],
        "reject": ["abcd", "xyza", "abba", "abcab", "xyzxy", "aabb", "abcabcd", "aba", "xyz", "abcba"],
        "par": 27,
    },
}


def grade_round(pattern_str, round_def):
    """
    Grade a single round. Returns (score, length, detail_lines).
    """
    name = round_def["name"]
    par = round_def["par"]
    match_list = round_def["match"]
    reject_list = round_def["reject"]

    if not isinstance(pattern_str, str):
        return 0, 0, [f"  {name}: INVALID (pattern is not a string) => 0 pts"]

    length = len(pattern_str)

    # Try to compile
    try:
        regex = re.compile(pattern_str)
    except re.error as e:
        return 0, length, [f"  {name}: COMPILE ERROR ({e}) => 0 pts"]

    # Check match list (must fullmatch all)
    missed = [s for s in match_list if not regex.fullmatch(s)]

    # Check reject list (must NOT fullmatch any)
    false_pos = [s for s in reject_list if regex.fullmatch(s)]

    if missed or false_pos:
        lines = [f"  {name}: INCORRECT => 0 pts"]
        if missed:
            lines.append(f"    Failed to match: {missed}")
        if false_pos:
            lines.append(f"    Incorrectly matched: {false_pos}")
        return 0, length, lines

    # Valid — compute score
    score = max(0, par - length)
    return score, length, [f"  {name}: len={length}, par={par} => {score} pts"]


def grade_submission(filepath):
    """Grade a full submission file. Prints report and returns total score."""
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        try:
            answers = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON — {e}")
            sys.exit(1)

    if not isinstance(answers, dict):
        print("Error: answers.json must be a JSON object")
        sys.exit(1)

    total_score = 0
    total_length = 0
    all_lines = []

    for round_key in ["round1", "round2", "round3", "round4", "round5"]:
        round_def = ROUNDS[round_key]
        if round_key not in answers:
            all_lines.append(f"  {round_def['name']}: MISSING => 0 pts")
            continue
        pattern = answers[round_key]
        score, length, lines = grade_round(pattern, round_def)
        total_score += score
        total_length += length
        all_lines.extend(lines)

    print(f"Grading: {filepath}")
    print("=" * 55)
    for line in all_lines:
        print(line)
    print("=" * 55)
    print(f"Total score: {total_score}/100")
    print(f"Total pattern length: {total_length} chars")
    print(f"\n{total_score}")
    return total_score


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} submissions/<agent-name>/answers.json")
        sys.exit(1)
    grade_submission(sys.argv[1])
