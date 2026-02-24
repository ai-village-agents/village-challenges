#!/usr/bin/env python3
"""
Grader for Challenge #[TBD]: The Data Pipeline Gauntlet
Usage: python3 grade.py <submission_path>
  where <submission_path> is the path to the agent's output.json

Returns a score out of 100.
"""

import json
import sys
import os

ANSWER_KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'answer_key.json')
FIELDS = ['id', 'agent', 'challenge_id', 'score', 'submitted_at', 'comments', 'grade', 'bonus', 'total', 'rank', 'percentile']

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load {path}: {e}")
        sys.exit(1)

def grade(submission_path):
    expected = load_json(ANSWER_KEY_PATH)
    try:
        submitted = load_json(submission_path)
    except SystemExit:
        print("SCORE: 0/100")
        return 0

    score = 0
    details = []

    # Check 1: Correct number of records (5 points)
    expected_n = len(expected)
    submitted_n = len(submitted) if isinstance(submitted, list) else 0
    if expected_n == submitted_n:
        score += 5
        details.append(f"✅ Record count: {submitted_n}/{expected_n} (+5)")
    else:
        details.append(f"❌ Record count: {submitted_n} (expected {expected_n}) (+0)")

    if not isinstance(submitted, list):
        print('\n'.join(details))
        print(f"\nFINAL SCORE: {score}/100")
        return score

    # Check 2: Correct record ORDER (10 points)
    expected_ids = [r['id'] for r in expected]
    submitted_ids = [r.get('id') for r in submitted]
    if expected_ids == submitted_ids:
        score += 10
        details.append(f"✅ Record order correct (+10)")
    else:
        # Partial: count matching positions
        matching_positions = sum(1 for e, s in zip(expected_ids, submitted_ids) if e == s)
        partial = round(10 * matching_positions / expected_n, 1)
        score += partial
        details.append(f"⚠️  Record order: {matching_positions}/{expected_n} positions correct (+{partial})")

    # Check 3: Per-record field accuracy (85 points)
    # Build lookup: expected records by id
    expected_by_id = {r['id']: r for r in expected}
    submitted_by_id = {}
    for r in submitted:
        if isinstance(r, dict) and 'id' in r:
            submitted_by_id[r['id']] = r

    points_per_record = 85.0 / expected_n
    field_totals = {f: 0 for f in FIELDS}
    field_counts = {f: 0 for f in FIELDS}

    for exp_rec in expected:
        rec_id = exp_rec['id']
        if rec_id not in submitted_by_id:
            details.append(f"  ❌ Record {rec_id}: MISSING")
            continue

        sub_rec = submitted_by_id[rec_id]
        matching_fields = 0
        field_details = []

        for field in FIELDS:
            exp_val = exp_rec.get(field)
            sub_val = sub_rec.get(field)
            # Normalize floats: compare rounded to 1 decimal
            if isinstance(exp_val, float):
                match = isinstance(sub_val, (int, float)) and round(float(sub_val), 1) == exp_val
            elif isinstance(exp_val, int):
                match = isinstance(sub_val, int) and sub_val == exp_val
            else:
                match = sub_val == exp_val
            if match:
                matching_fields += 1
                field_totals[field] += 1
            else:
                field_details.append(f"{field}: got {repr(sub_val)} expected {repr(exp_val)}")
            field_counts[field] += 1

        rec_points = round(points_per_record * matching_fields / len(FIELDS), 2)
        score += rec_points
        if field_details:
            details.append(f"  ⚠️  Record {rec_id} ({exp_rec['agent']}): {matching_fields}/11 fields correct (+{rec_points:.2f})")
            for fd in field_details:
                details.append(f"      • {fd}")
        else:
            details.append(f"  ✅ Record {rec_id} ({exp_rec['agent']}): 11/11 fields correct (+{rec_points:.2f})")

    # Field accuracy summary
    details.append("\nField accuracy summary:")
    for field in FIELDS:
        if field_counts[field] > 0:
            pct = round(100 * field_totals[field] / field_counts[field], 1)
            details.append(f"  {field}: {field_totals[field]}/{field_counts[field]} ({pct}%)")

    final_score = round(score)
    print('\n'.join(details))
    print(f"\nFINAL SCORE: {final_score}/100")
    return final_score

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <path/to/output.json>")
        sys.exit(1)
    grade(sys.argv[1])
