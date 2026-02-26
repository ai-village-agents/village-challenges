#!/usr/bin/env python3
"""
Multi-Stage Optimization Solver
Solves all three stages: pathfinding, allocation, scheduling

Author: Claude Opus 4.5
"""

import json
import sys
import heapq
from collections import defaultdict

def solve_stage1(graph):
    """
    Stage 1: Find shortest path from source to sink avoiding forbidden nodes.
    Uses Dijkstra's algorithm.
    """
    nodes = set(graph["nodes"])
    forbidden = set(graph.get("forbidden", []))
    source = graph["source"]
    sink = graph["sink"]
    
    # Build adjacency list
    adj = defaultdict(list)
    for edge in graph["edges"]:
        u, v, w = edge["from"], edge["to"], float(edge["weight"])
        adj[u].append((v, w))
    
    if source in forbidden or sink in forbidden:
        return [], float('inf')
    
    # Dijkstra
    dist = {n: float('inf') for n in nodes}
    parent = {n: None for n in nodes}
    dist[source] = 0
    heap = [(0, source)]
    
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == sink:
            break
        for v, w in adj[u]:
            if v in forbidden:
                continue
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))
    
    # Reconstruct path
    if dist[sink] == float('inf'):
        return [], float('inf')
    
    path = []
    node = sink
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    
    return path, dist[sink]


def solve_stage2(resources, path, tasks_ops):
    """
    Stage 2: Allocate resources on path nodes to maximize utility.
    Uses knapsack DP with minimum requirements from Stage 3.
    """
    if not path:
        return {}
    
    budget = float(resources.get("budget", 0))
    node_cost = resources.get("node_cost", {})
    utility = resources.get("utility", {})
    
    path_set = set(path)
    
    # Calculate minimum requirements per node from tasks
    min_req = defaultdict(int)
    for op in tasks_ops:
        node = op.get("node", "")
        if node in path_set:
            req = int(op.get("requires", 0))
            min_req[node] = max(min_req[node], req)
    
    # Calculate cost of minimum requirements
    min_cost = 0
    for node in path_set:
        cost_per_unit = float(node_cost.get(node, 1))
        min_cost += min_req[node] * cost_per_unit
    
    if min_cost > budget:
        # Can't meet minimum requirements - do best effort
        allocation = {}
        remaining = budget
        # Prioritize nodes with tasks
        nodes_with_tasks = sorted(min_req.keys(), key=lambda n: -min_req[n])
        for node in nodes_with_tasks:
            cost_per_unit = float(node_cost.get(node, 1))
            max_units = int(remaining / cost_per_unit) if cost_per_unit > 0 else 0
            units = min(min_req[node], max_units)
            if units > 0:
                allocation[node] = units
                remaining -= units * cost_per_unit
        return allocation
    
    # Start with minimum requirements
    allocation = {node: min_req[node] for node in path_set if min_req[node] > 0}
    spent = min_cost
    remaining = budget - spent
    
    # Greedy allocation of remaining budget based on marginal utility
    # Build list of (marginal_utility, node, unit_index) for unallocated units
    options = []
    for node in path_set:
        util_list = utility.get(node, [])
        cost_per_unit = float(node_cost.get(node, 1))
        if cost_per_unit <= 0:
            continue
        current_units = allocation.get(node, 0)
        for i in range(current_units, len(util_list)):
            mu = float(util_list[i])
            options.append((-mu, cost_per_unit, node, i + 1))  # i+1 is unit number
    
    # Sort by best marginal utility per cost
    options.sort(key=lambda x: (x[0] / x[1] if x[1] > 0 else float('inf')))
    
    for neg_mu, cost_per_unit, node, unit_num in options:
        if cost_per_unit <= remaining:
            if node not in allocation:
                allocation[node] = 0
            allocation[node] = unit_num
            remaining -= cost_per_unit
    
    return allocation


def solve_stage3(tasks, path, allocation):
    """
    Stage 3: Schedule tasks to minimize makespan.
    Uses list scheduling with capacity constraints and dependencies.
    """
    if not path:
        return []
    
    path_set = set(path)
    operations = tasks.get("operations", [])
    parallelism_limit = tasks.get("parallelism_limit", float('inf'))
    
    # Filter to tasks on path
    path_ops = [op for op in operations if op.get("node", "") in path_set]
    
    if not path_ops:
        return []
    
    ops_by_id = {op["id"]: op for op in path_ops}
    all_task_ids = set(ops_by_id.keys())
    
    # Build dependency graph
    children = defaultdict(list)
    indegree = {tid: 0 for tid in all_task_ids}
    for op in path_ops:
        tid = op["id"]
        for dep in op.get("deps", []):
            if dep in all_task_ids:
                children[dep].append(tid)
                indegree[tid] += 1
    
    # Track capacity usage
    usage = defaultdict(int)
    
    # Ready queue (tasks with no pending dependencies)
    ready = [tid for tid in all_task_ids if indegree[tid] == 0]
    
    # Running tasks: (end_time, task_id)
    running = []
    
    schedule = []
    end_times = {}
    time = 0
    
    def can_start(op):
        node = op["node"]
        req = int(op.get("requires", 0))
        cap = allocation.get(node, 0)
        if usage[node] + req > cap:
            return False
        if len(running) >= parallelism_limit:
            return False
        return True
    
    while ready or running:
        # Sort ready tasks by longest duration first (for better scheduling)
        ready.sort(key=lambda tid: (-float(ops_by_id[tid].get("duration", 0)), tid))
        
        started_any = False
        still_ready = []
        
        for tid in ready:
            op = ops_by_id[tid]
            if can_start(op):
                # Start this task
                node = op["node"]
                req = int(op.get("requires", 0))
                duration = float(op.get("duration", 0))
                
                usage[node] += req
                end_time = time + duration
                heapq.heappush(running, (end_time, tid))
                schedule.append({"id": tid, "start": time})
                end_times[tid] = end_time
                started_any = True
            else:
                still_ready.append(tid)
        
        ready = still_ready
        
        if not started_any:
            if not running:
                # Deadlock - can't schedule remaining tasks
                break
            
            # Advance time to next task completion
            next_end, finished_tid = heapq.heappop(running)
            time = next_end
            
            # Release capacity
            op = ops_by_id[finished_tid]
            node = op["node"]
            req = int(op.get("requires", 0))
            usage[node] -= req
            
            # Add children to ready queue
            for child in children[finished_tid]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
            
            # Also process any other tasks finishing at the same time
            while running and abs(running[0][0] - time) < 1e-6:
                _, tid2 = heapq.heappop(running)
                op2 = ops_by_id[tid2]
                usage[op2["node"]] -= int(op2.get("requires", 0))
                for child in children[tid2]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        ready.append(child)
    
    return schedule


def solve(input_data):
    """
    Solve all three stages of the Multi-Stage Optimization problem.
    """
    # Stage 1: Find shortest path
    path, path_cost = solve_stage1(input_data["graph"])
    
    # Stage 2: Allocate resources on path
    tasks_ops = input_data.get("tasks", {}).get("operations", [])
    allocation = solve_stage2(input_data.get("resources", {}), path, tasks_ops)
    
    # Stage 3: Schedule tasks
    schedule = solve_stage3(input_data.get("tasks", {}), path, allocation)
    
    return {
        "path": path,
        "allocation": allocation,
        "schedule": schedule
    }


if __name__ == "__main__":
    input_data = json.load(sys.stdin)
    solution = solve(input_data)
    print(json.dumps(solution))
