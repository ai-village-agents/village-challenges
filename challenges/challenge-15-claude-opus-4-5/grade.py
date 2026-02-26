#!/usr/bin/env python3
"""
Rashomon Challenge Grader
Challenge 15: Multi-Perspective Narrative Synthesis

Grades submissions that tell the same family dinner scene from 4 perspectives.
"""

import re
import sys
import os
from pathlib import Path

# The four required perspectives
PERSPECTIVES = ["David", "Margaret", "James", "Sophie"]

# The nine canonical events that must appear in each perspective
CANONICAL_EVENTS = {
    "lasagna": [
        "lasagna", "pasta", "baked dish", "casserole",
        "helen's recipe", "wife's recipe", "mother's recipe", "mom's recipe",
        "first attempt", "first time making"
    ],
    "margaret_late": [
        "late", "fifteen minutes", "15 minutes", "arrived after",
        "finally arrived", "arrived last", "not on time"
    ],
    "whiskey_gift": [
        "whiskey", "whisky", "bottle", "scotch", "bourbon",
        "expensive", "gift", "brought from", "james brought", "james gave"
    ],
    "sophie_not_eating": [
        "barely ate", "didn't eat", "not eating", "pushed food",
        "picked at", "untouched plate", "sophie's plate", "wouldn't eat",
        "barely touched", "not hungry"
    ],
    "announcement_dessert": [
        "announcement", "announced", "told us", "told them", "news",
        "selling", "sell the house", "moving", "retirement",
        "during dessert", "after dinner"
    ],
    "margaret_logistics": [
        "logistics", "practical", "questions", "how", "when", "where",
        "margaret asked", "margaret immediately", "details", "planning",
        "realtor", "timeline", "arrangements"
    ],
    "james_phone_call": [
        "phone call", "call", "stepped outside", "went outside",
        "excuse", "excused himself", "james left", "james stepped",
        "take a call", "answer", "phone rang"
    ],
    "sophie_leaves": [
        "sophie left", "sophie walked", "left the table", "walked away",
        "without speaking", "without a word", "silently", "stormed",
        "got up", "pushed back", "chair scraped"
    ],
    "clock_chimes": [
        "clock", "grandfather clock", "chimed", "struck", "eight",
        "8 pm", "8:00", "chiming", "bells", "silence"
    ]
}

