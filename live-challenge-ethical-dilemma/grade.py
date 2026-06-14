#!/usr/bin/env python3
"""
Grading script for the Ethical Dilemma Analysis challenge.
Usage: python3 grade.py <path-to-analysis.md>

This grader uses keyword/phrase detection to check for required elements.
It is designed to be deterministic and objective.
"""

import sys
import re
from pathlib import Path

def load_analysis(filepath):
    """Load and normalize the analysis text."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    # Normalize to lowercase for matching
    return text, text.lower()

def count_words(text):
    """Count words in text."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def check_stakeholder(text_lower, stakeholder_keywords, context_keywords):
    """
    Check if a stakeholder is mentioned with relevant context.
    Returns True if stakeholder keywords AND at least one context keyword appear nearby.
    """
    for sk in stakeholder_keywords:
        if sk in text_lower:
            # Check for context within 200 characters
            pos = text_lower.find(sk)
            window = text_lower[max(0, pos-200):pos+200+len(sk)]
            for ck in context_keywords:
                if ck in window:
                    return True
    return False

def check_value_conflict(text_lower, keywords_a, keywords_b, tension_words):
    """
    Check if a value conflict is discussed.
    Needs keywords from both sides AND a tension/tradeoff word nearby.
    """
    # Find if both value sets are mentioned
    has_a = any(k in text_lower for k in keywords_a)
    has_b = any(k in text_lower for k in keywords_b)
    has_tension = any(t in text_lower for t in tension_words)
    return has_a and has_b and has_tension

def check_action_analysis(text_lower, action_keywords, min_pros=2, min_cons=2):
    """
    Check if an action is analyzed with pros and cons.
    Returns (has_action, pros_count, cons_count)
    """
    has_action = any(k in text_lower for k in action_keywords)
    if not has_action:
        return False, 0, 0
    
    # Simple pro/con detection - look for positive and negative framing
    pro_patterns = [
        r'\bpro\b', r'benefit', r'advantage', r'improve', r'better', r'positive',
        r'faster', r'more accurate', r'save', r'efficient', r'enhance'
    ]
    con_patterns = [
        r'\bcon\b', r'risk', r'disadvantage', r'harm', r'worse', r'negative',
        r'concern', r'problem', r'issue', r'drawback', r'downside', r'cost'
    ]
    
    # Count unique pro/con mentions (rough heuristic)
    pros = len(set(p for p in pro_patterns if re.search(p, text_lower)))
    cons = len(set(p for p in con_patterns if re.search(p, text_lower)))
    
    return True, min(pros, 4), min(cons, 4)

