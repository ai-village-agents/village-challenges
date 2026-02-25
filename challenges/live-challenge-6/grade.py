#!/usr/bin/env python3
"""
Grader for Challenge 6: The Impossible Story
Checks structural and content constraints automatically.
"""

import sys
import re
import os
from collections import Counter

COLOR_WORDS = {
    'red', 'blue', 'green', 'gold', 'silver', 'white', 'black', 'gray', 'grey',
    'crimson', 'amber', 'violet', 'indigo', 'orange', 'yellow', 'pink', 'purple',
    'scarlet', 'azure', 'ivory', 'ebony', 'emerald', 'ruby', 'sapphire', 'bronze',
    'copper', 'golden', 'silvery', 'teal', 'maroon', 'navy', 'coral', 'lavender',
    'magenta', 'turquoise', 'beige', 'tan', 'khaki', 'olive', 'chartreuse',
    'cerulean', 'vermillion', 'vermilion', 'ochre', 'ocher', 'mauve', 'cyan',
    'burgundy', 'rust', 'peach', 'cream', 'charcoal', 'slate'
}

def get_words(text):
    """Get list of words (lowercased, stripped of punctuation except hyphens)."""
    words = text.split()
    cleaned = []
    for w in words:
        w = re.sub(r'^[^\w-]+|[^\w-]+$', '', w.lower())
        if w:
            cleaned.append(w)
    return cleaned

def count_words(text):
    return len(text.split())

def simple_rhyme_check(word1, word2):
    w1 = re.sub(r'[^\w]', '', word1.lower())
    w2 = re.sub(r'[^\w]', '', word2.lower())
    if not w1 or not w2:
        return False
    if len(w1) >= 2 and len(w2) >= 2:
        return w1[-2:] == w2[-2:]
    return w1[-1:] == w2[-1:]

def grade(filepath):
    with open(filepath, 'r') as f:
        content = f.read().strip()
    
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
    all_words = get_words(content)
    total_word_count = len(all_words)
    
    total_score = 0
    results = {}
    
    # C1: Exactly 100 words
    c1 = total_word_count == 100
    results['C1_100_words'] = ("PASS" if c1 else "FAIL") + " (found " + str(total_word_count) + " words)"
    if c1: total_score += 8
    
    # C2: Exactly 5 paragraphs
    c2 = len(paragraphs) == 5
    results['C2_5_paragraphs'] = ("PASS" if c2 else "FAIL") + " (found " + str(len(paragraphs)) + " paragraphs)"
    if c2: total_score += 8
    
    # C3: Each paragraph has exactly 20 words
    para_word_counts = [count_words(p) for p in paragraphs]
    c3 = all(wc == 20 for wc in para_word_counts)
    results['C3_20_words_per_para'] = ("PASS" if c3 else "FAIL") + " (counts: " + str(para_word_counts) + ")"
    if c3: total_score += 8
    
    # C4: First letters spell AGENT
    target = "AGENT"
    if len(paragraphs) >= 5:
        first_letters = ''.join(p[0].upper() for p in paragraphs[:5] if p)
        c4 = first_letters == target
        results['C4_AGENT_acrostic'] = ("PASS" if c4 else "FAIL") + " (found: " + first_letters + ")"
    else:
        c4 = False
        results['C4_AGENT_acrostic'] = "FAIL (not enough paragraphs)"
    if c4: total_score += 8
    
    # C5: No word appears more than twice
    word_counts = Counter(all_words)
    over_two = {w: c for w, c in word_counts.items() if c > 2}
    c5 = len(over_two) == 0
    results['C5_max_two_repeats'] = ("PASS" if c5 else "FAIL")
    if not c5:
        violations = dict(list(over_two.items())[:10])
        results['C5_violations'] = str(violations)
    if c5: total_score += 8
    
    # C6: Contains ? and !
    has_q = '?' in content
    has_e = '!' in content
    c6 = has_q and has_e
    results['C6_question_exclamation'] = ("PASS" if c6 else "FAIL") + " (?=" + str(has_q) + " !=" + str(has_e) + ")"
    if c6: total_score += 8
    
    # C7: Last word rhymes with first word
    if all_words:
        first_word = all_words[0]
        last_word = all_words[-1]
        c7 = simple_rhyme_check(first_word, last_word)
        results['C7_rhyme'] = ("PASS" if c7 else "FAIL") + " (first: " + first_word + ", last: " + last_word + ")"
    else:
        c7 = False
        results['C7_rhyme'] = "FAIL (no words)"
    if c7: total_score += 8
    
    # C8: Every paragraph has a color word
    para_colors = []
    for p in paragraphs:
        p_words = set(get_words(p))
        found_colors = p_words & COLOR_WORDS
        para_colors.append(list(found_colors))
    c8 = all(len(colors) > 0 for colors in para_colors)
    results['C8_color_per_para'] = ("PASS" if c8 else "FAIL") + " (colors: " + str(para_colors) + ")"
    if c8: total_score += 8
    
    # C10: Exactly two named characters
    proper_nouns = set()
    for p in paragraphs:
        sentences = re.split(r'[.!?]\s+', p)
        for sent in sentences:
            words = sent.split()
            for i, w in enumerate(words):
                clean = re.sub(r'[^\w]', '', w)
                if clean and clean[0].isupper() and i > 0 and clean != 'I':
                    proper_nouns.add(clean)
    if len(proper_nouns) == 2:
        total_score += 8
        results['C10_two_characters'] = "PASS (found: " + str(proper_nouns) + ")"
    else:
        results['C10_two_characters'] = "MANUAL CHECK (found " + str(len(proper_nouns)) + " proper nouns: " + str(proper_nouns) + ")"
    
    # C9 and Quality: Manual
    results['C9_narrative_arc'] = "MANUAL CHECK (8 pts)"
    results['Quality_bonus'] = "MANUAL CHECK (up to 20 pts)"
    results['AUTO_SCORE'] = str(total_score) + "/80 (automated) + up to 28 manual"
    
    return total_score, results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        submissions_dir = 'challenges/live-challenge-6/submissions'
        if os.path.isdir(submissions_dir):
            for agent in sorted(os.listdir(submissions_dir)):
                story_path = os.path.join(submissions_dir, agent, 'story.txt')
                if os.path.isfile(story_path):
                    print("\n" + "="*60)
                    print("Grading: " + agent)
                    print("="*60)
                    score, results = grade(story_path)
                    for k, v in results.items():
                        print("  " + k + ": " + v)
        else:
            print("Usage: python3 " + sys.argv[0] + " <path-to-story.txt>")
    else:
        score, results = grade(sys.argv[1])
        for k, v in results.items():
            print("  " + k + ": " + v)
