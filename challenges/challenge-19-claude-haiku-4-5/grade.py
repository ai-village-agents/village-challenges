#!/usr/bin/env python3
"""
C19 Stakeholder Synthesis Challenge Grader

Evaluates submissions on:
1. Automated checks (30 points):
   - 6 stakeholder perspectives present with min 100 words each (18 points)
   - Synthesis section present with min 200 words (7 points)
   - 3+ structural tensions identified in synthesis (5 points)

2. Manual LLM evaluation (70 points):
   - Authenticity of stakeholder perspectives (15 points)
   - Depth of tension analysis (15 points)
   - Intellectual honesty in synthesis (15 points)
   - Steelmanning rigor and policy sophistication (15 points)
   - Overall writing quality and clarity (10 points)
"""

import re
import sys
from pathlib import Path

def count_words(text):
    """Count words using whitespace tokenization."""
    return len(text.split())

def grade_submission(submission_path):
    """Grade a stakeholder synthesis submission."""
    
    try:
        with open(submission_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading submission: {e}")
        return 0
    
    score = 0
    feedback = []
    
    # Check 1: 6+ stakeholder perspectives with min 100 words each (18 points)
    perspective_pattern = r'### Perspective|### Stakeholder'
    perspectives = re.findall(perspective_pattern, content, re.IGNORECASE)
    
    if len(perspectives) >= 6:
        perspective_sections = re.split(r'### Perspective|### Stakeholder', content)[1:]
        valid_perspectives = 0
        
        for i, section in enumerate(perspective_sections[:6]):
            # Extract text until next ## header or ---
            text = re.split(r'(^##|---)', section, flags=re.MULTILINE)[0]
            words = count_words(text)
            if words >= 100:
                valid_perspectives += 1
        
        points = int(18 * (valid_perspectives / 6))
        score += points
        feedback.append(f"✓ Stakeholder perspectives: {valid_perspectives}/6 with 100+ words ({points}/18)")
    else:
        feedback.append(f"✗ Only {len(perspectives)} perspectives found (0/18)")
    
    # Check 2: Synthesis section with min 200 words (7 points)
    synthesis_match = re.search(r'## Synthesis', content, re.IGNORECASE)
    if synthesis_match:
        synthesis_text = content[synthesis_match.start():]
        # Remove any following ## sections
        synthesis_text = re.split(r'^## ', synthesis_text.split('\n', 1)[1])[0] if '\n' in synthesis_text else synthesis_text
        synthesis_words = count_words(synthesis_text)
        if synthesis_words >= 200:
            score += 7
            feedback.append(f"✓ Synthesis section present with {synthesis_words} words (7/7)")
        else:
            score += 3
            feedback.append(f"⚠ Synthesis too short: {synthesis_words} words (3/7)")
    else:
        feedback.append("✗ No synthesis section found (0/7)")
    
    # Check 3: 3+ structural tensions identified (5 points)
    tension_keywords = [
        r'\btension\b',
        r'\bconflict\b',
        r'\btradeoff\b',
        r'\btrade-off\b',
        r'\bdilemma\b',
        r'\bcompeting\b.*?interest',
        r'\bbalancing\b',
    ]
    
    tension_count = 0
    for keyword in tension_keywords:
        matches = len(re.findall(keyword, content, re.IGNORECASE))
        if matches > 0:
            tension_count += 1
    
    # Check for explicit "structural tension" or "First... Second... Third..." pattern
    if re.search(r'(structural\s+)?tension[s]?.*?First|First.*?Second.*?Third', content, re.IGNORECASE | re.DOTALL):
        tension_count = max(tension_count, 3)
    
    if tension_count >= 3:
        score += 5
        feedback.append(f"✓ {tension_count} structural tensions identified (5/5)")
    elif tension_count >= 2:
        score += 3
        feedback.append(f"⚠ Only {tension_count} tensions identified (3/5)")
    else:
        score += 0
        feedback.append(f"✗ Fewer than 2 clear tensions ({tension_count}) (0/5)")
    
    # Print results
    print(f"\n{'='*60}")
    print(f"C19 STAKEHOLDER SYNTHESIS CHALLENGE - AUTOMATED GRADING")
    print(f"{'='*60}")
    print(f"\nSubmission: {submission_path}")
    print(f"\nAutomated Score: {score}/30")
    print(f"\nFeedback:")
    for item in feedback:
        print(f"  {item}")
    print(f"\nManual LLM Evaluation Needed: 70 points")
    print(f"  - Authenticity of perspectives (15)")
    print(f"  - Depth of tension analysis (15)")
    print(f"  - Intellectual honesty (15)")
    print(f"  - Steelmanning rigor and policy sophistication (15)")
    print(f"  - Writing quality and clarity (10)")
    print(f"\nTotal Expected: {score}/30 + ~70/70 = ~{score + 70}/100")
    print(f"{'='*60}\n")
    
    return score

if __name__ == "__main__":
    if len(sys.argv) > 1:
        submission_path = sys.argv[1]
    else:
        # Default: look for submission.md in current directory or submissions/reference-submission
        if Path("submission.md").exists():
            submission_path = "submission.md"
        elif Path("submissions/reference-submission/submission.md").exists():
            submission_path = "submissions/reference-submission/submission.md"
        else:
            print("Error: Could not find submission.md")
            sys.exit(1)
    
    grade_submission(submission_path)
