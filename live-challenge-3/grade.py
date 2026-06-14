#!/usr/bin/env python3
"""
Grader for Live Challenge 3: The AI Conference
Scores 20 points per correct row (all 5 attributes must match).
Total: 100 points.
"""

import sys
import os

ANSWER_KEY = [
    "Alice, Google, NLP, 9 AM, Grand, Java",
    "Bob, Anthropic, Reinforcement Learning, 11 AM, Marriott, C++",
    "Carol, OpenAI, Alignment, 1 PM, Ritz, Rust",
    "Dave, DeepMind, Computer Vision, 10 AM, Plaza, Julia",
    "Eve, Meta, Robotics, 2 PM, Hilton, Python",
]

POINTS_PER_ROW = 20


def normalize(line: str) -> str:
    """Normalize a line for comparison: strip whitespace, normalize internal spaces."""
    return ", ".join(part.strip() for part in line.split(","))


def grade(submission_path: str) -> dict:
    """Grade a submission file and return results."""
    if not os.path.exists(submission_path):
        return {"score": 0, "max_score": 100, "details": "Submission file not found."}

    with open(submission_path, "r", encoding="utf-8") as f:
        raw_lines = f.read().strip().splitlines()

    # Filter out empty lines
    lines = [l.strip() for l in raw_lines if l.strip()]

    if len(lines) != 5:
        return {
            "score": 0,
            "max_score": 100,
            "details": f"Expected 5 lines, got {len(lines)}. Each line should be one researcher.",
        }

    score = 0
    details = []

    for i, (submitted, expected) in enumerate(zip(lines, ANSWER_KEY)):
        norm_submitted = normalize(submitted)
        norm_expected = normalize(expected)
        name = expected.split(",")[0].strip()

        if norm_submitted == norm_expected:
            score += POINTS_PER_ROW
            details.append(f"  ✅ {name}: Correct (+{POINTS_PER_ROW} pts)")
        else:
            details.append(f"  ❌ {name}: Incorrect (0 pts)")
            details.append(f"       Expected: {norm_expected}")
            details.append(f"       Got:      {norm_submitted}")

    return {
        "score": score,
        "max_score": 100,
        "details": "\n".join(details),
    }


def main():
    if len(sys.argv) < 2:
        # Try to find submission in standard location
        base = os.path.dirname(os.path.abspath(__file__))
        # Look for any submission in submissions/
        submissions_dir = os.path.join(base, "submissions")
        if os.path.isdir(submissions_dir):
            for agent_name in sorted(os.listdir(submissions_dir)):
                answer_path = os.path.join(submissions_dir, agent_name, "answer.txt")
                if os.path.exists(answer_path):
                    print(f"\n{'='*50}")
                    print(f"Grading: {agent_name}")
                    print(f"{'='*50}")
                    result = grade(answer_path)
                    print(result["details"])
                    print(f"\n  Score: {result['score']}/{result['max_score']}")
            return
        else:
            print(f"Usage: python {sys.argv[0]} <path-to-answer.txt>")
            print("   Or: place submissions in submissions/<agent-name>/answer.txt")
            sys.exit(1)
    else:
        submission_path = sys.argv[1]
        result = grade(submission_path)
        print(f"Grading: {submission_path}")
        print(result["details"])
        print(f"\nScore: {result['score']}/{result['max_score']}")


if __name__ == "__main__":
    main()
