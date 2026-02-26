#!/usr/bin/env python3
"""
Greedy Reference Solution for Supply Chain Optimization Challenge
Algorithm: Greedy nearest-neighbor flow assignment
- Sort all demand nodes and their incoming edges
- Greedily assign flow from cheapest sources
- Work backward through supply chain tiers
This is NOT optimal but demonstrates baseline approach for grading comparison.
"""
import json
import sys
def solve_greedy(input_file):
    """Solve supply chain optimization using greedy nearest-neighbor approach."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    nodes = data['nodes']
    edges = data['edges']
    
    # Build adjacency structures
    edge_dict = {}
    for edge in edges:
        key = (edge['from'], edge['to'])
        edge_dict[key] = edge
    
    # Extract all node info
    suppliers = {n['id']: n['supply'] for n in nodes['suppliers']}
    warehouses = {n['id']: n['capacity'] for n in nodes['warehouses']}
    dcenters = {n['id']: n['capacity'] for n in nodes['distribution_centers']}
    customers = {n['id']: n['demand'] for n in nodes['customers']}
    
    # Sort customer-facing edges by cost (D->C edges)
    dc_c_edges = [e for e in edges if e['from'][0] == 'D' and e['to'][0] == 'C']
    dc_c_edges.sort(key=lambda e: e['cost'])
    
    # Allocate flow greedily from customers backward
    flow_assignment = {}
    remaining_supply = suppliers.copy()
    remaining_demand = customers.copy()
    used_capacity = {e: 0 for e in [tuple(ed.values())[:2] for ed in edges]}
    
    # Process each D->C edge in order of cost
    for edge in dc_c_edges:
        src, dst = edge['from'], edge['to']
        max_flow = min(
            edge['capacity'],
            remaining_demand.get(dst, 0)
        )
        
        if max_flow > 0:
            flow_assignment[(src, dst)] = max_flow
            remaining_demand[dst] -= max_flow
    
    # Backward flow allocation through warehouse layer
    w_d_edges = [e for e in edges if e['from'][0] == 'W' and e['to'][0] == 'D']
    w_d_edges.sort(key=lambda e: e['cost'])
    
    remaining_dc_demand = {}
    for (dc, cust), amount in flow_assignment.items():
        remaining_dc_demand[dc] = remaining_dc_demand.get(dc, 0) + amount
    
    for edge in w_d_edges:
        src, dst = edge['from'], edge['to']
        max_flow = min(
            edge['capacity'],
            remaining_dc_demand.get(dst, 0)
        )
        if max_flow > 0:
            flow_assignment[(src, dst)] = max_flow
            remaining_dc_demand[dst] -= max_flow
    
    # Supplier to warehouse layer
    s_w_edges = [e for e in edges if e['from'][0] == 'S' and e['to'][0] == 'W']
    s_w_edges.sort(key=lambda e: e['cost'])
    
    remaining_w_demand = {}
    for (wh, dc), amount in flow_assignment.items():
        remaining_w_demand[wh] = remaining_w_demand.get(wh, 0) + amount
    
    for edge in s_w_edges:
        src, dst = edge['from'], edge['to']
        max_flow = min(
            edge['capacity'],
            remaining_w_demand.get(dst, 0),
            remaining_supply.get(src, 0)
        )
        if max_flow > 0:
            flow_assignment[(src, dst)] = max_flow
            remaining_supply[src] -= max_flow
            remaining_w_demand[dst] -= max_flow
    
    # Calculate total cost
    total_cost = 0
    for (src, dst), amount in flow_assignment.items():
        for edge in edges:
            if edge['from'] == src and edge['to'] == dst:
                total_cost += edge['cost'] * amount
                break
    
    # Format output
    flows = [
        {'from': src, 'to': dst, 'amount': amount}
        for (src, dst), amount in flow_assignment.items()
    ]
    
    result = {
        'flows': flows,
        'total_cost': total_cost,
        'algorithm': 'Greedy nearest-neighbor (baseline for comparison)'
    }
    
    return result
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python greedy_solution.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'greedy_output.json'
    
    result = solve_greedy(input_file)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Solution written to {output_file}")
    print(f"Total cost: {result['total_cost']}")
