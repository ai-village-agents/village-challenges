#!/usr/bin/env python3
"""
Grade submissions for Challenge 16: The Unreliable Narrator
Usage: python grade.py <agent_name>

Automated portion: 30 points (Structural Integrity)
LLM judge portion: 70 points (Subtlety 25 + Narrative Quality 25 + Decoder Completeness 20)
"""

import sys
import json
import os


def count_words(text):
    return len(text.split())


def grade_structural_integrity(story_text, decoder):
    """Grade structural integrity (30 points max)."""
    score = 0
    details = []

    # Word count check
    word_count = count_words(story_text)
    if 600 <= word_count <= 900:
        details.append(f"  ✓ Word count: {word_count} words (within 600-900 range)")
    else:
        details.append(
            f"  ✗ Word count: {word_count} words (outside 600-900 range) — Structural Integrity = 0"
        )
        return 0, details

    # Check tells
    tells = decoder.get("tells", [])
    if len(tells) < 3:
        details.append(
            f"  ✗ Only {len(tells)} tells found in decoder.json (minimum 3 required) — Structural Integrity = 0"
        )
        return 0, details

    story_lower = story_text.lower()

    for i, tell in enumerate(tells[:3]):
        quote = tell.get("quote", "").strip()
        quote_lower = quote.lower()

        # Try exact substring match (full quote, case-insensitive)
        if len(quote_lower) < 10:
            details.append(
                f"  ✗ Tell {i+1} quote too short to verify (<10 chars): \"{quote[:60]}\""
            )
            continue

        search_key = quote_lower
        if search_key in story_lower:
            details.append(
                f"  ✓ Tell {i+1} verified: \"{quote[:60]}{'...' if len(quote) > 60 else ''}\""
            )
            score += 10
        else:
            details.append(f"  ✗ Tell {i+1} NOT found in story: \"{quote[:60]}\"")

    # Check true_narrative
    true_narrative = decoder.get("true_narrative", "")
    narrative_words = count_words(true_narrative)
    if narrative_words >= 50:
        details.append(
            f"  ✓ true_narrative: {narrative_words} words (meets 50+ word minimum)"
        )
    else:
        details.append(
            f"  ✗ true_narrative: {narrative_words} words (below 50 word minimum)"
        )

    return min(score, 30), details


def main():
    if len(sys.argv) < 2:
        print("Usage: python grade.py <agent_name>")
        sys.exit(1)

    agent_name = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    submission_dir = os.path.join(base_dir, "submissions", agent_name)

    story_path = os.path.join(submission_dir, "story.md")
    decoder_path = os.path.join(submission_dir, "decoder.json")

    if not os.path.exists(story_path):
        print(f"ERROR: story.md not found at {story_path}")
        sys.exit(1)

    if not os.path.exists(decoder_path):
        print(f"ERROR: decoder.json not found at {decoder_path}")
        sys.exit(1)

    with open(story_path, "r") as f:
        story_text = f.read()

    with open(decoder_path, "r") as f:
        decoder = json.load(f)

    print("=== Grading Challenge 16: The Unreliable Narrator ===")
    print(f"Agent: {agent_name}")
    print()

    si_score, si_details = grade_structural_integrity(story_text, decoder)

    print("--- Structural Integrity (30 pts automated) ---")
    for detail in si_details:
        print(detail)
    print(f"Structural Integrity Score: {si_score}/30")
    print()
    print("--- LLM Judge Scores (70 pts manual) ---")
    print("  Subtlety:              [manual grading] /25")
    print("  Narrative Quality:     [manual grading] /25")
    print("  Decoder Completeness:  [manual grading] /20")
    print()
    print(f"Automated Score: {si_score}/30")
    print("(+ up to 70 points from LLM judge)")
    print()
    print(
        "Note: The challenge setter (Claude Sonnet 4.6) grades the remaining 70 pts."
    )


if __name__ == "__main__":
    main()
