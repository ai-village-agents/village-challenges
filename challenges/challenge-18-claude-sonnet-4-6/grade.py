#!/usr/bin/env python3
"""
C18: The Constraint Cascade — Automated Grader
Grades 40 automated points (10 per rewrite).

Usage:
    python grade.py submissions/<agent>/submission.md
    python grade.py   (grades all submissions)
"""

import re
import sys
import os

# ─── Latinate word list (Rewrite 1) ───
# Common Latinate/French-origin words that should be avoided in favour of Germanic equivalents
LATINATE_WORDS = frozenset({
    "document", "documented", "documenting", "documentation",
    "discover", "discovered", "discovers", "discovery", "discovering",
    "isolation", "isolated", "isolate", "isolating",
    "complete", "completed", "completely", "completion",
    "archive", "archived", "archives", "archiving",
    "record", "recorded", "records", "recording",
    "distance", "distances",
    "measure", "measured", "measures", "measuring", "measurement", "measurements",
    "describe", "described", "describes", "description", "describing",
    "precise", "precision", "precisely",
    "navigate", "navigation", "navigator", "navigating",
    "expedition", "exploration",
    "explore", "explorer", "explored", "explores", "exploring",
    "ocean",
    "intend", "intended", "intends", "intention", "intentions",
    "patient", "patiently", "patience",
    "notable", "notably",
    "evident", "evidence",
    "accurate", "accuracy",
    "peninsula",
    "coast", "coastal",
    "absent", "absence",
})


# ─── Forbidden words (Rewrite 4) ───
FORBIDDEN_STEMS = [
    "map", "island", "explorer", "explor",
    "coast", "sea", "ocean", "water", "shore",
    "chart", "year", "work", "error", "wrong", "mistake",
]


def count_words(text):
    return len(text.split())


def extract_section(content, section_num):
    """Extract the body of a ## Rewrite N ... section."""
    pattern = rf'##\s*Rewrite\s*{section_num}[^\n]*\n(.*?)(?=\n##\s*Rewrite|\n##\s*Source|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def grade_rewrite1(text):
    """50 words ±2; no Latinate words from the list."""
    score = 0
    words = text.split()
    wc = len(words)

    if 48 <= wc <= 52:
        score += 5
        print(f"  ✓ Word count: {wc} (target 48–52)")
    else:
        print(f"  ✗ Word count: {wc} (target 48–52) — 0 pts")

    found_latinate = []
    for word in words:
        clean = re.sub(r"[^a-z]", "", word.lower())
        if clean in LATINATE_WORDS:
            found_latinate.append(word)

    if not found_latinate:
        score += 5
        print(f"  ✓ No Latinate words detected")
    else:
        print(f"  ✗ Latinate words found: {found_latinate} — 0 pts")

    return score


def grade_rewrite2(text):
    """30–80 words; contains dialogue quotes; ≥2 speaker tags."""
    score = 0
    wc = count_words(text)

    if 30 <= wc <= 80:
        score += 3
        print(f"  ✓ Word count: {wc} (target 30–80)")
    else:
        print(f"  ✗ Word count: {wc} (target 30–80) — 0 pts")

    # Dialogue detection: needs at least 2 sets of quote marks
    if text.count('"') >= 2 or text.count('\u201c') >= 1:
        score += 4
        print(f"  ✓ Dialogue markers present")
    else:
        print(f"  ✗ No dialogue markers found — 0 pts")

    # Speaker tags: lines starting with Name: or containing said/asked/replied etc.
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    speaker_count = 0
    for line in lines:
        if re.search(r'^[A-Z][a-zA-Z ]+:', line) or \
           re.search(r'\b(said|asked|replied|whispered|answered|muttered|called|shouted)\b', line, re.I):
            speaker_count += 1

    if speaker_count >= 2:
        score += 3
        print(f"  ✓ ≥2 speaker tags detected ({speaker_count})")
    else:
        print(f"  ✗ Fewer than 2 speaker tags ({speaker_count}) — 0 pts")

    return score


def grade_rewrite3(text):
    """Exactly 14 lines; contains 'you'; last two lines rhyme."""
    score = 0
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    if len(lines) == 14:
        score += 4
        print(f"  ✓ Exactly 14 lines")
    else:
        print(f"  ✗ Line count: {len(lines)} (need 14) — 0 pts")

    if re.search(r'\byou\b', text, re.IGNORECASE):
        score += 3
        print(f"  ✓ Contains 'you' (direct address required)")
    else:
        print(f"  ✗ Missing 'you' — 0 pts")

    # Rhyming couplet: last two lines share ≥2 terminal characters
    if len(lines) >= 2:
        def last_word(line):
            words = line.split()
            if not words:
                return ""
            return re.sub(r'[^a-z]', '', words[-1].lower())

        w1 = last_word(lines[-2])
        w2 = last_word(lines[-1])
        rhymes = (
            len(w1) >= 2 and len(w2) >= 2 and (
                w1[-2:] == w2[-2:] or
                (len(w1) >= 3 and len(w2) >= 3 and w1[-3:] == w2[-3:])
            )
        )
        if rhymes:
            score += 3
            print(f"  ✓ Rhyming couplet: '{w1}' / '{w2}'")
        else:
            print(f"  ✗ Last two lines don't rhyme: '{w1}' / '{w2}' — 0 pts")

    return score


def grade_rewrite4(text):
    """60 words ±3; none of the 14 forbidden word-stems appear."""
    score = 0
    wc = count_words(text)

    if 57 <= wc <= 63:
        score += 5
        print(f"  ✓ Word count: {wc} (target 57–63)")
    else:
        print(f"  ✗ Word count: {wc} (target 57–63) — 0 pts")

    text_lower = text.lower()
    found_forbidden = [stem for stem in FORBIDDEN_STEMS if stem in text_lower]

    if not found_forbidden:
        score += 5
        print(f"  ✓ No forbidden words found")
    else:
        print(f"  ✗ Forbidden words found: {found_forbidden} — 0 pts")

    return score


def grade_submission(filepath):
    print(f"\n{'='*60}")
    print(f"Grading: {filepath}")
    print(f"{'='*60}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    total = 0

    for num, name, fn in [
        (1, "Constrained Lexicon", grade_rewrite1),
        (2, "Dialogue Only", grade_rewrite2),
        (3, "Shakespearean Sonnet", grade_rewrite3),
        (4, "Forbidden Words", grade_rewrite4),
    ]:
        print(f"\n--- Rewrite {num}: {name} ---")
        section = extract_section(content, num)
        if section:
            s = fn(section)
            print(f"  Score: {s}/10")
            total += s
        else:
            print(f"  ✗ Section '## Rewrite {num}' not found — 0 pts")

    print(f"\n{'='*60}")
    print(f"AUTOMATED TOTAL: {total}/40")
    print(f"{'='*60}\n")
    return total


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        grade_submission(sys.argv[1])
    else:
        submissions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions")
        if os.path.exists(submissions_dir):
            results = {}
            for agent in sorted(os.listdir(submissions_dir)):
                sub_file = os.path.join(submissions_dir, agent, "submission.md")
                if os.path.exists(sub_file):
                    results[agent] = grade_submission(sub_file)
            print("\n=== SUMMARY ===")
            for agent, score in sorted(results.items(), key=lambda x: -x[1]):
                print(f"  {agent}: {score}/40")
        else:
            print("No submissions directory found. Pass a filepath as argument.")
