#!/usr/bin/env python3
"""
Grading script for the Logical Consistency Audit challenge.

Scoring:
- True Positive (correct contradiction identified): 10 points each (max 70 points)
- Partial credit (subset of contradicting statements): 5 points
- False Positive (incorrect contradiction claimed): -5 points penalty
- Explanation Quality bonus: +4 points per correct contradiction (max 28 points)
- Proper JSON formatting: 2 points
- Minimum total score: 0 (no negative totals)
- Maximum possible score: 100 points
"""

import json
import sys
import argparse
from pathlib import Path

# Answer key data - the 7 correct contradictions
ANSWER_KEY = {
    1: {"statement_ids": {1, 2, 3, 4, 5}, "keywords": ["senior", "member", "3 years", "alice", "committee", "2024", "2026"]},
    2: {"statement_ids": {6, 7, 8, 9}, "keywords": ["quorum", "15", "12", "resolution", "47", "vote", "voting event"]},
    3: {"statement_ids": {10, 11, 12}, "keywords": ["department head", "two", "bob", "only", "review"]},
    4: {"statement_ids": {7, 15, 16, 17}, "keywords": ["budget", "voting event", "quorum", "2025", "emergency"]},
    5: {"statement_ids": {18, 19, 20}, "keywords": ["project lead", "5", "3", "carol", "projects"]},
    6: {"statement_ids": {21, 22}, "keywords": ["committee", "two", "three", "david", "positions"]},
    7: {"statement_ids": {23, 24, 25}, "keywords": ["expense", "500", "750", "executive director", "vacant", "emma", "approval"]},
}

def load_json_file(filepath):
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f), True
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}, False
    except FileNotFoundError:
        return {"error": "File not found"}, False

def extract_statement_ids(contradiction):
    """Extract statement IDs from a contradiction entry."""
    # Support various formats
    if isinstance(contradiction, dict):
        for key in ['statement_ids', 'statements', 'ids', 'involved_statements']:
            if key in contradiction:
                ids = contradiction[key]
                if isinstance(ids, list):
                    return set(ids)
                elif isinstance(ids, set):
                    return ids
    elif isinstance(contradiction, list):
        return set(contradiction)
    return set()

def check_explanation_quality(contradiction, answer_key_entry):
    """
    Check if the explanation demonstrates understanding of the contradiction.
    Returns True if at least 3 relevant keywords are mentioned.
    """
    explanation = ""
    if isinstance(contradiction, dict):
        for key in ['explanation', 'reasoning', 'description', 'analysis']:
            if key in contradiction:
                explanation = str(contradiction[key]).lower()
                break
    
    if not explanation:
        return False
    
    keywords_found = sum(1 for kw in answer_key_entry["keywords"] if kw.lower() in explanation)
    return keywords_found >= 3

def match_contradiction(submitted_ids, answer_key):
    """
    Find the best matching contradiction from the answer key.
    Returns (contradiction_id, match_type) where match_type is 'full', 'partial', or None.
    """
    best_match = None
    best_overlap = 0
    
    for c_id, c_data in answer_key.items():
        correct_ids = c_data["statement_ids"]
        overlap = len(submitted_ids & correct_ids)
        
        # Full match: submitted IDs are a superset or equal to correct IDs (core statements covered)
        if correct_ids <= submitted_ids:
            return c_id, 'full'
        
        # Also accept if submitted is a subset that covers the primary conflict
        # (at least 2 correct statements and >= 60% overlap)
        if overlap >= 2 and overlap >= len(correct_ids) * 0.6:
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = c_id
    
    if best_match and best_overlap >= 2:
        return best_match, 'partial'
    
    return None, None

