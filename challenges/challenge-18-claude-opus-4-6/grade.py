#!/usr/bin/env python3
"""
C18: The Constraint Cascade — Automated Grader
Challenge Designer: Claude Opus 4.6

Grades a 10-sentence essay on "Why curiosity matters more than certainty"
where each sentence adds one cumulative constraint.

Usage: python3 grade.py <submission.txt>
"""

import sys
import re
import string

# ─── Color words (case-insensitive match as standalone words) ───
COLOR_WORDS = {
    "red", "blue", "green", "gold", "silver", "white", "black", "gray",
    "violet", "crimson", "indigo", "amber", "coral", "ivory", "rust",
    "scarlet", "teal", "plum", "bronze", "maroon", "navy", "olive",
    "peach", "tan", "turquoise"
}


def words_rhyme(word1, word2):
    """Check if two words approximately rhyme.
    
    Generous: the spec says "approximate rhyme accepted — same ending sound."
    We check last 2+ characters match, plus common phonetic patterns.
    """
    w1 = word1.lower().rstrip(string.punctuation)
    w2 = word2.lower().rstrip(string.punctuation)
    
    if w1 == w2:
        return True
    if not w1 or not w2:
        return False
    
    # Check if last 2 characters match (covers most rhymes)
    if len(w1) >= 2 and len(w2) >= 2 and w1[-2:] == w2[-2:]:
        return True
    
    # Check if last 3 characters match
    if len(w1) >= 3 and len(w2) >= 3 and w1[-3:] == w2[-3:]:
        return True
    
    # Additional phonetic rhyme groups
    rhyme_groups = [
        # -ight / -ite / -yte
        lambda w: w.endswith(("ight", "ite", "yte")),
        # -ay / -ey / -eigh
        lambda w: w.endswith(("ay", "ey", "eigh")),
        # -ow / -ough (as in know/though)
        lambda w: w.endswith(("ow", "ough")),
        # -ine / -ign / -yn
        lambda w: w.endswith(("ine", "ign", "yn")),
        # -tion / -sion
        lambda w: w.endswith(("tion", "sion")),
        # -ound / -owned
        lambda w: w.endswith(("ound", "owned")),
        # -air / -are / -ear
        lambda w: w.endswith(("air", "are", "ear")),
    ]
    
    for matcher in rhyme_groups:
        if matcher(w1) and matcher(w2):
            return True
    
    # Short-word vowel ending match (e.g., sky/fly, go/know)
    if len(w1) >= 2 and len(w2) >= 2:
        if w1[-1] == w2[-1] and w1[-1] in 'aeiouy':
            if len(w1) <= 4 and len(w2) <= 4:
                return True
    
    return False


def get_words(sentence):
    """Split sentence into words. Punctuation is stripped from token edges."""
    tokens = sentence.split()
    words = []
    for token in tokens:
        cleaned = token.strip(string.punctuation)
        if cleaned:
            words.append(cleaned)
        else:
            # Token is purely punctuation — check for digits
            digit_part = ''.join(c for c in token if c.isdigit())
            if digit_part:
                words.append(digit_part)
    return words


def count_words(sentence):
    """Count words in a sentence."""
    return len(get_words(sentence))


def check_word_count_12(sentence):
    wc = count_words(sentence)
    return wc == 12, f"Word count: {wc} (need exactly 12)"


def check_word_count_le10(sentence):
    wc = count_words(sentence)
    return wc <= 10, f"Word count: {wc} (need ≤ 10)"


def check_word_count_5(sentence):
    wc = count_words(sentence)
    return wc == 5, f"Word count: {wc} (need exactly 5)"


def check_is_question(sentence):
    stripped = sentence.rstrip()
    is_q = stripped.endswith("?")
    return is_q, f"Ends with '?': {is_q}"


def check_no_letter_e(sentence):
    words = get_words(sentence)
    offending = [w for w in words if 'e' in w.lower()]
    if offending:
        return False, f"Words containing 'e': {offending}"
    return True, "No words contain 'e'"


def check_color_word(sentence):
    words = get_words(sentence)
    found = [w for w in words if w.lower() in COLOR_WORDS]
    if found:
        return True, f"Color word(s) found: {found}"
    return False, "No color word found"


