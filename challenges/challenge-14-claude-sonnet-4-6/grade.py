#!/usr/bin/env python3
"""
Grader for Challenge #14: The Logic Grid Gauntlet
Usage: python3 grade.py <path-to-answers.md>
Returns: JSON with score and breakdown
"""

import sys
import re
import json

# ── Answer Keys ──────────────────────────────────────────────────────────────

PUZZLE1_KEY = {
    "1": {"name": "evie",  "drink": "coffee", "topic": "math"},
    "2": {"name": "bixby", "drink": "milk",   "topic": "art"},
    "3": {"name": "dex",   "drink": "juice",  "topic": "science"},
    "4": {"name": "cleo",  "drink": "tea",    "topic": "history"},
    "5": {"name": "aria",  "drink": "water",  "topic": "coding"},
}

PUZZLE2_KEY = {
    "dr. fenn": {"lab": "b", "project": "materials", "language": "java",   "day": "monday"},
    "dr. gao":  {"lab": "c", "project": "vision",    "language": "python", "day": "tuesday"},
    "dr. hart": {"lab": "a", "project": "genetics",  "language": "c++",    "day": "thursday"},
    "dr. ibis": {"lab": "e", "project": "robotics",  "language": "go",     "day": "friday"},
    "dr. jole": {"lab": "d", "project": "climate",   "language": "rust",   "day": "wednesday"},
}

PUZZLE3_KEY = {
    "alpha":   {"coach": "hayes",  "city": "boston",  "color": "white",  "rank": "3rd"},
    "beta":    {"coach": "dixon",  "city": "miami",   "color": "orange", "rank": "4th"},
    "gamma":   {"coach": "carter", "city": "denver",  "color": "green",  "rank": "1st"},
    "delta":   {"coach": "grant",  "city": "seattle", "color": "gold",   "rank": "2nd"},
    "epsilon": {"coach": "flynn",  "city": "chicago", "color": "blue",   "rank": "5th"},
    "zeta":    {"coach": "evans",  "city": "tampa",   "color": "red",    "rank": "6th"},
}

# ── Parser ───────────────────────────────────────────────────────────────────

def parse_table(text, section_header):
    """Extract a markdown table from the section following section_header."""
    # Find section
    pattern = re.compile(
        rf'{re.escape(section_header)}.*?(\|.*?\|.*?\n(?:\|[-:| ]+\|\n)?(?:\|.*?\|.*?\n)*)',
        re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(text)
    if not match:
        return []
    
    table_text = match.group(1)
    rows = []
    for line in table_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('|--') or line.startswith('| --') or re.match(r'^\|[-| :]+\|$', line):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if cells:
            rows.append(cells)
    
    # Remove header row if present (non-numeric first cell for puzzle 1, non-"Dr." for puzzle 2, etc.)
    return rows

def normalize(s):
    """Normalize a string for comparison."""
    return s.strip().lower()

# ── Graders ──────────────────────────────────────────────────────────────────

def grade_puzzle1(text):
    """Grade Puzzle 1 — Village Café. 6 pts per correct row (all 3 attrs)."""
    score = 0
    details = {}
    
    rows = parse_table(text, "Puzzle 1")
    
    found = {}
    for row in rows:
        if len(row) < 4:
            continue
        table_num, name, drink, topic = row[0], row[1], row[2], row[3]
        table_key = normalize(table_num)
        if table_key in PUZZLE1_KEY:
            found[table_key] = {
                "name": normalize(name),
                "drink": normalize(drink),
                "topic": normalize(topic),
            }
    
    for table_key, correct in PUZZLE1_KEY.items():
        if table_key not in found:
            details[f"table_{table_key}"] = "missing"
            continue
        submitted = found[table_key]
        if (submitted["name"] == correct["name"] and
            submitted["drink"] == correct["drink"] and
            submitted["topic"] == correct["topic"]):
            score += 6
            details[f"table_{table_key}"] = "correct"
        else:
            details[f"table_{table_key}"] = f"wrong (got name={submitted['name']}, drink={submitted['drink']}, topic={submitted['topic']})"
    
    return score, details

def grade_puzzle2(text):
    """Grade Puzzle 2 — Research Lab. 7 pts per correct researcher (all 4 attrs)."""
    score = 0
    details = {}
    
    rows = parse_table(text, "Puzzle 2")
    
    found = {}
    for row in rows:
        if len(row) < 5:
            continue
        name_raw = normalize(row[0])
        # Match to known researchers
        for key in PUZZLE2_KEY:
            if key in name_raw or name_raw in key:
                found[key] = {
                    "lab": normalize(row[1]),
                    "project": normalize(row[2]),
                    "language": normalize(row[3]),
                    "day": normalize(row[4]),
                }
                break
    
    for name_key, correct in PUZZLE2_KEY.items():
        display = name_key.title()
        if name_key not in found:
            details[display] = "missing"
            continue
        submitted = found[name_key]
        if (submitted["lab"] == correct["lab"] and
            submitted["project"] == correct["project"] and
            submitted["language"] == correct["language"] and
            submitted["day"] == correct["day"]):
            score += 7
            details[display] = "correct"
        else:
            details[display] = (
                f"wrong (lab:{submitted['lab']} proj:{submitted['project']} "
                f"lang:{submitted['language']} day:{submitted['day']})"
            )
    
    return score, details

def grade_puzzle3(text):
    """Grade Puzzle 3 — Tournament. ~5.83 pts per team (35/6), awarded whole."""
    score = 0
    details = {}
    correct_count = 0
    
    rows = parse_table(text, "Puzzle 3")
    
    found = {}
    for row in rows:
        if len(row) < 5:
            continue
        team_raw = normalize(row[0])
        for key in PUZZLE3_KEY:
            if key == team_raw:
                found[key] = {
                    "coach": normalize(row[1]),
                    "city": normalize(row[2]),
                    "color": normalize(row[3]),
                    "rank": normalize(row[4]),
                }
                break
    
    for team_key, correct in PUZZLE3_KEY.items():
        display = team_key.title()
        if team_key not in found:
            details[display] = "missing"
            continue
        submitted = found[team_key]
        if (submitted["coach"] == correct["coach"] and
            submitted["city"] == correct["city"] and
            submitted["color"] == correct["color"] and
            submitted["rank"] == correct["rank"]):
            correct_count += 1
            details[display] = "correct"
        else:
            details[display] = (
                f"wrong (coach:{submitted['coach']} city:{submitted['city']} "
                f"color:{submitted['color']} rank:{submitted['rank']})"
            )
    
    # 35 points split across 6 teams: round to nearest integer per team
    # Award: correct_count / 6 * 35, rounded
    score = round(correct_count / 6 * 35)
    return score, details

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 grade.py <path-to-answers.md>")
        sys.exit(1)
    
    answers_path = sys.argv[1]
    try:
        with open(answers_path, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        result = {"score": 0, "error": f"File not found: {answers_path}"}
        print(json.dumps(result, indent=2))
        sys.exit(1)
    
    p1_score, p1_details = grade_puzzle1(text)
    p2_score, p2_details = grade_puzzle2(text)
    p3_score, p3_details = grade_puzzle3(text)
    
    total = p1_score + p2_score + p3_score
    
    result = {
        "total_score": total,
        "puzzle1": {
            "score": p1_score,
            "max": 30,
            "details": p1_details,
        },
        "puzzle2": {
            "score": p2_score,
            "max": 35,
            "details": p2_details,
        },
        "puzzle3": {
            "score": p3_score,
            "max": 35,
            "details": p3_details,
        },
    }
    
    print(json.dumps(result, indent=2))
    return total

if __name__ == "__main__":
    main()
