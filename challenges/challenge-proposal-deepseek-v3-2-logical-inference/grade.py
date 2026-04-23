#!/usr/bin/env python3
"""
Grader for Logical Inference Gauntlet challenge.
"""

import sys
import os
import importlib.util
import json
from pathlib import Path

def load_solution(solution_path):
    """Load the solution module."""
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    solution = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solution)
    return solution

class TestCase:
    def __init__(self, problem_text, expected):
        self.problem_text = problem_text
        self.expected = expected  # dict with keys: consistent, contradiction, entailment_q3, entailment_q4, proof
        
def create_sample_test():
    """Create a sample test case."""
    problem_text = """### Statements ###
1. All dogs are mammals.
2. No reptiles are mammals.
3. Some mammals can swim.
4. If something is a dog, then it is not a reptile.
5. Either Spot is a dog or Spot is a reptile.
6. Spot is a mammal.
7. If Spot is a mammal, then Spot can swim.
8. Not all mammals can swim.

### Queries ###
Q1. Is the set of statements logically consistent? (Yes/No)
Q2. Which statement numbers, if any, form a minimal contradiction? (e.g., "3,8" or "None")
Q3. Does statement 6 logically follow from statements 1-5? (Yes/No/Undetermined)
Q4. From statements 1-4, does "Spot is not a reptile" follow? (Yes/No/Undetermined)
Q5. Provide a minimal proof sketch for Q4 if "Yes": list statement numbers in logical order.

### Domain ###
Constants: Spot
Predicates: Dog(x), Mammal(x), Reptile(x), CanSwim(x)
Relations: All, Some, No, If-Then, Either-Or, Not
"""
    
    # Expected answers for this specific test
    expected = {
        "consistent": False,  # Statements 3 and 8 are contradictory in classical logic
        "contradiction": [3, 8],  # "Some mammals can swim" vs "Not all mammals can swim"
        "entailment_q3": "Undetermined",  # From 1-5, we can't deduce Spot is mammal
        "entailment_q4": "Yes",  # From 1-4, Spot not reptile follows (if Spot is dog)
        "proof": [1, 4, 5]  # Using statements 1,4,5 (Spot is dog or reptile; if dog then not reptile)
    }
    return TestCase(problem_text, expected)

def create_hidden_tests():
    """Create hidden test cases (simplified for grader structure)."""
    tests = []
    
    # Test 1: Simple consistency
    problem1 = """### Statements ###
1. All A are B.
2. No B are C.
3. Some A are C.

### Queries ###
Q1. Is the set of statements logically consistent? (Yes/No)
Q2. Which statement numbers, if any, form a minimal contradiction? (e.g., "1,2,3" or "None")
Q3. Does statement 3 logically follow from statements 1-2? (Yes/No/Undetermined)
Q4. From statements 1-2, does "No A are C" follow? (Yes/No/Undetermined)
Q5. Provide a minimal proof sketch for Q4 if "Yes": list statement numbers in logical order.

### Domain ###
Constants: none
Predicates: A(x), B(x), C(x)
Relations: All, Some, No
"""
    expected1 = {
        "consistent": False,
        "contradiction": [1, 2, 3],
        "entailment_q3": "No",
        "entailment_q4": "Yes",
        "proof": [1, 2]
    }
    tests.append(TestCase(problem1, expected1))
    
    # Test 2: Consistent set
    problem2 = """### Statements ###
1. If it rains, the ground is wet.
2. It is raining.
3. The ground is wet.

### Queries ###
Q1. Is the set of statements logically consistent? (Yes/No)
Q2. Which statement numbers, if any, form a minimal contradiction? (e.g., "1,2,3" or "None")
Q3. Does statement 3 logically follow from statements 1-2? (Yes/No/Undetermined)
Q4. From statements 1-2, does "The ground is wet" follow? (Yes/No/Undetermined)
Q5. Provide a minimal proof sketch for Q4 if "Yes": list statement numbers in logical order.

### Domain ###
Constants: none
Predicates: Rains(), WetGround()
Relations: If-Then
"""
    expected2 = {
        "consistent": True,
        "contradiction": [],
        "entailment_q3": "Yes",
        "entailment_q4": "Yes",
        "proof": [1, 2]
    }
    tests.append(TestCase(problem2, expected2))
    
    return tests

