#!/usr/bin/env python3
"""
Supply Chain Optimization Solver
Uses min-cost max-flow algorithm to find optimal routing.

Author: Claude Opus 4.5
"""

import json
import sys
from collections import defaultdict

def solve_min_cost_flow(test_case):
    """
    Solve the supply chain optimization using min-cost max-flow.
    Uses the successive shortest paths algorithm (Bellman-Ford based).
    """
    # Build graph
    # Node types: suppliers, warehouses, DCs, customers + source + sink
    nodes = set()
    edges_data = []
    
    # Collect all nodes
    for s in test_case['suppliers']:
        nodes.add(s['id'])
    for w in test_case['warehouses']:
        nodes.add(w['id'])
    for d in test_case['distribution_centers']:
        nodes.add(d['id'])
    for c in test_case['customers']:
        nodes.add(c['id'])
    
    # Add virtual source and sink
    source = '_SOURCE_'
    sink = '_SINK_'
    nodes.add(source)
    nodes.add(sink)
    
    # Create edge list with capacities and costs
    # Format: (from, to, capacity, cost)
    
    # Source -> Suppliers (capacity = supply, cost = 0)
    for s in test_case['suppliers']:
        edges_data.append((source, s['id'], s['supply'], 0))
    
    # Customers -> Sink (capacity = demand, cost = 0)
    for c in test_case['customers']:
        edges_data.append((c['id'], sink, c['demand'], 0))
    
    # All edges from test case
    for e in test_case['edges']:
        edges_data.append((e['from'], e['to'], e['capacity'], e['cost']))
    
    # Build adjacency list with residual capacities
    # graph[u][v] = {'capacity': cap, 'cost': cost, 'flow': 0}
    graph = defaultdict(dict)
    
    for u, v, cap, cost in edges_data:
        if v not in graph[u]:
            graph[u][v] = {'capacity': cap, 'cost': cost, 'flow': 0}
        else:
            # Multiple edges - take max capacity
            graph[u][v]['capacity'] = max(graph[u][v]['capacity'], cap)
        
        # Add reverse edge for residual graph
        if u not in graph[v]:
            graph[v][u] = {'capacity': 0, 'cost': -cost, 'flow': 0}
    
    def bellman_ford(source, sink):
        """Find shortest path by cost in residual graph."""
        dist = {n: float('inf') for n in nodes}
        parent = {n: None for n in nodes}
        dist[source] = 0
        
        # Relax edges V-1 times
        for _ in range(len(nodes) - 1):
            for u in graph:
                if dist[u] == float('inf'):
                    continue
                for v in graph[u]:
                    edge = graph[u][v]
                    residual_cap = edge['capacity'] - edge['flow']
                    if residual_cap > 0 and dist[u] + edge['cost'] < dist[v]:
                        dist[v] = dist[u] + edge['cost']
                        parent[v] = u
        
        if dist[sink] == float('inf'):
            return None, 0
        
        # Reconstruct path
        path = []
        node = sink
        while parent[node] is not None:
            path.append((parent[node], node))
            node = parent[node]
        path.reverse()
        
        # Find min residual capacity along path
        min_cap = float('inf')
        for u, v in path:
            residual_cap = graph[u][v]['capacity'] - graph[u][v]['flow']
            min_cap = min(min_cap, residual_cap)
        
        return path, min_cap
    
    # Successive shortest paths algorithm
    total_cost = 0
    total_flow = 0
    total_demand = sum(c['demand'] for c in test_case['customers'])
    
    while total_flow < total_demand:
        path, flow = bellman_ford(source, sink)
        if path is None or flow == 0:
            break
        
        # Limit flow to remaining demand
        flow = min(flow, total_demand - total_flow)
        
        # Augment flow along path
        for u, v in path:
            graph[u][v]['flow'] += flow
            graph[v][u]['flow'] -= flow
            total_cost += flow * graph[u][v]['cost']
        
        total_flow += flow
    
    # Extract solution flows (only original edges, not virtual ones)
    flows = []
    original_edges = {(e['from'], e['to']) for e in test_case['edges']}
    
    for u in graph:
        for v in graph[u]:
            if (u, v) in original_edges and graph[u][v]['flow'] > 0:
                flows.append({
                    'from': u,
                    'to': v,
                    'amount': graph[u][v]['flow']
                })
    
    return {
        'flows': flows,
        'notes': f"Solved using successive shortest paths (Bellman-Ford based min-cost max-flow). Total flow: {total_flow}, Total cost: {total_cost}"
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python solve.py <test_case.json> [output.json]")
        sys.exit(1)
    
    test_case_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'solution.json'
    
    with open(test_case_file, 'r') as f:
        test_case = json.load(f)
    
    solution = solve_min_cost_flow(test_case)
    
    with open(output_file, 'w') as f:
        json.dump(solution, f, indent=2)
    
    print(f"Solution written to {output_file}")
    print(f"Notes: {solution['notes']}")
