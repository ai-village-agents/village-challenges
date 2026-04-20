#!/usr/bin/env python3
"""
Automated grading script for Challenge 19: The Paradox Resolver
"""

import re
import sys
from pathlib import Path

def count_words(text):
    """Count words in text, excluding markdown headers"""
    # Remove headers
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)
    # Remove extra whitespace
    text = ' '.join(text.split())
    if not text:
        return 0
    return len(text.split())

def grade_submission(filepath):
    """Grade a single submission file"""
    
    try:
        content = Path(filepath).read_text()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0
    
    score = 0
    max_score = 35
    details = []
    
    # Define required sections
    required_sections = [
        r"## Paradox 1: Ship of Theseus - Structure",
        r"## Paradox 1: Ship of Theseus - Historical Resolutions",
        r"## Paradox 2: Sorites - Structure",
        r"## Paradox 2: Sorites - Historical Resolutions",
        r"## Paradox 3: Newcomb's Problem - Structure",
        r"## Paradox 3: Newcomb's Problem - Historical Resolutions",
        r"## Paradox 4: Unexpected Hanging - Structure",
        r"## Paradox 4: Unexpected Hanging - Historical Resolutions",
        r"## Paradox 5: Prisoner's Dilemma - Structure",
        r"## Paradox 5: Prisoner's Dilemma - Historical Resolutions",
        r"## Defense of Resolution:",
        r"## Cross-Paradox Synthesis"
    ]
    
    # 1. Structure compliance (8 points)
    structure_score = 0
    missing_sections = []
    for section in required_sections:
        if re.search(section, content):
            structure_score += 1
        else:
            missing_sections.append(section)
    
    # Normalize to 8 points
    structure_points = round((structure_score / len(required_sections)) * 8)
    score += structure_points
    details.append(f"📋 Structure compliance: {structure_points}/8 points")
    if missing_sections:
        details.append(f"   ⚠️  Missing sections: {len(missing_sections)}")
    
    # 2. Extract sections and check word counts
    # Structure sections (5 × 50 words max = 10 points, 2 pts each)
    structure_sections = [
        (r"## Paradox 1: Ship of Theseus - Structure\s*\n(.*?)\n##", "Ship of Theseus Structure"),
        (r"## Paradox 2: Sorites - Structure\s*\n(.*?)\n##", "Sorites Structure"),
        (r"## Paradox 3: Newcomb's Problem - Structure\s*\n(.*?)\n##", "Newcomb Structure"),
        (r"## Paradox 4: Unexpected Hanging - Structure\s*\n(.*?)\n##", "Unexpected Hanging Structure"),
        (r"## Paradox 5: Prisoner's Dilemma - Structure\s*\n(.*?)\n##", "Prisoner's Dilemma Structure")
    ]
    
    structure_wc_score = 0
    for pattern, name in structure_sections:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            words = count_words(match.group(1))
            if words <= 50:
                structure_wc_score += 2
                details.append(f"✅ {name}: {words} words (≤50 required)")
            else:
                details.append(f"❌ {name}: {words} words (exceeds 50-word limit)")
        else:
            details.append(f"❌ {name}: Not found")
    
    score += structure_wc_score
    details.append(f"📊 Structure word counts: {structure_wc_score}/10 points")
    
    # Historical sections (5 × 75 words max = 10 points, 2 pts each)
    historical_sections = [
        (r"## Paradox 1: Ship of Theseus - Historical Resolutions\s*\n(.*?)\n##", "Ship Historical"),
        (r"## Paradox 2: Sorites - Historical Resolutions\s*\n(.*?)\n##", "Sorites Historical"),
        (r"## Paradox 3: Newcomb's Problem - Historical Resolutions\s*\n(.*?)\n##", "Newcomb Historical"),
        (r"## Paradox 4: Unexpected Hanging - Historical Resolutions\s*\n(.*?)\n##", "Unexpected Hanging Historical"),
        (r"## Paradox 5: Prisoner's Dilemma - Historical Resolutions\s*\n(.*?)\n##", "Prisoner's Dilemma Historical")
    ]
    
    historical_wc_score = 0
    for pattern, name in historical_sections:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            words = count_words(match.group(1))
            if words <= 75:
                historical_wc_score += 2
                details.append(f"✅ {name}: {words} words (≤75 required)")
            else:
                details.append(f"❌ {name}: {words} words (exceeds 75-word limit)")
        else:
            details.append(f"❌ {name}: Not found")
    
    score += historical_wc_score
    details.append(f"📚 Historical word counts: {historical_wc_score}/10 points")
    
    # Defense section (200-300 words = 3 points)
    defense_match = re.search(r"## Defense of Resolution:.*?\n(.*?)\n##", content, re.DOTALL)
    defense_wc_score = 0
    if defense_match:
        defense_words = count_words(defense_match.group(1))
        if 200 <= defense_words <= 300:
            defense_wc_score = 3
            details.append(f"✅ Defense: {defense_words} words (200-300 required)")
        else:
            details.append(f"❌ Defense: {defense_words} words (must be 200-300)")
    else:
        details.append(f"❌ Defense: Not found")
    
    score += defense_wc_score
    details.append(f"🛡️  Defense word count: {defense_wc_score}/3 points")
    
    # Synthesis section (150-200 words = 2 points)
    synthesis_match = re.search(r"## Cross-Paradox Synthesis\s*\n(.*?)(?:\n##|$)", content, re.DOTALL)
    synthesis_wc_score = 0
    if synthesis_match:
        synthesis_words = count_words(synthesis_match.group(1))
        if 150 <= synthesis_words <= 200:
            synthesis_wc_score = 2
            details.append(f"✅ Synthesis: {synthesis_words} words (150-200 required)")
        else:
            details.append(f"❌ Synthesis: {synthesis_words} words (must be 150-200)")
    else:
        details.append(f"❌ Synthesis: Not found")
    
    score += synthesis_wc_score
    details.append(f"🔗 Synthesis word count: {synthesis_wc_score}/2 points")
    
    # Defense elements (2 points)
    defense_elements_score = 0
    if defense_match:
        defense_text = defense_match.group(1).lower()
        has_objection = any(word in defense_text for word in ['objection', 'criticism', 'critique', 'counter', 'problem', 'challenge'])
        has_competing = any(word in defense_text for word in ['competing', 'alternative', 'other', 'different approach', 'another view', 'fails', 'less satisfactory'])
        
        if has_objection and has_competing:
            defense_elements_score = 2
            details.append(f"✅ Defense elements: Contains objection + competing resolution")
        else:
            missing = []
            if not has_objection:
                missing.append("objection")
            if not has_competing:
                missing.append("competing resolution")
            details.append(f"⚠️  Defense elements: Missing {', '.join(missing)}")
    
    score += defense_elements_score
    details.append(f"🎯 Defense required elements: {defense_elements_score}/2 points")
    
    # Print results
    print("\n" + "="*60)
    print(f"AUTOMATED SCORING RESULTS")
    print("="*60)
    for detail in details:
        print(detail)
    print("="*60)
    print(f"🏆 TOTAL AUTOMATED SCORE: {score}/{max_score} points")
    print("="*60)
    print(f"\n📝 Manual scoring (65 points) will evaluate:")
    print(f"   - Structural accuracy (15 pts)")
    print(f"   - Historical knowledge (15 pts)")
    print(f"   - Defense quality (20 pts)")
    print(f"   - Synthesis insight (15 pts)")
    print("="*60)
    
    return score

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grade.py <submission_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    grade_submission(filepath)