def grade(filepath):
    """Grade the analysis and return detailed results."""
    text, text_lower = load_analysis(filepath)
    results = {
        'stakeholders': {},
        'value_conflicts': {},
        'actions': {},
        'recommendation': {},
        'completeness': {},
        'total': 0
    }
    
    # PART A: Stakeholder Identification (30 points)
    stakeholders = {
        'current_patients': {
            'keywords': ['current patient', 'existing patient', 'er patient', 'emergency patient', 'people currently'],
            'context': ['care', 'quality', 'speed', 'wait', 'triage', 'treatment', 'diagnosis', 'immediate', 'affected']
        },
        'future_patients': {
            'keywords': ['future patient', 'later patient', 'long-term', 'coming years', 'future people'],
            'context': ['improve', 'data', 'learn', 'better', 'later', 'eventually', 'over time', 'continuous']
        },
        'nursing_staff': {
            'keywords': ['nurs', 'staff', 'employee', 'worker', 'position', 'job'],
            'context': ['cut', 'lose', 'job', 'security', 'attrition', 'layoff', 'work', 'condition', 'displaced']
        },
        'administration': {
            'keywords': ['admin', 'hospital board', 'management', 'leadership', 'executive'],
            'context': ['budget', 'cost', 'liability', 'regulatory', 'compliance', 'reputation', 'decision', 'responsible']
        },
        'techhealth': {
            'keywords': ['techhealth', 'vendor', 'company', 'corporation', 'developer'],
            'context': ['commercial', 'profit', 'data', 'contract', 'business', 'interest', 'sell', 'revenue']
        },
        'rural_community': {
            'keywords': ['rural', 'underserve', '35%', 'training data'],
            'context': ['disparity', 'representation', 'bias', 'underrepresent', 'access', '3%', 'different', 'worse']
        }
    }
    
    for name, config in stakeholders.items():
        found = check_stakeholder(text_lower, config['keywords'], config['context'])
        results['stakeholders'][name] = 5 if found else 0
    
    # PART B: Value Conflict Analysis (28 points)
    tension_words = ['tradeoff', 'trade-off', 'tension', 'conflict', 'balance', 'versus', 'vs', 
                     'competing', 'weigh', 'dilemma', 'at the expense', 'but', 'however', 'cost of']
    
    value_conflicts = {
        'safety_vs_efficiency': {
            'a': ['safety', 'safe', 'harm', 'risk', 'accurate', 'life-threatening'],
            'b': ['efficien', 'resource', 'cost', 'fast', 'quick', 'speed', 'budget']
        },
        'privacy_vs_collective': {
            'a': ['privacy', 'confidential', 'data sharing', 'personal information', 'patient data'],
            'b': ['collective', 'improve', 'learn', 'continuous', 'benefit all', 'society', 'aggregate']
        },
        'workers_vs_future_patients': {
            'a': ['job', 'employee', 'worker', 'nurse', 'staff', 'position', 'livelihood'],
            'b': ['future patient', 'future care', 'better care', 'improved outcome', 'fund', 'quality']
        },
        'innovation_vs_precaution': {
            'a': ['innovation', 'adopt', 'early', 'new technology', 'progress', 'advance'],
            'b': ['precaution', 'caution', 'careful', 'risk', 'unknown', 'uncertain', 'wait', 'test']
        }
    }
    
    for name, config in value_conflicts.items():
        found = check_value_conflict(text_lower, config['a'], config['b'], tension_words)
        results['value_conflicts'][name] = 7 if found else 0
    
    # PART C: Action Analysis (24 points, need at least 3 actions)
    actions = {
        'deploy_fully': ['deploy full', 'full deploy', 'implement now', 'proceed with', 'option 1', 'fully in the er'],
        'reject': ['reject', 'decline', 'refuse', 'not adopt', 'option 2', 'continue current', 'human-only'],
        'pilot': ['pilot', 'trial', 'test', 'parallel', '6 month', 'option 3', 'limited deploy'],
        'negotiate': ['negotiate', 'modify', 'renegotiate', 'new terms', 'option 4', 'change contract']
    }
    
    actions_found = 0
    for name, keywords in actions.items():
        has_action, pros, cons = check_action_analysis(text_lower, keywords)
        if has_action and (pros >= 2 or cons >= 2):
            score = 0
            if pros >= 2:
                score += 4
            if cons >= 2:
                score += 4
            results['actions'][name] = score
            actions_found += 1
        else:
            results['actions'][name] = 0
    
    # PART D: Recommendation Quality (12 points)
    recommendation_keywords = ['recommend', 'suggest', 'advise', 'should', 'best option', 'my recommendation', 
                                'i believe', 'the hospital should', 'conclusion']
    has_recommendation = any(k in text_lower for k in recommendation_keywords)
    results['recommendation']['clear_recommendation'] = 4 if has_recommendation else 0
    
    # Check for supporting reasons (look for "because", "since", "reason", etc.)
    reason_patterns = ['because', 'since', 'reason', 'therefore', 'this is because', 'firstly', 'secondly',
                       'this allows', 'this ensures', 'this provides', 'key factor']
    reason_count = sum(1 for p in reason_patterns if p in text_lower)
    results['recommendation']['supporting_reasons'] = 4 if reason_count >= 2 else 0
    
    # Check for limitations acknowledged
    limitation_keywords = ['limitation', 'uncertain', 'caveat', 'risk', 'might not', 'may not work',
                           'depends on', 'assumption', 'if techhealth', 'acknowledge', 'imperfect',
                           'however', 'that said', 'downside']
    has_limitation = sum(1 for k in limitation_keywords if k in text_lower) >= 2
    results['recommendation']['limitations'] = 4 if has_limitation else 0
    
    # PART E: Completeness (6 points)
    word_count = count_words(text)
    results['completeness']['word_count'] = word_count
    results['completeness']['min_words_met'] = 3 if word_count >= 500 else 0
    results['completeness']['coherent'] = 3  # Default to pass - hard to auto-check
    
    # Calculate totals
    total = 0
    total += sum(results['stakeholders'].values())
    total += sum(results['value_conflicts'].values())
    total += sum(results['actions'].values())
    total += sum(v for k, v in results['recommendation'].items() if isinstance(v, int))
    total += results['completeness']['min_words_met']
    total += results['completeness']['coherent']
    results['total'] = total
    
    return results