def check_starts_with_c(sentence):
    words = get_words(sentence)
    if not words:
        return False, "Empty sentence"
    starts = words[0][0].lower() == 'c' if words[0] else False
    return starts, f"First word '{words[0]}' starts with '{'C' if starts else words[0][0]}'"


def check_contains_digit(sentence):
    has_digit = any(c.isdigit() for c in sentence)
    return has_digit, f"Contains digit: {has_digit}"


def check_rhymes_with(sentence, other_sentence):
    words1 = get_words(sentence)
    words2 = get_words(other_sentence)
    if not words1 or not words2:
        return False, "Cannot check rhyme — empty sentence"
    last1 = words1[-1].lower().rstrip(string.punctuation)
    last2 = words2[-1].lower().rstrip(string.punctuation)
    rhymes = words_rhyme(last1, last2)
    return rhymes, f"Last words: '{last1}' / '{last2}' — {'rhyme ✓' if rhymes else 'do NOT rhyme ✗'}"


def grade_submission(filepath):
    """Grade a C18 submission file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return 0
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        return 0
    
    lines = content.strip().split('\n')
    sentences = [line.strip() for line in lines if line.strip()]
    
    if len(sentences) != 10:
        print(f"ERROR: Expected exactly 10 sentences, found {len(sentences)}")
        print(f"(Got {len(lines)} lines total, {len(sentences)} non-empty)")
        return 0
    
    total_score = 0
    POINTS_PER_SENTENCE = 7
    
    print("=" * 70)
    print("C18: THE CONSTRAINT CASCADE — AUTOMATED GRADING")
    print("=" * 70)
    print()
    
    for i, sentence in enumerate(sentences):
        sent_num = i + 1
        print(f"--- Sentence {sent_num} ---")
        print(f"  Text: \"{sentence}\"")
        
        checks = []
        
        # Word count constraint
        if sent_num >= 10:
            checks.append(("Exactly 5 words", *check_word_count_5(sentence)))
        elif sent_num >= 6:
            checks.append(("≤ 10 words", *check_word_count_le10(sentence)))
        elif sent_num >= 2:
            checks.append(("Exactly 12 words", *check_word_count_12(sentence)))
        
        # Question constraint (S3+)
        if sent_num >= 3:
            checks.append(("Is a question", *check_is_question(sentence)))
        
        # No letter 'e' (S4+)
        if sent_num >= 4:
            checks.append(("No letter 'e'", *check_no_letter_e(sentence)))
        
        # Color word (S5+)
        if sent_num >= 5:
            checks.append(("Contains color word", *check_color_word(sentence)))
        
        # Starts with C (S7+)
        if sent_num >= 7:
            checks.append(("Starts with 'C'", *check_starts_with_c(sentence)))
        
        # Contains digit (S8+)
        if sent_num >= 8:
            checks.append(("Contains digit", *check_contains_digit(sentence)))
        
        # Rhymes with S8 (S9+)
        if sent_num >= 9:
            checks.append(("Rhymes with S8", *check_rhymes_with(sentence, sentences[7])))
        
        # Report results
        if not checks:
            print("  [No constraints — FREE]")
            checks_pass = True
        else:
            checks_pass = True
            for constraint_name, passed, msg in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {status} | {constraint_name}: {msg}")
                if not passed:
                    checks_pass = False
        
        if checks_pass:
            total_score += POINTS_PER_SENTENCE
            print(f"  → +{POINTS_PER_SENTENCE} pts")
        else:
            print(f"  → +0 pts (constraint violation)")
        print()
    
    print("=" * 70)
    print(f"AUTOMATED SCORE: {total_score} / 70")
    print("=" * 70)
    print()
    print("Manual grading (30 pts) will be assessed separately:")
    print("  - Coherence (15 pts)")
    print("  - Insight (10 pts)")
    print("  - Elegance (5 pts)")
    
    return total_score


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <submission.txt>")
        sys.exit(1)
    
    score = grade_submission(sys.argv[1])
    sys.exit(0 if score > 0 else 1)
