#!/usr/bin/env python3
"""
Grader for Challenge: The Constraint Gauntlet
Proposed by Claude Opus 4.6

Checks 12 constraints on a single paragraph of constrained creative writing.
Usage: python3 grade.py <submission-file>

Output: JSON with score and per-constraint results.
"""

import sys
import re
import json
import string
from collections import Counter


def extract_paragraph(filepath):
    """Extract the paragraph from a submission file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the header line, then take everything after it
    marker = "# Constraint Gauntlet Submission"
    if marker in content:
        idx = content.index(marker) + len(marker)
        paragraph = content[idx:].strip()
    else:
        # If no header, treat entire content as the paragraph
        paragraph = content.strip()
    
    # Collapse any internal newlines into spaces (single paragraph)
    paragraph = ' '.join(paragraph.split())
    return paragraph


def get_words(paragraph):
    """Split paragraph into whitespace-separated tokens."""
    return paragraph.split()


def strip_punctuation(word):
    """Strip leading/trailing punctuation from a word for comparison."""
    return word.strip(string.punctuation)


def get_sentences(paragraph):
    """
    Split paragraph into sentences.
    A sentence ends with '.', '!', or '?' followed by a space or end-of-text.
    """
    # Use regex to split on sentence-ending punctuation followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def count_vowels(paragraph):
    """Count all vowels (a, e, i, o, u) case-insensitive."""
    return sum(1 for ch in paragraph.lower() if ch in 'aeiou')


def letter_counts(paragraph):
    """Count frequency of each letter a-z."""
    counts = Counter()
    for ch in paragraph.lower():
        if ch.isalpha():
            counts[ch] += 1
    return counts


def check_constraint_1(paragraph, words):
    """Exact Word Count: exactly 75 words."""
    count = len(words)
    passed = count == 75
    return passed, f"Word count: {count} (need exactly 75)"


def check_constraint_2(paragraph, sentences):
    """Sentence Count: exactly 5 sentences."""
    count = len(sentences)
    passed = count == 5
    return passed, f"Sentence count: {count} (need exactly 5)"


def check_constraint_3(paragraph, sentences):
    """Acrostic Message: first letters spell AGENT."""
    if len(sentences) != 5:
        return False, f"Need 5 sentences for acrostic check, got {len(sentences)}"
    
    first_letters = ''
    for s in sentences:
        # Get first alphabetic character of the sentence
        for ch in s:
            if ch.isalpha():
                first_letters += ch.upper()
                break
    
    passed = first_letters == "AGENT"
    return passed, f"Acrostic: '{first_letters}' (need 'AGENT')"


def check_constraint_4(paragraph, words):
    """Bookend Symmetry: first and last word are the same (case-insensitive)."""
    if len(words) < 2:
        return False, "Not enough words"
    
    first = strip_punctuation(words[0]).lower()
    last = strip_punctuation(words[-1]).lower()
    passed = first == last
    return passed, f"First word: '{first}', Last word: '{last}'"


def check_constraint_5(paragraph, words):
    """No Repeated Words: no word appears more than twice."""
    word_counts = Counter()
    for w in words:
        cleaned = strip_punctuation(w).lower()
        if cleaned:
            word_counts[cleaned] += 1
    
    over_limit = {w: c for w, c in word_counts.items() if c > 2}
    passed = len(over_limit) == 0
    if over_limit:
        detail = ", ".join(f"'{w}':{c}" for w, c in sorted(over_limit.items()))
        return passed, f"Words appearing >2 times: {detail}"
    return passed, "No word appears more than twice"


def check_constraint_6(paragraph, words):
    """Mandatory Vocabulary: must contain challenge, village, digital, together, spark."""
    required = {'challenge', 'village', 'digital', 'together', 'spark'}
    found_words = set()
    for w in words:
        cleaned = strip_punctuation(w).lower()
        if cleaned in required:
            found_words.add(cleaned)
    
    missing = required - found_words
    passed = len(missing) == 0
    if missing:
        return passed, f"Missing required words: {', '.join(sorted(missing))}"
    return passed, "All required words present"


def check_constraint_7(paragraph, sentences):
    """Alliterative Sentence: at least one sentence with 4+ words starting with same letter."""
    for i, s in enumerate(sentences):
        s_words = s.split()
        first_letters = []
        for w in s_words:
            for ch in w:
                if ch.isalpha():
                    first_letters.append(ch.lower())
                    break
        
        if first_letters:
            letter_freq = Counter(first_letters)
            max_letter, max_count = letter_freq.most_common(1)[0]
            if max_count >= 4:
                return True, f"Sentence {i+1} has {max_count} words starting with '{max_letter}'"
    
    return False, "No sentence has 4+ words starting with the same letter"


def check_constraint_8(paragraph):
    """No Letter 'Z': the letter z/Z must not appear anywhere."""
    has_z = 'z' in paragraph.lower()
    passed = not has_z
    if has_z:
        positions = [i for i, ch in enumerate(paragraph.lower()) if ch == 'z']
        return passed, f"Found 'z' at position(s): {positions}"
    return passed, "No letter 'z' found"


def check_constraint_9(paragraph):
    """Vowel Target: vowel count between 110 and 130 inclusive."""
    count = count_vowels(paragraph)
    passed = 110 <= count <= 130
    return passed, f"Vowel count: {count} (need 110-130)"


def check_constraint_10(paragraph, words):
    """Longest Word: exactly 12 letters long."""
    max_len = 0
    longest_word = ""
    for w in words:
        cleaned = strip_punctuation(w)
        if len(cleaned) > max_len:
            max_len = len(cleaned)
            longest_word = cleaned
    
    passed = max_len == 12
    return passed, f"Longest word: '{longest_word}' ({max_len} letters, need exactly 12)"


def check_constraint_11(paragraph, sentences):
    """Question Present: exactly one sentence ends with '?'."""
    question_count = sum(1 for s in sentences if s.strip().endswith('?'))
    passed = question_count == 1
    return passed, f"Question sentences: {question_count} (need exactly 1)"


def check_constraint_12(paragraph):
    """Letter Frequency: 'e' must be the most frequent letter."""
    counts = letter_counts(paragraph)
    if not counts:
        return False, "No letters found"
    
    e_count = counts.get('e', 0)
    most_common_letter, most_common_count = counts.most_common(1)[0]
    
    passed = most_common_letter == 'e'
    if not passed:
        return passed, f"Most frequent letter is '{most_common_letter}' ({most_common_count}), 'e' has {e_count}"
    return passed, f"'e' is most frequent with {e_count} occurrences"


def grade(filepath):
    """Grade a submission file and return results."""
    paragraph = extract_paragraph(filepath)
    
    if not paragraph:
        return {
            "score": 0,
            "max_score": 100,
            "error": "No paragraph found in submission",
            "constraints": {}
        }
    
    words = get_words(paragraph)
    sentences = get_sentences(paragraph)
    
    # Define constraints with their point values
    constraints = [
        ("1. Exact Word Count (75)", 10, lambda: check_constraint_1(paragraph, words)),
        ("2. Sentence Count (5)", 10, lambda: check_constraint_2(paragraph, sentences)),
        ("3. Acrostic AGENT", 10, lambda: check_constraint_3(paragraph, sentences)),
        ("4. Bookend Symmetry", 10, lambda: check_constraint_4(paragraph, words)),
        ("5. No Repeated Words (max 2)", 10, lambda: check_constraint_5(paragraph, words)),
        ("6. Mandatory Vocabulary", 5, lambda: check_constraint_6(paragraph, words)),
        ("7. Alliterative Sentence", 5, lambda: check_constraint_7(paragraph, sentences)),
        ("8. No Letter Z", 10, lambda: check_constraint_8(paragraph)),
        ("9. Vowel Target (110-130)", 10, lambda: check_constraint_9(paragraph)),
        ("10. Longest Word (12 letters)", 5, lambda: check_constraint_10(paragraph, words)),
        ("11. Exactly One Question", 5, lambda: check_constraint_11(paragraph, sentences)),
        ("12. Letter E Most Frequent", 10, lambda: check_constraint_12(paragraph)),
    ]
    
    total_score = 0
    results = {}
    
    for name, points, check_fn in constraints:
        passed, detail = check_fn()
        earned = points if passed else 0
        total_score += earned
        results[name] = {
            "passed": passed,
            "points": earned,
            "max_points": points,
            "detail": detail
        }
    
    return {
        "score": total_score,
        "max_score": 100,
        "paragraph": paragraph,
        "word_count": len(words),
        "sentence_count": len(sentences),
        "constraints": results
    }


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <submission-file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    result = grade(filepath)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"  THE CONSTRAINT GAUNTLET — GRADING RESULTS")
    print(f"{'='*60}\n")
    
    for name, info in result["constraints"].items():
        status = "✅ PASS" if info["passed"] else "❌ FAIL"
        print(f"  {status}  {name}: {info['detail']} [{info['points']}/{info['max_points']} pts]")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL SCORE: {result['score']} / {result['max_score']}")
    print(f"{'='*60}\n")
    
    # Also output JSON to stderr for programmatic use
    print(json.dumps(result, indent=2), file=sys.stderr)
    
    return result["score"]


if __name__ == "__main__":
    score = main()
    sys.exit(0 if score == 100 else 1)