def print_results(results):
    """Print formatted grading results."""
    print("=" * 60)
    print("ETHICAL DILEMMA ANALYSIS - GRADING RESULTS")
    print("=" * 60)
    
    print("\n--- PART A: Stakeholder Identification (30 points max) ---")
    stakeholder_names = {
        'current_patients': 'Current ER Patients',
        'future_patients': 'Future Patients',
        'nursing_staff': 'ER Nursing Staff',
        'administration': 'Hospital Administration',
        'techhealth': 'TechHealth Corp',
        'rural_community': 'Rural Community Members'
    }
    for key, name in stakeholder_names.items():
        score = results['stakeholders'].get(key, 0)
        status = "✓" if score > 0 else "✗"
        print(f"  {status} {name}: {score}/5")
    print(f"  Subtotal: {sum(results['stakeholders'].values())}/30")
    
    print("\n--- PART B: Value Conflict Analysis (28 points max) ---")
    conflict_names = {
        'safety_vs_efficiency': 'Safety vs. Efficiency',
        'privacy_vs_collective': 'Privacy vs. Collective Benefit',
        'workers_vs_future_patients': 'Current Workers vs. Future Patients',
        'innovation_vs_precaution': 'Innovation vs. Precaution'
    }
    for key, name in conflict_names.items():
        score = results['value_conflicts'].get(key, 0)
        status = "✓" if score > 0 else "✗"
        print(f"  {status} {name}: {score}/7")
    print(f"  Subtotal: {sum(results['value_conflicts'].values())}/28")
    
    print("\n--- PART C: Action Analysis (24 points max, need 3+ actions) ---")
    action_names = {
        'deploy_fully': 'Deploy Fully',
        'reject': 'Reject MediAssist',
        'pilot': 'Pilot Program',
        'negotiate': 'Negotiate Terms'
    }
    for key, name in action_names.items():
        score = results['actions'].get(key, 0)
        status = "✓" if score > 0 else "✗"
        print(f"  {status} {name}: {score}/8")
    print(f"  Subtotal: {sum(results['actions'].values())}/24")
    
    print("\n--- PART D: Recommendation Quality (12 points max) ---")
    rec = results['recommendation']
    print(f"  {'✓' if rec.get('clear_recommendation', 0) > 0 else '✗'} Clear recommendation: {rec.get('clear_recommendation', 0)}/4")
    print(f"  {'✓' if rec.get('supporting_reasons', 0) > 0 else '✗'} Supporting reasons: {rec.get('supporting_reasons', 0)}/4")
    print(f"  {'✓' if rec.get('limitations', 0) > 0 else '✗'} Limitations acknowledged: {rec.get('limitations', 0)}/4")
    rec_total = sum(v for k, v in rec.items() if isinstance(v, int))
    print(f"  Subtotal: {rec_total}/12")
    
    print("\n--- PART E: Completeness (6 points max) ---")
    comp = results['completeness']
    print(f"  Word count: {comp.get('word_count', 0)} (need 500+)")
    print(f"  {'✓' if comp.get('min_words_met', 0) > 0 else '✗'} Minimum words: {comp.get('min_words_met', 0)}/3")
    print(f"  {'✓' if comp.get('coherent', 0) > 0 else '✗'} Coherent: {comp.get('coherent', 0)}/3")
    print(f"  Subtotal: {comp.get('min_words_met', 0) + comp.get('coherent', 0)}/6")
    
    print("\n" + "=" * 60)
    print(f"TOTAL SCORE: {results['total']}/100")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 grade.py <path-to-analysis.md>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    results = grade(filepath)
    print_results(results)
