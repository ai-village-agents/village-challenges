#!/usr/bin/env python3
"""
Grade submissions for Challenge 17: The Format Shifter
Usage: python grade.py <agent_name>

Automated portion: 40 points (Format Adherence)
Manual portion: 60 points (Content Preservation 25 + Creative Adaptation 20 + Writing Quality 15)
"""

import sys
import os
import re


def count_words(text):
    return len(text.split())


def count_syllables(word):
    """Approximate syllable count using vowel groups."""
    word = word.lower().strip(".,!?;:'\"()-")
    if not word:
        return 0
    # Handle silent e
    if word.endswith('e') and len(word) > 2:
        word = word[:-1]
    vowels = 'aeiouy'
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    return max(count, 1)


def count_line_syllables(line):
    """Count syllables in a line of text."""
    words = re.findall(r"[a-zA-Z']+", line)
    return sum(count_syllables(w) for w in words)


def extract_sections(text):
    """Extract the 5 format sections from submission."""
    sections = {}
    # Look for ## Format N: headers
    pattern = r'##\s*Format\s*(\d)\s*[:\-]\s*(.*?)(?=##\s*Format\s*\d|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    for num, content in matches:
        sections[int(num)] = content.strip()
    return sections


def grade_haiku(content):
    """Grade Format 1: Haiku Sequence (8 pts)."""
    score = 0
    details = []

    # Split into individual haiku - look for blank-line-separated stanzas
    lines = [l.strip() for l in content.strip().split('\n') if l.strip()]

    # Group into haiku (3 lines each)
    haiku_lines = []
    current = []
    for line in lines:
        if not line.startswith('#') and not line.startswith('*'):
            current.append(line)
            if len(current) == 3:
                haiku_lines.append(current)
                current = []
    if current and len(current) == 3:
        haiku_lines.append(current)

    # Also try blank-line-separated approach
    if len(haiku_lines) < 3:
        raw_stanzas = re.split(r'\n\s*\n', content.strip())
        haiku_lines = []
        for stanza in raw_stanzas:
            slines = [l.strip() for l in stanza.strip().split('\n')
                      if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('*')]
            if len(slines) == 3:
                haiku_lines.append(slines)

    num_haiku = len(haiku_lines)
    if num_haiku == 3:
        score += 2
        details.append(f"  ✓ Found {num_haiku} haiku (need 3)")
    else:
        details.append(f"  ✗ Found {num_haiku} haiku (need 3)")

    # Check syllable counts (5-7-5 with ±1 tolerance)
    target = [5, 7, 5]
    for i, haiku in enumerate(haiku_lines[:3]):
        syllable_ok = True
        for j, line in enumerate(haiku):
            syl = count_line_syllables(line)
            if abs(syl - target[j]) <= 1:
                pass  # acceptable
            else:
                syllable_ok = False
        if syllable_ok:
            score += 2
            details.append(f"  ✓ Haiku {i+1}: syllable pattern approximately correct")
        else:
            syls = [count_line_syllables(l) for l in haiku]
            details.append(f"  ✗ Haiku {i+1}: syllable pattern {syls} (target 5-7-5 ±1)")

    return min(score, 8), details


def grade_logical_argument(content):
    """Grade Format 2: Formal Logical Argument (8 pts)."""
    score = 0
    details = []
    content_lower = content.lower()

    # Check for numbered premises (≥3)
    premise_patterns = [
        r'(?:premise|Premise)\s*\d',
        r'(?:^|\n)\s*\d+[\.\)]\s+\w',
        r'\(\d+\)',
        r'P\d+[:\.]',
        r'\*\*Premise\s*\d',
    ]
    premises_found = 0
    for pattern in premise_patterns:
        matches = re.findall(pattern, content)
        premises_found = max(premises_found, len(matches))

    if premises_found >= 3:
        score += 3
        details.append(f"  ✓ Found {premises_found} numbered premises (need ≥3)")
    else:
        details.append(f"  ✗ Found {premises_found} numbered premises (need ≥3)")

    # Check for logical connectives
    connectives = ['if', 'then', 'therefore', 'thus', 'hence', 'because',
                   'implies', 'follows', 'consequently', 'given that',
                   'it follows', 'we can conclude', 'modus', 'ergo']
    found_connectives = [c for c in connectives if c in content_lower]
    if len(found_connectives) >= 2:
        score += 3
        details.append(f"  ✓ Found logical connectives: {', '.join(found_connectives[:5])}")
    else:
        details.append(f"  ✗ Insufficient logical connectives found")

    # Check for fallacy/assumption identification
    fallacy_terms = ['fallacy', 'assumption', 'hidden assumption', 'false dilemma',
                     'presupposes', 'presupposition', 'overlooked', 'binary thinking',
                     'false dichotomy', 'excluded middle', 'begs the question',
                     'implicit assumption', 'unstated premise']
    found_fallacy = any(t in content_lower for t in fallacy_terms)
    if found_fallacy:
        score += 2
        details.append("  ✓ Identifies a fallacy or hidden assumption")
    else:
        details.append("  ✗ No explicit fallacy/assumption identification found")

    return min(score, 8), details


