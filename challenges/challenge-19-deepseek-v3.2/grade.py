#!/usr/bin/env python3
"""
Automated grader for Challenge 19: The Deductive Reasoning Gauntlet

Checks format compliance and objective answers for:
- Task 1: required labels per argument and validity judgments
- Task 2: height/arrival ordering puzzle and query answers
- Task 3: required proof-audit sections and overall correctness flag

Usage:
    python grade.py <agent-name>

The script expects the submission at submissions/<agent-name>/submission.md
and reports a detailed, point-by-point breakdown (max automated score: 40).
"""

import os
import re
import sys
from typing import Dict, List, Optional, Tuple


PEOPLE = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
VALIDITY_KEY = {
    "A": "invalid",
    "B": "invalid",
    "C": "invalid",
    "D": "valid",
    "E": "valid",
}


def read_submission(path: str) -> Optional[str]:
    if not os.path.exists(path):
        print(f"Submission file not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_section(content: str, header: str) -> Optional[str]:
    """Extract text under a top-level ## header."""
    pattern = re.compile(rf"##\s+{re.escape(header)}", re.IGNORECASE)
    match = pattern.search(content)
    if not match:
        return None
    start = match.end()
    next_match = re.search(r"\n##\s+", content[start:], re.IGNORECASE)
    end = start + next_match.start() if next_match else len(content)
    return content[start:end].strip()


def extract_subsection(content: str, title: str) -> Optional[str]:
    """Extract text under a ### header within a section."""
    pattern = re.compile(rf"###\s+{re.escape(title)}", re.IGNORECASE)
    match = pattern.search(content)
    if not match:
        return None
    start = match.end()
    next_match = re.search(r"\n###\s+", content[start:], re.IGNORECASE)
    end = start + next_match.start() if next_match else len(content)
    return content[start:end].strip()


def parse_arguments(task1: str) -> Dict[str, str]:
    """Return per-argument text chunks keyed by letter."""
    pattern = re.compile(r"###\s+Argument\s+([A-E])", re.IGNORECASE)
    matches = list(pattern.finditer(task1))
    sections: Dict[str, str] = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(task1)
        sections[match.group(1).upper()] = task1[start:end].strip()
    return sections


def check_task1(task1: str) -> Tuple[int, List[str]]:
    details = []
    format_points = 0
    validity_points = 0

    arg_sections = parse_arguments(task1)
    required_labels = ["Form", "Validity", "Fallacy", "Counterexample"]

    for arg in ["A", "B", "C", "D", "E"]:
        section = arg_sections.get(arg)
        if not section:
            details.append(f"Argument {arg}: section missing (0/2 pts)")
            continue

        missing = [lab for lab in required_labels if not re.search(rf"{lab}\s*:", section, re.IGNORECASE)]
        if missing:
            details.append(f"Argument {arg}: missing labels {missing} (0/1 fmt pt)")
        else:
            format_points += 1

        val_match = re.search(r"Validity\s*:\s*([A-Za-z]+)", section, re.IGNORECASE)
        if val_match:
            validity = val_match.group(1).strip().lower()
            if validity == VALIDITY_KEY[arg]:
                validity_points += 1
                details.append(f"Argument {arg}: validity correct ({validity.title()})")
            else:
                details.append(
                    f"Argument {arg}: validity incorrect (got '{val_match.group(1).strip()}', expected {VALIDITY_KEY[arg].title()})"
                )
        else:
            details.append(f"Argument {arg}: validity label/value missing")

    details.append(f"Task 1 format: {format_points}/5")
    details.append(f"Task 1 validity: {validity_points}/5")
    return format_points + validity_points, details


def parse_order(block: str) -> List[str]:
    """Parse a numbered list of names."""
    entries = re.findall(r"^\s*\d+\.\s*([A-Za-z]+)", block, flags=re.MULTILINE)
    return [name.strip() for name in entries[:6]]


def validate_names(order: List[str]) -> Optional[str]:
    if len(order) != 6:
        return f"expected 6 names, found {len(order)}"
    if len(set(order)) != 6:
        return "names must be unique"
    unknown = [n for n in order if n.title() not in PEOPLE]
    if unknown:
        return f"unknown names: {', '.join(unknown)}"
    return None


def check_height_order(order: List[str]) -> Optional[str]:
    pos = {p: i for i, p in enumerate(order)}
    if pos["Alice"] >= pos["Bob"]:
        return "height constraint failed: Alice must be taller than Bob"
    if not (pos["Diana"] < pos["Frank"] < pos["Bob"]):
        return "height constraint failed: Diana > Frank > Bob"
    if pos["Diana"] >= pos["Eve"]:
        return "height constraint failed: Diana must be taller than Eve"
    if abs(pos["Alice"] - pos["Diana"]) != 3:
        return "height constraint failed: exactly two people between Alice and Diana"
    return None


def check_arrival_order(order: List[str], tallest: str) -> Optional[str]:
    pos = {p: i for i, p in enumerate(order)}
    if pos["Eve"] != 0:
        return "arrival constraint failed: Eve must arrive first"
    if not (pos["Eve"] < pos["Charlie"] < pos["Diana"]):
        return "arrival constraint failed: Eve before Charlie before Diana"
    if not (pos["Alice"] < pos["Bob"] < pos["Charlie"]):
        return "arrival constraint failed: Alice before Bob before Charlie"
    if pos["Frank"] != pos["Charlie"] + 1:
        return "arrival constraint failed: Frank must arrive immediately after Charlie"
    if pos.get(tallest) != 5:
        return f"arrival constraint failed: tallest person ({tallest}) must arrive last"
    return None


def derive_queries(height: List[str], arrival: List[str]) -> Dict[int, str]:
    hpos = {p: i for i, p in enumerate(height)}
    apos = {p: i for i, p in enumerate(arrival)}
    answers: Dict[int, str] = {}
    answers[1] = arrival[apos["Diana"] - 1] if apos["Diana"] > 0 else "N/A"
    answers[2] = height[-1]
    second = arrival[1]
    answers[3] = str(sum(1 for p in PEOPLE if hpos[p] < hpos[second]))
    third_tallest = height[2]
    answers[4] = third_tallest if apos[third_tallest] == 3 else "None"
    answers[5] = "True" if hpos[arrival[2]] < hpos[arrival[4]] else "False"
    return answers


def parse_queries(task2: str) -> Dict[int, str]:
    result: Dict[int, str] = {}
    for i in range(1, 6):
        match = re.search(rf"A{i}\s*:\s*(.+)", task2, re.IGNORECASE)
        if match:
            result[i] = match.group(1).strip()
    return result


def check_task2(task2: str) -> Tuple[int, List[str]]:
    details = []
    score = {"height": 0, "arrival": 0, "queries": 0}

    height_block = extract_subsection(task2, "Height Order")
    arrival_block = extract_subsection(task2, "Arrival Order")
    queries_block = extract_subsection(task2, "Queries") or task2

    height_order = parse_order(height_block or "")
    arrival_order = parse_order(arrival_block or "")

    # Height validation
    name_err = validate_names(height_order)
    if name_err:
        details.append(f"Height order invalid: {name_err}")
    else:
        constraint_err = check_height_order(height_order)
        if constraint_err:
            details.append(f"Height order incorrect: {constraint_err}")
        else:
            score["height"] = 5
            details.append("Height order satisfies all constraints (5/5)")

    # Arrival validation
    tallest = height_order[0] if height_order else ""
    name_err = validate_names(arrival_order)
    if name_err:
        details.append(f"Arrival order invalid: {name_err}")
    else:
        constraint_err = check_arrival_order(arrival_order, tallest)
        if constraint_err:
            details.append(f"Arrival order incorrect: {constraint_err}")
        else:
            score["arrival"] = 5
            details.append("Arrival order satisfies all constraints (5/5)")

    # Query validation (only if both orders valid)
    submission_queries = parse_queries(queries_block)
    if score["height"] == 5 and score["arrival"] == 5:
        expected = derive_queries(height_order, arrival_order)
        correct = 0
        for q_num in range(1, 6):
            submitted = submission_queries.get(q_num)
            exp = expected[q_num]
            if submitted and submitted.strip().lower() == exp.strip().lower():
                correct += 2  # 10 points total, 2 per query
            else:
                details.append(
                    f"Query Q{q_num} incorrect: expected '{exp}', got '{submitted or 'missing'}'"
                )
        score["queries"] = correct
        if correct == 10:
            details.append("All query answers correct (10/10)")
    else:
        details.append("Queries not graded because ordering constraints were not fully satisfied")

    total = score["height"] + score["arrival"] + score["queries"]
    details.append(f"Task 2 scores — Height: {score['height']}/5, Arrival: {score['arrival']}/5, Queries: {score['queries']}/10")
    return total, details


def check_task3(task3: str) -> Tuple[int, List[str]]:
    details = []
    format_points = 0
    correctness_points = 0

    sections = {
        "Logical Errors": extract_subsection(task3, "Logical Errors"),
        "Missing Assumptions": extract_subsection(task3, "Missing Assumptions"),
        "Steps Requiring Justification": extract_subsection(task3, "Steps Requiring Justification"),
        "Overall Correctness": extract_subsection(task3, "Overall Correctness"),
    }

    missing = [name for name, text in sections.items() if not text]
    if missing:
        details.append(f"Missing Task 3 sections: {', '.join(missing)}")
    else:
        format_points = 5
        details.append("All Task 3 sections present (5/5)")

    overall = sections.get("Overall Correctness") or ""
    match = re.search(r"Correctness\s*:\s*([A-Za-z]+)", overall, re.IGNORECASE)
    if match and match.group(1).strip().lower() == "flawed":
        correctness_points = 5
        details.append("Overall Correctness correctly marked as 'Flawed' (5/5)")
    else:
        details.append("Overall Correctness must be marked as 'Flawed' (0/5)")

    return format_points + correctness_points, details


def grade(content: str) -> Tuple[int, List[str]]:
    total_score = 0
    all_details: List[str] = []

    task1 = extract_section(content, "Task 1")
    task2 = extract_section(content, "Task 2")
    task3 = extract_section(content, "Task 3")

    if not task1:
        all_details.append("Task 1 section not found — 0/10")
    else:
        score, details = check_task1(task1)
        total_score += score
        all_details.append(f"Task 1 automated score: {score}/10")
        all_details.extend(details)

    if not task2:
        all_details.append("Task 2 section not found — 0/20")
    else:
        score, details = check_task2(task2)
        total_score += score
        all_details.append(f"Task 2 automated score: {score}/20")
        all_details.extend(details)

    if not task3:
        all_details.append("Task 3 section not found — 0/10")
    else:
        score, details = check_task3(task3)
        total_score += score
        all_details.append(f"Task 3 automated score: {score}/10")
        all_details.extend(details)

    return total_score, all_details


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python grade.py <agent-name>")
        sys.exit(1)

    agent = sys.argv[1]
    submission_path = os.path.join("submissions", agent, "submission.md")
    content = read_submission(submission_path)
    if content is None:
        sys.exit(1)

    score, details = grade(content)

    print("=" * 70)
    print(f"Deductive Reasoning Gauntlet — Automated Grading for '{agent}'")
    print("=" * 70)
    print(f"Automated Score: {score}/40")
    print()
    for line in details:
        print(f"- {line}")
    print()
    print("Manual scoring (60 pts) is separate and not computed by this script.")


if __name__ == "__main__":
    main()
