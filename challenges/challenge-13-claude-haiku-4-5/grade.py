#!/usr/bin/env python3

import json
import sys
from pathlib import Path

def grade(submission_path):
    """
    Grade a submission for Challenge 13: Logical Consistency Auditor
    
    Args:
        submission_path: Path to the submission file (should be answers.json or answers.md)
    
    Returns:
        dict with 'score' (0-100) and 'feedback'
    """
    
    # Load the correct answer key
    challenge_dir = Path(__file__).parent
    with open(challenge_dir / 'answer_key.json', 'r') as f:
        answer_key = json.load(f)
    
    correct_indices = set(answer_key['inconsistencies'])
    
    # Parse submission
    submission_file = Path(submission_path)
    
    if submission_file.suffix == '.json':
        try:
            with open(submission_file, 'r') as f:
                submission = json.load(f)
            
            if isinstance(submission, dict) and 'inconsistencies' in submission:
                submitted_indices = set(submission['inconsistencies'])
            else:
                return {
                    'score': 0,
                    'feedback': 'Invalid JSON format. Expected {"inconsistencies": [...]}'
                }
        except json.JSONDecodeError:
            return {
                'score': 0,
                'feedback': 'Invalid JSON. Could not parse submission file.'
            }
    
    elif submission_file.suffix == '.md':
        # Parse markdown format (comma-separated or list format)
        with open(submission_file, 'r') as f:
            content = f.read()
        
        # Try to extract list of indices
        submitted_indices = set()
        for line in content.split('\n'):
            # Look for lines with indices
            if any(char.isdigit() for char in line):
                # Extract all numbers from the line
                import re
                numbers = re.findall(r'\b\d+\b', line)
                submitted_indices.update(int(n) for n in numbers if 1 <= int(n) <= 27)
    else:
        return {
            'score': 0,
            'feedback': f'Unsupported file format: {submission_file.suffix}'
        }
    
    # Calculate score
    correct_count = len(correct_indices & submitted_indices)
    false_positive_count = len(submitted_indices - correct_indices)
    false_negative_count = len(correct_indices - submitted_indices)
    
    # Scoring: 10 points per correct identification, -5 per false positive
    score = correct_count * 10 - false_positive_count * 5
    score = max(0, min(100, score))  # Cap between 0-100
    
    feedback = {
        'score': score,
        'correct_identifications': correct_count,
        'false_positives': false_positive_count,
        'false_negatives': false_negative_count,
        'submitted_indices': sorted(list(submitted_indices)),
        'correct_indices': sorted(list(correct_indices)),
        'feedback': (
            f'You correctly identified {correct_count}/{len(correct_indices)} inconsistencies. '
            f'False positives: {false_positive_count}, False negatives: {false_negative_count}. '
            f'Score: {score}/100'
        )
    }
    
    return feedback

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python grade.py <submission_file>')
        sys.exit(1)
    
    result = grade(sys.argv[1])
    print(json.dumps(result, indent=2))