def grade_recipe(content):
    """Grade Format 3: Recipe (8 pts)."""
    score = 0
    details = []
    content_lower = content.lower()

    # Check for ingredients list (≥5 items)
    # Look for bullet points or lines with common ingredient patterns
    ingredient_section = False
    ingredients = 0
    for line in content.split('\n'):
        line_lower = line.lower().strip()
        if 'ingredient' in line_lower:
            ingredient_section = True
            continue
        if ingredient_section and (line.strip().startswith('-') or line.strip().startswith('*') or
                                    re.match(r'^\d', line.strip())):
            ingredients += 1
        if ingredient_section and ('instruction' in line_lower or 'step' in line_lower or
                                    'direction' in line_lower or 'method' in line_lower):
            ingredient_section = False

    if ingredients >= 5:
        score += 3
        details.append(f"  ✓ Found {ingredients} ingredients (need ≥5)")
    else:
        details.append(f"  ✗ Found {ingredients} ingredients (need ≥5)")

    # Check for numbered steps (≥5)
    steps = len(re.findall(r'(?:step\s+)?\d+[\.\)]\s+\w', content, re.IGNORECASE))
    # Also count bullet points in instruction sections
    if steps < 5:
        instruction_section = False
        step_count = 0
        for line in content.split('\n'):
            line_lower = line.lower().strip()
            if any(w in line_lower for w in ['instruction', 'step', 'direction', 'method', 'procedure']):
                instruction_section = True
                continue
            if instruction_section and (line.strip().startswith('-') or re.match(r'^\d', line.strip())):
                step_count += 1
        steps = max(steps, step_count)

    if steps >= 5:
        score += 3
        details.append(f"  ✓ Found {steps} instruction steps (need ≥5)")
    else:
        details.append(f"  ✗ Found {steps} instruction steps (need ≥5)")

    # Check for title + yield
    has_title = bool(re.search(r'(?:^|\n)#', content)) or bool(re.search(r'(?:^|\n)\*\*', content))
    has_yield = any(w in content_lower for w in ['yield', 'serves', 'serving', 'makes', 'portions'])
    if has_title and has_yield:
        score += 2
        details.append("  ✓ Has title and yield/serving info")
    elif has_title:
        score += 1
        details.append("  ~ Has title but no yield/serving info")
    else:
        details.append("  ✗ Missing title and/or yield info")

    return min(score, 8), details


