#!/usr/bin/env python3
"""
Validator and grader for Challenge 14: Supply Chain Optimization

Scoring:
- 40 points: Correctness (all demands met, supply constraints honored)
- 40 points: Optimization (cost efficiency relative to baseline)
- 20 points: Code quality (clarity, comments, efficiency)
"""

import json
import sys
from pathlib import Path

def validate_solution(solution_data, test_case):
    """
    Validate solution against test case.
    
    Returns: (is_valid, errors, warnings, total_cost)
    """
    errors = []
    warnings = []
    
    # Check required fields
    if 'flows' not in solution_data:
        errors.append("Missing 'flows' field in solution")
        return False, errors, warnings, float('inf')
    
    flows = solution_data['flows']
    if not isinstance(flows, list):
        errors.append("'flows' must be a list")
        return False, errors, warnings, float('inf')
    
    # Track flow by node
    node_inflow = {}
    node_outflow = {}
    total_cost = 0
    
    # Create edge lookup
    edge_map = {}
    for edge in test_case['edges']:
        key = (edge['from'], edge['to'])
        edge_map[key] = edge
    
    # Process flows
    for flow_item in flows:
        if not isinstance(flow_item, dict):
            errors.append("Each flow must be a dictionary")
            continue
        
        if 'from' not in flow_item or 'to' not in flow_item or 'amount' not in flow_item:
            errors.append(f"Flow missing required fields: {flow_item}")
            continue
        
        from_node = flow_item['from']
        to_node = flow_item['to']
        amount = flow_item['amount']
        
        # Check if edge exists
        if (from_node, to_node) not in edge_map:
            errors.append(f"Invalid edge: {from_node} -> {to_node}")
            continue
        
        edge = edge_map[(from_node, to_node)]
        
        # Check capacity constraint
        if amount < 0:
            errors.append(f"Negative flow: {from_node} -> {to_node} = {amount}")
            continue
        
        if amount > edge['capacity']:
            errors.append(f"Capacity exceeded: {from_node} -> {to_node} = {amount} (capacity: {edge['capacity']})")
            continue
        
        # Track flow
        node_inflow[to_node] = node_inflow.get(to_node, 0) + amount
        node_outflow[from_node] = node_outflow.get(from_node, 0) + amount
        
        # Calculate cost
        total_cost += amount * edge['cost']
    
    if errors:
        return False, errors, warnings, float('inf')
    
    # Validate supply constraints
    for supplier in test_case['suppliers']:
        sid = supplier['id']
        supply = supplier['supply']
        outflow = node_outflow.get(sid, 0)
        
        if outflow > supply:
            errors.append(f"Supply exceeded: {sid} has {supply} supply but {outflow} outflow")
    
    # Validate demand constraints
    for customer in test_case['customers']:
        cid = customer['id']
        demand = customer['demand']
        inflow = node_inflow.get(cid, 0)
        
        if inflow < demand:
            warnings.append(f"Demand not met: {cid} requires {demand} but receives {inflow}")
    
    if errors:
        return False, errors, warnings, total_cost
    
    # All constraints satisfied
    return True, errors, warnings, total_cost

def calculate_baseline_cost(test_case):
    """
    Calculate baseline cost using nearest-neighbor greedy approach.
    This is used as a reference for optimization scoring.
    """
    # Simple greedy: for each customer, route demand via cheapest path
    total_cost = 0
    
    for customer in test_case['customers']:
        remaining_demand = customer['demand']
        cid = customer['id']
        
        # Find all edges into this customer, sorted by cost
        incoming = []
        for edge in test_case['edges']:
            if edge['to'] == cid:
                incoming.append(edge)
        
        incoming.sort(key=lambda e: e['cost'])
        
        # Allocate using cheapest edges first
        for edge in incoming:
            if remaining_demand <= 0:
                break
            
            # Allocate min(remaining_demand, edge_capacity)
            amount = min(remaining_demand, edge['capacity'])
            total_cost += amount * edge['cost']
            remaining_demand -= amount
    
    return total_cost

def grade_solution(solution_file, test_case_file):
    """
    Grade a solution against a test case.
    
    Returns: (score, feedback)
    """
    try:
        with open(solution_file, 'r') as f:
            solution = json.load(f)
        with open(test_case_file, 'r') as f:
            test_case = json.load(f)
    except Exception as e:
        return 0, f"Failed to load files: {e}"
    
    # Validate solution
    is_valid, errors, warnings, total_cost = validate_solution(solution, test_case)
    
    if not is_valid:
        feedback = f"Solution invalid: {'; '.join(errors)}"
        return 0, feedback
    
    # Calculate baseline
    baseline_cost = calculate_baseline_cost(test_case)
    
    # Scoring breakdown:
    # 40 points: Correctness (all constraints met)
    correctness_score = 40 if not warnings else max(20, 40 - len(warnings) * 5)
    
    # 40 points: Optimization (cost efficiency)
    if baseline_cost == 0:
        optimization_score = 40
    else:
        cost_ratio = total_cost / baseline_cost
        if cost_ratio <= 0.8:
            optimization_score = 40
        elif cost_ratio <= 1.0:
            optimization_score = 40 - 5 * (cost_ratio - 0.8) / 0.2
        elif cost_ratio <= 1.2:
            optimization_score = 35 - 15 * (cost_ratio - 1.0) / 0.2
        else:
            optimization_score = max(0, 20 - (cost_ratio - 1.2) * 5)
    
    # 20 points: Code quality (basic check)
    code_quality_score = 20
    if 'notes' not in solution:
        code_quality_score -= 5
    
    total_score = min(100, max(0, int(correctness_score + optimization_score + code_quality_score)))
    
    feedback = f"Correctness: {correctness_score:.1f}/40 | Optimization: {optimization_score:.1f}/40 (cost={total_cost}, baseline={baseline_cost}) | Quality: {code_quality_score}/20 | Total: {total_score}/100"
    
    return total_score, feedback

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python grade.py <solution_file> [test_case_file]")
        sys.exit(1)
    
    solution_file = sys.argv[1]
    test_case_file = sys.argv[2] if len(sys.argv) > 2 else 'test_case.json'
    
    score, feedback = grade_solution(solution_file, test_case_file)
    print(f"Score: {score}")
    print(f"Feedback: {feedback}")
