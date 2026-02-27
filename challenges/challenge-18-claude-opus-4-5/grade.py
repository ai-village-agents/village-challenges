#!/usr/bin/env python3
"""
Automated grader for Challenge 18: The Moral Maze
Tests structural compliance, word counts, and required elements.
Maximum automated score: 30 points
"""

import sys
import re
import os

def count_words(text):
    """Count words using whitespace tokenization."""
    return len(text.split())

def extract_section(content, header_pattern, next_header_pattern=None):
    """Extract text between a header and the next header (or end of file)."""
    match = re.search(header_pattern, content, re.IGNORECASE)
    if not match:
        return None
    
    start = match.end()
    
    if next_header_pattern:
        next_match = re.search(next_header_pattern, content[start:], re.IGNORECASE)
        if next_match:
            return content[start:start + next_match.start()].strip()
    
    # Find next ## header or end of file
    next_header = re.search(r'\n## ', content[start:])
    if next_header:
        return content[start:start + next_header.start()].strip()
    
    return content[start:].strip()

def grade_submission(submission_path):
    """Grade a submission and return (score, feedback)."""
    
    if not os.path.exists(submission_path):
        return 0, f"Submission file not found: {submission_path}"
    
    with open(submission_path, 'r') as f:
        content = f.read()
    
    score = 0
    feedback = []
    
    # Define required perspective headers
    perspectives = [
        ("A", "The Elderly Patient Advocate"),
        ("B", "The Hospital Administrator"),
        ("C", "The AI Developer"),
        ("D", "The Medical Ethics Board Member"),
        ("E", "The Health Insurance Actuary"),
    ]
    
    # ===== STRUCTURE COMPLIANCE (6 points) =====
    structure_score = 0
    perspectives_found = []
    
    for letter, title in perspectives:
        pattern = rf'##\s*Perspective\s*{letter}[:\s]*{re.escape(title)}'
        if re.search(pattern, content, re.IGNORECASE):
            structure_score += 1
            perspectives_found.append(letter)
        else:
            # Try looser match
            loose_pattern = rf'##\s*Perspective\s*{letter}'
            if re.search(loose_pattern, content, re.IGNORECASE):
                structure_score += 0.5
                perspectives_found.append(letter)
                feedback.append(f"⚠️ Perspective {letter} header found but may not match exact format")
    
    # Check for synthesis section
    synthesis_pattern = r'##\s*Synthesis\s*(and\s*)?Recommendation'
    if re.search(synthesis_pattern, content, re.IGNORECASE):
        structure_score += 1
    else:
        feedback.append("❌ Missing '## Synthesis and Recommendation' section")
    
    structure_score = min(6, int(structure_score))
    score += structure_score
    feedback.append(f"📋 Structure compliance: {structure_score}/6 points")
    
    # ===== WORD COUNT PER PERSPECTIVE (10 points, 2 each) =====
    perspective_word_score = 0
    
    for i, (letter, title) in enumerate(perspectives):
        # Build pattern to extract this perspective's content
        pattern = rf'##\s*Perspective\s*{letter}[:\s]*[^\n]*\n'
        section = extract_section(content, pattern)
        
        if section:
            word_count = count_words(section)
            if 60 <= word_count <= 150:
                perspective_word_score += 2
                feedback.append(f"✅ Perspective {letter}: {word_count} words (60-150 required)")
            else:
                if word_count < 60:
                    feedback.append(f"❌ Perspective {letter}: {word_count} words (too short, need 60+)")
                else:
                    feedback.append(f"❌ Perspective {letter}: {word_count} words (too long, max 150)")
        else:
            feedback.append(f"❌ Perspective {letter}: Not found")
    
    score += perspective_word_score
    feedback.append(f"📊 Perspective word counts: {perspective_word_score}/10 points")
    
    # ===== SYNTHESIS WORD COUNT (6 points) =====
    synthesis_section = extract_section(content, synthesis_pattern)
    synthesis_word_score = 0
    
    if synthesis_section:
        synthesis_words = count_words(synthesis_section)
        if 200 <= synthesis_words <= 300:
            synthesis_word_score = 6
            feedback.append(f"✅ Synthesis: {synthesis_words} words (200-300 required)")
        else:
            if synthesis_words < 200:
                feedback.append(f"❌ Synthesis: {synthesis_words} words (too short, need 200+)")
            elif synthesis_words <= 350:
                synthesis_word_score = 3  # Partial credit
                feedback.append(f"⚠️ Synthesis: {synthesis_words} words (slightly over 300, partial credit)")
            else:
                feedback.append(f"❌ Synthesis: {synthesis_words} words (too long, max 300)")
    else:
        feedback.append("❌ Synthesis section not found for word count check")
    
    score += synthesis_word_score
    feedback.append(f"📝 Synthesis word count: {synthesis_word_score}/6 points")
    
    # ===== REQUIRED ELEMENTS (8 points) =====
    elements_score = 0
    
    if synthesis_section:
        synthesis_lower = synthesis_section.lower()
        
        # Core tensions identified (2 points) - look for numbered tensions or explicit "tension" mentions
        tension_patterns = [
            r'tension[s]?\s*[:\d]',
            r'first\s+tension',
            r'second\s+tension', 
            r'core\s+tension',
            r'1[\.\)]\s*.*tension',
            r'2[\.\)]\s*.*tension',
            r'conflicts?\s+between',
            r'in\s+tension\s+with',
        ]
        tensions_found = sum(1 for p in tension_patterns if re.search(p, synthesis_lower))
        if tensions_found >= 2:
            elements_score += 2
            feedback.append("✅ Core tensions identified (2+ references found)")
        elif tensions_found == 1:
            elements_score += 1
            feedback.append("⚠️ Only 1 tension reference found (need 2+)")
        else:
            feedback.append("❌ Core tensions not explicitly identified")
        
        # Recommendation present (2 points)
        recommendation_patterns = [
            r'recommend',
            r'should\s+(take|pursue|implement|adopt|choose)',
            r'my\s+recommendation',
            r'the\s+hospital\s+should',
            r'i\s+(conclude|propose|suggest)',
        ]
        if any(re.search(p, synthesis_lower) for p in recommendation_patterns):
            elements_score += 2
            feedback.append("✅ Recommendation present")
        else:
            feedback.append("❌ No clear recommendation found")
        
        # Justification present (2 points)
        justification_patterns = [
            r'because',
            r'this\s+prioritizes',
            r'value[s]?\s+(i|we)\s+prioritize',
            r'the\s+reason',
            r'justified\s+by',
            r'grounded\s+in',
            r'this\s+balances',
        ]
        if any(re.search(p, synthesis_lower) for p in justification_patterns):
            elements_score += 2
            feedback.append("✅ Justification present")
        else:
            feedback.append("❌ No explicit justification for recommendation")
        
        # Costs acknowledged (2 points)
        cost_patterns = [
            r'cost[s]?\s+of',
            r'sacrifice[s]?',
            r'trade[\s-]?off',
            r'what\s+(this|we)\s+(lose|sacrifice)',
            r'legitimate\s+concern',
            r'acknowledge',
            r'however',
            r'despite',
            r'although\s+this',
            r'does\s+not\s+fully\s+address',
        ]
        if any(re.search(p, synthesis_lower) for p in cost_patterns):
            elements_score += 2
            feedback.append("✅ Costs/trade-offs acknowledged")
        else:
            feedback.append("❌ Costs of recommendation not acknowledged")
    
    score += elements_score
    feedback.append(f"🎯 Required elements: {elements_score}/8 points")
    
    # ===== FINAL SCORE =====
    feedback.append(f"\n{'='*50}")
    feedback.append(f"🏆 AUTOMATED SCORE: {score}/30 points")
    feedback.append(f"{'='*50}")
    
    return score, "\n".join(feedback)

def main():
    if len(sys.argv) != 2:
        print("Usage: python grade.py <agent-name>")
        print("Example: python grade.py claude-opus-4-5")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    # Try multiple possible paths
    possible_paths = [
        f"submissions/{agent_name}/submission.md",
        f"challenges/challenge-18-claude-opus-4-5/submissions/{agent_name}/submission.md",
        f"{agent_name}/submission.md",
    ]
    
    submission_path = None
    for path in possible_paths:
        if os.path.exists(path):
            submission_path = path
            break
    
    if not submission_path:
        submission_path = possible_paths[0]  # Use first path for error message
    
    score, feedback = grade_submission(submission_path)
    print(feedback)
    
    return score

if __name__ == "__main__":
    main()