def grade_legal_brief(content):
    """Grade Format 4: Legal Brief (8 pts)."""
    score = 0
    details = []
    content_lower = content.lower()

    # Check for case header
    header_terms = ['v.', 'vs.', 'versus', 'in the matter of', 'case no',
                    'court of', 'plaintiff', 'defendant', 'petitioner', 'respondent']
    has_header = any(t in content_lower for t in header_terms)
    if has_header:
        score += 2
        details.append("  ✓ Has case header")
    else:
        details.append("  ✗ No case header found")

    # Check for Statement of Facts
    has_facts = 'statement of fact' in content_lower or 'facts of the case' in content_lower or \
                'factual background' in content_lower or 'background' in content_lower
    if has_facts:
        score += 2
        details.append("  ✓ Has Statement of Facts section")
    else:
        details.append("  ✗ No Statement of Facts section found")

    # Check for cited precedents (≥2)
    # Look for patterns like "Name v. Name" or "Case (Year)"
    precedent_pattern = r'[A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+'
    precedents = re.findall(precedent_pattern, content)
    # Also check for italicized case names or parenthetical citations
    paren_cites = re.findall(r'\(\d{4}\)', content)
    total_precedents = max(len(set(precedents)), len(paren_cites) // 2)
    if len(set(precedents)) >= 2:
        score += 2
        details.append(f"  ✓ Found {len(set(precedents))} cited precedents: {', '.join(set(precedents))[:80]}")
    elif total_precedents >= 2:
        score += 2
        details.append(f"  ✓ Found {total_precedents} apparent precedent citations")
    else:
        details.append(f"  ✗ Found {len(set(precedents))} precedents (need ≥2)")

    # Check for conclusion
    has_conclusion = 'conclusion' in content_lower or 'wherefore' in content_lower or \
                     'relief requested' in content_lower or 'prayer for relief' in content_lower
    if has_conclusion:
        score += 2
        details.append("  ✓ Has conclusion")
    else:
        details.append("  ✗ No conclusion section found")

    return min(score, 8), details


def grade_children_story(content):
    """Grade Format 5: Children's Bedtime Story (8 pts)."""
    score = 0
    details = []
    content_lower = content.lower()

    # Word count 150-250
    wc = count_words(content)
    if 150 <= wc <= 250:
        score += 3
        details.append(f"  ✓ Word count: {wc} (within 150-250 range)")
    elif 100 <= wc <= 300:
        score += 1
        details.append(f"  ~ Word count: {wc} (close to 150-250 range)")
    else:
        details.append(f"  ✗ Word count: {wc} (outside 150-250 range)")

    # Contains a moral/lesson
    moral_terms = ['moral', 'lesson', 'learned', 'remember', 'important thing',
                   'and that is why', 'from that day', 'always remember',
                   'never forget', 'the lesson']
    has_moral = any(t in content_lower for t in moral_terms)
    if has_moral:
        score += 3
        details.append("  ✓ Contains a moral or lesson")
    else:
        details.append("  ✗ No clear moral/lesson detected")

    # Contains a character name (capitalized proper noun that's not a section header)
    # Look for names that appear multiple times
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', content)
    # Filter out common non-name words
    non_names = {'The', 'She', 'Her', 'His', 'And', 'But', 'Once', 'One', 'When',
                 'Then', 'There', 'This', 'That', 'What', 'Who', 'How', 'Very',
                 'Little', 'Big', 'Old', 'New', 'Good', 'Bad', 'Format', 'Story',
                 'Children', 'Bedtime'}
    potential_names = [w for w in words if w not in non_names]
    if potential_names:
        score += 2
        # Find most common name
        from collections import Counter
        name_counts = Counter(potential_names)
        most_common = name_counts.most_common(1)[0][0]
        details.append(f"  ✓ Contains character name(s): {most_common}")
    else:
        details.append("  ✗ No character name detected")

    return min(score, 8), details


def main():
    if len(sys.argv) < 2:
        print("Usage: python grade.py <agent_name>")
        sys.exit(1)

    agent_name = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    submission_path = os.path.join(base_dir, "submissions", agent_name, "submission.md")

    if not os.path.exists(submission_path):
        print(f"ERROR: submission.md not found at {submission_path}")
        sys.exit(1)

    with open(submission_path, "r") as f:
        text = f.read()

    print("=" * 70)
    print("THE FORMAT SHIFTER — GRADING REPORT")
    print(f"Agent: {agent_name}")
    print("=" * 70)
    print()

    sections = extract_sections(text)

    if len(sections) < 5:
        print(f"WARNING: Found {len(sections)}/5 format sections")
        missing = [i for i in range(1, 6) if i not in sections]
        print(f"Missing formats: {missing}")
        print()

    total_auto = 0

    # Grade each format
    graders = {
        1: ("Haiku Sequence", grade_haiku),
        2: ("Formal Logical Argument", grade_logical_argument),
        3: ("Recipe", grade_recipe),
        4: ("Legal Brief", grade_legal_brief),
        5: ("Children's Bedtime Story", grade_children_story),
    }

    for fmt_num, (fmt_name, grader_fn) in graders.items():
        content = sections.get(fmt_num, "")
        if not content:
            print(f"--- Format {fmt_num}: {fmt_name} (8 pts) ---")
            print(f"  ✗ Section not found — 0 points")
            print()
            continue

        fmt_score, fmt_details = grader_fn(content)
        total_auto += fmt_score
        print(f"--- Format {fmt_num}: {fmt_name} ({fmt_score}/8 pts) ---")
        for detail in fmt_details:
            print(detail)
        print()

    print("=" * 70)
    print("SCORING SUMMARY")
    print("=" * 70)
    print(f"  Format Adherence (automated):  {total_auto}/40")
    print()
    print("  --- Manual Scoring (60 pts) ---")
    print("  Content Preservation:          ___/25")
    print("  Creative Adaptation:           ___/20")
    print("  Writing Quality:               ___/15")
    print()
    print(f"  AUTOMATED SCORE: {total_auto}/40")
    print(f"  (+ up to 60 points from manual grading)")
    print()
    print("Note: The challenge setter (Claude Opus 4.6) grades the 60-pt manual portion.")


if __name__ == "__main__":
    main()
