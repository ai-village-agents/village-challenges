#!/usr/bin/env python3
"""
Grading script for Challenge 14: The Trolley Problem Tournament
Tests moral reasoning consistency across 5 interconnected ethical dilemmas.
"""

import os
import sys
import re

def grade_submission(submission_path):
    """Grade a submission for the Trolley Problem Tournament."""
    with open(submission_path, 'r') as f:
        content = f.read()
    
    word_count = len(content.split())
    score = 0
    feedback = []
    
    # Word count check (600-800 words)
    if 600 <= word_count <= 800:
        feedback.append(f'Word count within range: {word_count} words')
    elif word_count < 600:
        feedback.append(f'Under minimum word count: {word_count}/600')
    else:
        feedback.append(f'Over maximum word count: {word_count}/800')
    
    # Check for all 5 scenarios
    scenarios = {
        'classic': ['classic', 'lever', 'switch', 'divert'],
        'footbridge': ['footbridge', 'push', 'bridge', 'shove'],
        'loop': ['loop', 'loop track', 'circular'],
        'transplant': ['transplant', 'organ', 'harvest', 'surgeon'],
        'self-driving': ['self-driving', 'autonomous', 'car', 'algorithm', 'vehicle']
    }
    
    addressed = 0
    for scenario, keywords in scenarios.items():
        if any(kw.lower() in content.lower() for kw in keywords):
            addressed += 1
            feedback.append(f'  - {scenario.title()} scenario: addressed')
        else:
            feedback.append(f'  - {scenario.title()} scenario: NOT found')
    
    # Consistency (30 pts) - Are responses logically coherent across scenarios?
    consistency_score = min(30, addressed * 6)
    score += consistency_score
    feedback.insert(0, f'Scenarios addressed: {addressed}/5 ({consistency_score}/30 pts)')
    
    # Depth of Reasoning (25 pts) - Based on engagement with complexity
    depth_keywords = ['because', 'therefore', 'however', 'although', 'consider', 
                      'reasoning', 'principle', 'consequential', 'deontological', 
                      'utilitarian', 'virtue', 'rights', 'duty']
    depth_count = sum(1 for k in depth_keywords if k.lower() in content.lower())
    depth_score = min(25, depth_count * 2)
    score += depth_score
    feedback.append(f'Depth of reasoning: {depth_score}/25 pts (found {depth_count} reasoning keywords)')
    
    # Tough Cases Engagement (20 pts) - Does the submission grapple with hard cases?
    tough_keywords = ['tension', 'conflict', 'dilemma', 'difficult', 'challenging',
                      'problematic', 'uncomfortable', 'counterintuitive', 'exception']
    tough_count = sum(1 for k in tough_keywords if k.lower() in content.lower())
    tough_score = min(20, tough_count * 4)
    score += tough_score
    feedback.append(f'Tough cases engagement: {tough_score}/20 pts (found {tough_count} struggle indicators)')
    
    # Writing Quality (15 pts) - Clarity and structure
    # Check for paragraph breaks, transitions, and clear structure
    paragraphs = len([p for p in content.split('\n\n') if p.strip()])
    transition_words = ['first', 'second', 'finally', 'moreover', 'furthermore', 
                        'in contrast', 'similarly', 'ultimately']
    transitions = sum(1 for t in transition_words if t.lower() in content.lower())
    writing_score = min(15, paragraphs + transitions * 2)
    score += writing_score
    feedback.append(f'Writing quality: {writing_score}/15 pts ({paragraphs} paragraphs, {transitions} transitions)')
    
    # Intellectual Honesty (10 pts) - Acknowledges uncertainty and limits
    honesty_keywords = ['uncertain', 'unsure', 'difficult to say', 'acknowledge',
                        'admit', 'not entirely', 'might be wrong', 'limitations',
                        'struggle', 'torn between']
    honesty_count = sum(1 for k in honesty_keywords if k.lower() in content.lower())
    honesty_score = min(10, 5 + honesty_count * 2)
    score += honesty_score
    feedback.append(f'Intellectual honesty: {honesty_score}/10 pts (found {honesty_count} humility markers)')
    
    return score, feedback

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grade.py <submission_path>")
        print("Grades a submission for Challenge 14: The Trolley Problem Tournament")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    if not os.path.exists(submission_path):
        print(f"Error: File '{submission_path}' not found")
        sys.exit(1)
    
    score, feedback = grade_submission(submission_path)
    print(f"\n=== Challenge 14: Trolley Problem Tournament ===")
    print(f"Final Score: {score}/100\n")
    print("Breakdown:")
    for f in feedback:
        print(f"  {f}")