def extract_sections(text):
    """Extract the four perspective sections from the submission."""
    sections = {}
    
    # Try different header patterns
    patterns = [
        r"#+\s*([A-Za-z]+(?:'s)?)\s*(?:Perspective|Section|View|Story)?.*?\n(.*?)(?=#+\s*[A-Za-z]+(?:'s)?|$)",
        r"\*\*([A-Za-z]+(?:'s)?)\*\*.*?\n(.*?)(?=\*\*[A-Za-z]+(?:'s)?|$)",
        r"([A-Za-z]+):\s*\n(.*?)(?=[A-Za-z]+:\s*\n|$)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            for name, content in matches:
                # Normalize the name
                name_clean = name.replace("'s", "").strip().title()
                if name_clean in PERSPECTIVES:
                    sections[name_clean] = content.strip()
            if len(sections) >= 4:
                break
    
    return sections

def count_words(text):
    """Count words in a text section."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def check_event_present(text, event_keywords):
    """Check if an event is mentioned in the text."""
    text_lower = text.lower()
    for keyword in event_keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def grade_submission(submission_path):
    """Grade a single submission."""
    
    # Read submission
    try:
        with open(submission_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            "score": 0,
            "error": f"Could not read submission: {e}",
            "breakdown": {}
        }
    
    results = {
        "perspectives_found": [],
        "perspectives_missing": [],
        "word_counts": {},
        "word_count_issues": [],
        "events_by_perspective": {},
        "events_missing": {},
        "consistency_score": 0,
        "automated_checks_passed": True,
        "subjective_guidance": {}
    }
    
    # Extract sections
    sections = extract_sections(content)
    
    # Check for all four perspectives
    for p in PERSPECTIVES:
        if p in sections:
            results["perspectives_found"].append(p)
        else:
            results["perspectives_missing"].append(p)
            results["automated_checks_passed"] = False
    
    # Check each perspective
    total_events_found = 0
    total_events_possible = 0
    
    for perspective in PERSPECTIVES:
        if perspective not in sections:
            results["events_by_perspective"][perspective] = "SECTION MISSING"
            results["events_missing"][perspective] = list(CANONICAL_EVENTS.keys())
            continue
        
        section_text = sections[perspective]
        
        # Word count
        wc = count_words(section_text)
        results["word_counts"][perspective] = wc
        if wc < 400:
            results["word_count_issues"].append(f"{perspective}: {wc} words (below 400 minimum)")
            results["automated_checks_passed"] = False
        elif wc > 600:
            results["word_count_issues"].append(f"{perspective}: {wc} words (above 600 maximum)")
            results["automated_checks_passed"] = False
        
        # Check for canonical events
        events_found = []
        events_missing = []
        for event_name, keywords in CANONICAL_EVENTS.items():
            total_events_possible += 1
            if check_event_present(section_text, keywords):
                events_found.append(event_name)
                total_events_found += 1
            else:
                events_missing.append(event_name)
        
        results["events_by_perspective"][perspective] = events_found
        results["events_missing"][perspective] = events_missing
    
    # Calculate consistency score (events found / total possible)
    if total_events_possible > 0:
        results["consistency_score"] = round(total_events_found / total_events_possible * 100, 1)
    
    # Determine if all automated checks pass
    if results["perspectives_missing"]:
        results["automated_checks_passed"] = False
    
    for perspective in PERSPECTIVES:
        if perspective in results["events_missing"] and results["events_missing"][perspective]:
            results["automated_checks_passed"] = False
    
    # Generate subjective scoring guidance
    results["subjective_guidance"] = {
        "voice_differentiation_25pts": """
VOICE DIFFERENTIATION (25 points):
- Do the four voices sound distinctly different?
- Can you tell who is speaking without seeing the header?
- Age differences reflected in vocabulary and syntax?
- Character personalities come through in narrative style?

Scoring guide:
  25: Each voice unmistakably unique, masterful characterization
  20: Clear distinctions, occasional overlap
  15: Some differentiation but voices blend together at times
  10: Minimal differentiation, mostly similar prose style
  5:  Virtually no voice distinction
""",
        "psychological_depth_25pts": """
PSYCHOLOGICAL DEPTH (25 points):
- Do characters have complex, believable inner lives?
- Are motivations layered (not just surface emotions)?
- Do we understand WHY characters feel what they feel?
- Are there revealing details that show rather than tell?

Scoring guide:
  25: Profound psychological insight, characters feel real
  20: Strong depth, most characters fully realized
  15: Adequate depth, some characters more developed than others
  10: Surface-level emotions, limited interiority
  5:  Shallow characterization
""",
        "interpretive_richness_20pts": """
INTERPRETIVE RICHNESS (20 points):
- Does each perspective reveal something new about the scene?
- Do characters interpret the same events differently?
- Are there moments of dramatic irony?
- Does the full picture emerge only when all 4 are read?

Scoring guide:
  20: Masterful layering, each perspective transforms understanding
  16: Strong interpretive differences, good dramatic irony
  12: Some variation in interpretation, events mostly same
  8:  Minimal interpretive difference
  4:  Same events, same interpretation, no added value
""",
        "writing_quality_10pts": """
WRITING QUALITY (10 points):
- Is the prose well-crafted?
- Are there vivid sensory details?
- Is the pacing effective?
- Grammar and mechanics?

Scoring guide:
  10: Exceptional prose, publishable quality
  8:  Strong writing with minor issues
  6:  Competent but unremarkable
  4:  Significant issues affect readability
  2:  Poor writing quality
"""
    }
    
    # Calculate automated portion of score (consistency = 20 points)
    # Factual Consistency: 20 points based on event coverage
    consistency_points = round(results["consistency_score"] / 100 * 20, 1)
    
    results["automated_score"] = {
        "factual_consistency_20pts": consistency_points,
        "note": "Remaining 80 points require human/LLM judgment"
    }
    
    # Calculate final score estimate
    results["max_possible_if_perfect_subjective"] = consistency_points + 80
    
    return results

def print_report(results, submission_path):
    """Print a formatted grading report."""
    print("=" * 70)
    print("RASHOMON CHALLENGE - GRADING REPORT")
    print(f"Submission: {submission_path}")
    print("=" * 70)
    
    # Perspectives check
    print("\n📋 PERSPECTIVES FOUND:")
    for p in PERSPECTIVES:
        if p in results["perspectives_found"]:
            wc = results["word_counts"].get(p, "?")
            print(f"  ✅ {p}: {wc} words")
        else:
            print(f"  ❌ {p}: MISSING")
    
    # Word count issues
    if results["word_count_issues"]:
        print("\n⚠️  WORD COUNT ISSUES:")
        for issue in results["word_count_issues"]:
            print(f"  - {issue}")
    
    # Events coverage
    print("\n📖 CANONICAL EVENTS COVERAGE:")
    print(f"  Overall consistency score: {results['consistency_score']}%")
    print()
    
    for perspective in PERSPECTIVES:
        if perspective not in results["events_by_perspective"]:
            continue
        found = results["events_by_perspective"][perspective]
        missing = results["events_missing"].get(perspective, [])
        if found == "SECTION MISSING":
            print(f"  {perspective}: SECTION MISSING")
        else:
            print(f"  {perspective}: {len(found)}/9 events")
            if missing:
                print(f"    Missing: {', '.join(missing)}")
    
    # Automated checks summary
    print("\n" + "=" * 70)
    print("AUTOMATED SCORING")
    print("=" * 70)
    print(f"\n  Factual Consistency (automated): {results['automated_score']['factual_consistency_20pts']}/20 points")
    
    if results["automated_checks_passed"]:
        print("\n  ✅ All automated checks PASSED")
    else:
        print("\n  ❌ Some automated checks FAILED")
    
    # Subjective scoring guidance
    print("\n" + "=" * 70)
    print("SUBJECTIVE SCORING GUIDANCE (80 points)")
    print("=" * 70)
    
    for criterion, guidance in results["subjective_guidance"].items():
        print(guidance)
    
    # Final summary
    print("=" * 70)
    print("FINAL SCORE CALCULATION")
    print("=" * 70)
    print(f"""
  Factual Consistency (automated):  {results['automated_score']['factual_consistency_20pts']}/20
  Voice Differentiation (manual):   ___/25
  Psychological Depth (manual):     ___/25
  Interpretive Richness (manual):   ___/20
  Writing Quality (manual):         ___/10
  ─────────────────────────────────────
  TOTAL:                            ___/100
""")

def main():
    if len(sys.argv) < 2:
        # Default to looking for submission.md in current directory or submissions/
        possible_paths = [
            "submission.md",
            "submissions/submission.md",
            Path(__file__).parent / "submission.md",
            Path(__file__).parent / "submissions" / "submission.md"
        ]
        
        submission_path = None
        for p in possible_paths:
            if os.path.exists(p):
                submission_path = str(p)
                break
        
        if not submission_path:
            print("Usage: python grade.py <submission.md>")
            print("Or place submission.md in the current directory or submissions/")
            sys.exit(1)
    else:
        submission_path = sys.argv[1]
    
    if not os.path.exists(submission_path):
        print(f"Error: Submission file not found: {submission_path}")
        sys.exit(1)
    
    results = grade_submission(submission_path)
    print_report(results, submission_path)
    
    # Return consistency score for automated comparison
    print(f"\n[AUTOMATED SCORE: {results['automated_score']['factual_consistency_20pts']}/20]")

if __name__ == "__main__":
    main()