def grade_submission(submission_path, verbose=False):
    """Grade a submission and return the score breakdown."""
    submission, valid_json = load_json_file(submission_path)
    
    results = {
        "submission_file": str(submission_path),
        "valid_json": valid_json,
        "true_positives": 0,
        "partial_matches": 0,
        "false_positives": 0,
        "explanation_bonuses": 0,
        "contradictions_found": [],
        "false_positive_details": [],
        "score_breakdown": {},
        "total_score": 0
    }
    
    if not valid_json:
        results["error"] = submission.get("error", "Unknown error")
        results["score_breakdown"] = {"json_format": 0, "total": 0}
        return results
    
    # JSON format bonus
    json_bonus = 2
    results["score_breakdown"]["json_format"] = json_bonus
    
    # Extract contradictions from submission
    contradictions = []
    if isinstance(submission, dict):
        for key in ['contradictions', 'findings', 'results', 'identified_contradictions']:
            if key in submission and isinstance(submission[key], list):
                contradictions = submission[key]
                break
    elif isinstance(submission, list):
        contradictions = submission
    
    # Track which answer key contradictions have been matched
    matched_answers = set()
    
    # Score each submitted contradiction
    for i, cont in enumerate(contradictions):
        submitted_ids = extract_statement_ids(cont)
        
        if not submitted_ids:
            if verbose:
                print(f"  Contradiction {i+1}: No statement IDs found, skipping")
            continue
        
        match_id, match_type = match_contradiction(submitted_ids, ANSWER_KEY)
        
        if match_id and match_id not in matched_answers:
            matched_answers.add(match_id)
            
            if match_type == 'full':
                results["true_positives"] += 1
                results["contradictions_found"].append({
                    "submitted_ids": list(submitted_ids),
                    "matched_contradiction": match_id,
                    "match_type": "full",
                    "points": 10
                })
                
                # Check explanation quality
                if check_explanation_quality(cont, ANSWER_KEY[match_id]):
                    results["explanation_bonuses"] += 1
                    results["contradictions_found"][-1]["explanation_bonus"] = 4
            else:
                results["partial_matches"] += 1
                results["contradictions_found"].append({
                    "submitted_ids": list(submitted_ids),
                    "matched_contradiction": match_id,
                    "match_type": "partial",
                    "points": 5
                })
        else:
            # False positive - either no match or duplicate
            results["false_positives"] += 1
            results["false_positive_details"].append({
                "submitted_ids": list(submitted_ids),
                "reason": "duplicate" if match_id else "no matching contradiction"
            })
    
    # Calculate scores
    tp_score = results["true_positives"] * 10
    partial_score = results["partial_matches"] * 5
    fp_penalty = results["false_positives"] * 5
    explanation_score = results["explanation_bonuses"] * 4
    
    results["score_breakdown"] = {
        "json_format": json_bonus,
        "true_positives": f"{results['true_positives']} x 10 = {tp_score}",
        "partial_matches": f"{results['partial_matches']} x 5 = {partial_score}",
        "false_positive_penalty": f"-{results['false_positives']} x 5 = -{fp_penalty}",
        "explanation_bonuses": f"{results['explanation_bonuses']} x 4 = {explanation_score}",
    }
    
    raw_score = json_bonus + tp_score + partial_score - fp_penalty + explanation_score
    results["total_score"] = max(0, min(100, raw_score))
    results["score_breakdown"]["raw_total"] = raw_score
    results["score_breakdown"]["final_total"] = results["total_score"]
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Grade Logical Consistency Audit submissions")
    parser.add_argument("submission", help="Path to submission JSON file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()
    
    results = grade_submission(args.submission, verbose=args.verbose)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"LOGICAL CONSISTENCY AUDIT - GRADING RESULTS")
        print(f"{'='*60}")
        print(f"Submission: {results['submission_file']}")
        print(f"Valid JSON: {'Yes' if results['valid_json'] else 'No'}")
        
        if not results['valid_json']:
            print(f"Error: {results.get('error', 'Unknown')}")
            print(f"\nTotal Score: 0/100")
            return
        
        print(f"\n--- Findings ---")
        print(f"True Positives (full match):  {results['true_positives']}/7")
        print(f"Partial Matches:              {results['partial_matches']}")
        print(f"False Positives:              {results['false_positives']}")
        print(f"Explanation Bonuses:          {results['explanation_bonuses']}")
        
        print(f"\n--- Score Breakdown ---")
        for key, val in results['score_breakdown'].items():
            print(f"  {key}: {val}")
        
        print(f"\n{'='*60}")
        print(f"TOTAL SCORE: {results['total_score']}/100")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
