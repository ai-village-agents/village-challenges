#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys

WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
COLOR_WORDS = {
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "indigo",
    "violet",
    "white",
    "black",
    "grey",
    "gray",
    "brown",
    "pink",
    "purple",
    "gold",
    "silver",
    "cyan",
    "magenta",
    "beige",
    "turquoise",
    "teal",
    "maroon",
}


def get_words(text: str) -> list[str]:
    """Extract word-like tokens (letters and apostrophes)."""
    return WORD_PATTERN.findall(text)


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def rhyme_match(first: str, last: str) -> bool:
    """Simple rhyme heuristic: matching 3-letter or 2-letter suffix."""
    def clean(word: str) -> str:
        return re.sub(r"[^A-Za-z]", "", word.lower())

    f = clean(first)
    l = clean(last)
    if not f or not l:
        return False
    for n in (3, 2):
        if len(f) >= n and len(l) >= n and f[-n:] == l[-n:]:
            return True
    return False


def count_proper_nouns(text: str) -> int:
    """Count capitalized words not at the start of a sentence."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    count = 0
    for sentence in sentences:
        words = get_words(sentence)
        if not words:
            continue
        for word in words[1:]:
            if word == "I":
                continue
            if word[0].isupper():
                count += 1
    return count


def print_result(title: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status}: {title} - {detail}")


def main() -> int:
    story_path = Path(__file__).parent / "story.txt"
    if not story_path.exists():
        print("Story file missing:", story_path)
        return 1

    text = story_path.read_text(encoding="utf-8")
    paragraphs = split_paragraphs(text)
    words = get_words(text)

    # Constraint 1: Exactly 100 words total.
    total_words = len(words)
    print_result("100 words total", total_words == 100, f"found {total_words}")

    # Constraint 2: Exactly 5 paragraphs.
    para_count = len(paragraphs)
    print_result("5 paragraphs", para_count == 5, f"found {para_count}")

    # Constraint 3: Each paragraph has exactly 20 words.
    para_lengths = [len(get_words(p)) for p in paragraphs]
    per_para_ok = para_count == 5 and all(length == 20 for length in para_lengths)
    print_result(
        "20 words per paragraph",
        per_para_ok,
        f"lengths {para_lengths if para_lengths else 'n/a'}",
    )

    # Constraint 4: First letters spell AGENT.
    initials = "".join(get_words(p)[0][0].upper() for p in paragraphs if get_words(p))
    print_result("Initials spell AGENT", initials == "AGENT", f"got '{initials}'")

    # Constraint 5: No word appears more than twice (case-insensitive).
    counts = Counter(w.lower() for w in words)
    overused = {w: c for w, c in counts.items() if c > 2}
    print_result("No word overused (>2)", not overused, f"overused {overused}")

    # Constraint 6: Contains at least one '?' and one '!'.
    has_question = "?" in text
    has_exclaim = "!" in text
    punctuation_ok = has_question and has_exclaim
    print_result(
        "Contains '?' and '!'",
        punctuation_ok,
        f"question={has_question}, exclamation={has_exclaim}",
    )

    # Constraint 7: Last word rhymes with the first word.
    first_word = words[0] if words else ""
    last_word = words[-1] if words else ""
    rhyme_ok = rhyme_match(first_word, last_word)
    rhyme_detail = f"first='{first_word}', last='{last_word}'"
    print_result("Rhyme first/last", rhyme_ok, rhyme_detail)

    # Constraint 8: Each paragraph contains a color word.
    def has_color(paragraph: str) -> bool:
        return any(word.lower() in COLOR_WORDS for word in get_words(paragraph))

    colors_present = [has_color(p) for p in paragraphs]
    colors_ok = para_count == 5 and all(colors_present)
    print_result("Color word in each paragraph", colors_ok, f"flags {colors_present}")

    # Constraint 9: Print count of proper nouns (for 2 named characters).
    proper_noun_count = count_proper_nouns(text)
    print(f"Proper noun count (not sentence starts): {proper_noun_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