def evaluate_solution(solution, test_case):
    """Evaluate solution against a test case."""
    results = {}
    score = 0
    
    # Parse statements
    try:
        statements = solution.parse_statements(test_case.problem_text)
        results["parse_success"] = True
        # Basic check: should return a list
        if isinstance(statements, list) and len(statements) > 0:
            score += 20  # Full parsing points for sample
            results["parse_score"] = 20
        else:
            results["parse_score"] = 0
    except Exception as e:
        results["parse_success"] = False
        results["parse_error"] = str(e)
        results["parse_score"] = 0
        statements = []
    
    # Check consistency
    try:
        consistent = solution.is_consistent(statements)
        if consistent == test_case.expected["consistent"]:
            score += 20
            results["consistent_correct"] = True
        else:
            results["consistent_correct"] = False
    except Exception as e:
        results["consistent_error"] = str(e)
        results["consistent_correct"] = False
    
    # Find contradiction
    try:
        contradiction = solution.find_contradiction(statements)
        # Sort for comparison
        if sorted(contradiction) == sorted(test_case.expected["contradiction"]):
            score += 20
            results["contradiction_correct"] = True
        else:
            results["contradiction_correct"] = False
            results["contradiction_got"] = contradiction
            results["contradiction_expected"] = test_case.expected["contradiction"]
    except Exception as e:
        results["contradiction_error"] = str(e)
        results["contradiction_correct"] = False
    
    # Check entailment Q3 (statement 6 from 1-5 in sample, adjust for other tests)
    # For simplicity, we'll test with first test's indices
    try:
        # For sample test: premises = statements[0:5], conclusion = statements[5]
        if len(statements) >= 6:
            entail_q3 = solution.check_entailment(statements[0:5], 6, statements)
            if entail_q3 == test_case.expected["entailment_q3"]:
                score += 15
                results["entailment_q3_correct"] = True
            else:
                results["entailment_q3_correct"] = False
                results["entailment_q3_got"] = entail_q3
        else:
            results["entailment_q3_correct"] = False
    except Exception as e:
        results["entailment_q3_error"] = str(e)
        results["entailment_q3_correct"] = False
    
    # Check entailment Q4 (statements 1-4 to "Spot not reptile")
    try:
        if len(statements) >= 5:
            # For sample: premises = statements[0:4], conclusion about "Spot not reptile"
            # We'll use a placeholder index; actual test would need mapping
            # Simplified: just check function call
            entail_q4 = solution.check_entailment(statements[0:4], 5, statements)
            if entail_q4 == test_case.expected["entailment_q4"]:
                score += 15
                results["entailment_q4_correct"] = True
            else:
                results["entailment_q4_correct"] = False
                results["entailment_q4_got"] = entail_q4
        else:
            results["entailment_q4_correct"] = False
    except Exception as e:
        results["entailment_q4_error"] = str(e)
        results["entailment_q4_correct"] = False
    
    # Check proof generation
    try:
        if len(statements) >= 5:
            proof = solution.generate_proof(statements[0:4], 5, statements)
            # Sort for comparison
            if sorted(proof) == sorted(test_case.expected["proof"]):
                score += 10
                results["proof_correct"] = True
            else:
                results["proof_correct"] = False
                results["proof_got"] = proof
                results["proof_expected"] = test_case.expected["proof"]
        else:
            results["proof_correct"] = False
    except Exception as e:
        results["proof_error"] = str(e)
        results["proof_correct"] = False
    
    results["total_score"] = score
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python grade.py <path_to_solution.py>")
        sys.exit(1)
    
    solution_path = sys.argv[1]
    if not os.path.exists(solution_path):
        print(f"Error: File not found: {solution_path}")
        sys.exit(1)
    
    print(f"Grading: {solution_path}")
    
    try:
        solution = load_solution(solution_path)
    except Exception as e:
        print(f"Error loading solution: {e}")
        sys.exit(1)
    
    # Run tests
    sample_test = create_sample_test()
    hidden_tests = create_hidden_tests()
    all_tests = [sample_test] + hidden_tests
    
    total_score = 0
    max_score = 100 * len(all_tests)
    
    for i, test in enumerate(all_tests):
        print(f"\n{'='*60}")
        print(f"Test {i+1}")
        results = evaluate_solution(solution, test)
        
        print(f"Parse success: {results.get('parse_success', False)}")
        if 'parse_error' in results:
            print(f"Parse error: {results['parse_error']}")
        
        print(f"Consistency correct: {results.get('consistent_correct', False)}")
        print(f"Contradiction correct: {results.get('contradiction_correct', False)}")
        if 'contradiction_got' in results:
            print(f"  Got: {results['contradiction_got']}, Expected: {results['contradiction_expected']}")
        
        print(f"Entailment Q3 correct: {results.get('entailment_q3_correct', False)}")
        if 'entailment_q3_got' in results:
            print(f"  Got: {results['entailment_q3_got']}")
        
        print(f"Entailment Q4 correct: {results.get('entailment_q4_correct', False)}")
        if 'entailment_q4_got' in results:
            print(f"  Got: {results['entailment_q4_got']}")
        
        print(f"Proof correct: {results.get('proof_correct', False)}")
        if 'proof_got' in results:
            print(f"  Got: {results['proof_got']}, Expected: {results['proof_expected']}")
        
        print(f"Test score: {results['total_score']}/100")
        total_score += results['total_score']
    
    final_score = total_score / len(all_tests)  # Average across tests
    print(f"\n{'='*60}")
    print(f"FINAL SCORE: {final_score:.1f}/100")
    
    # Output JSON for automated processing
    output = {
        "score": final_score,
        "max_score": 100,
        "tests_run": len(all_tests)
    }
    
    with open("grade_results.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
