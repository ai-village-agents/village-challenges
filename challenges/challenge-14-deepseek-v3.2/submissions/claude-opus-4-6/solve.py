#!/usr/bin/env python3
"""
Multi-Stage Optimization Solver
================================
Author: Claude Opus 4.6

Stage 1: Dijkstra's shortest path with forbidden node filtering
Stage 2: Knapsack DP for optimal resource allocation (task-aware)
Stage 3: List scheduling with capacity/precedence/parallelism constraints
"""
import json
import sys
import heapq
import math
from collections import defaultdict, deque


def solve_stage1(graph):
    """Find minimum-cost path from source to sink avoiding forbidden nodes."""
    nodes = set(graph["nodes"])
    source = graph["source"]
    sink = graph["sink"]
    forbidden = set(graph.get("forbidden", []))
    
    adj = defaultdict(list)
    for e in graph["edges"]:
        adj[e["from"]].append((e["to"], float(e["weight"])))
    
    if source in forbidden or sink in forbidden:
        return [source, sink]
    
    dist = defaultdict(lambda: math.inf)
    prev = {}
    dist[source] = 0.0
    heap = [(0.0, source)]
    
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u] + 1e-9:
            continue
        if u == sink:
            break
        for v, w in adj[u]:
            if v in forbidden:
                continue
            nd = d + w
            if nd + 1e-9 < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    
    if dist[sink] == math.inf:
        return [source]
    
    path = deque()
    cur = sink
    while cur is not None:
        path.appendleft(cur)
        cur = prev.get(cur)
    return list(path)


def solve_stage2(path, resources, tasks):
    """
    Optimal resource allocation via knapsack DP.
    Task-aware: ensures minimum allocation for task feasibility.
    """
    budget = float(resources.get("budget", 0))
    node_cost = resources.get("node_cost", {})
    utilities = resources.get("utility", {})
    operations = tasks.get("operations", [])
    
    B = int(round(budget))
    path_set = set(path)
    
    # Determine minimum required allocation per node for tasks
    min_required = defaultdict(int)
    for op in operations:
        node = op.get("node")
        if node in path_set:
            req = int(op.get("requires", 0))
            min_required[node] = max(min_required[node], req)
    
    # Calculate cost of minimum required allocations
    min_cost = 0
    base_allocation = {}
    for node, min_units in min_required.items():
        c = float(node_cost.get(node, 0))
        if c > 0:
            min_cost += int(round(c)) * min_units
        base_allocation[node] = min_units
    
    # If minimum requirements exceed budget, just allocate what we can
    # prioritizing nodes with tasks (by utility)
    if min_cost > B:
        # Greedy: allocate to nodes with highest task requirements first
        allocation = {}
        remaining_budget = B
        sorted_nodes = sorted(min_required.keys(), 
                            key=lambda n: -min_required[n])
        for node in sorted_nodes:
            c = int(round(float(node_cost.get(node, 0))))
            if c <= 0:
                allocation[node] = min_required[node]
                continue
            units = min(min_required[node], remaining_budget // c)
            if units > 0:
                allocation[node] = units
                remaining_budget -= units * c
        return allocation
    
    # Budget available after minimum requirements
    remaining_B = B - min_cost
    
    # Compute base utility from minimum allocations
    base_utility = 0.0
    for node, units in base_allocation.items():
        util_list = [float(u) for u in utilities.get(node, [])]
        base_utility += sum(util_list[:units])
    
    # DP for remaining budget: allocate extra units for utility
    dp = [0.0] * (remaining_B + 1)
    alloc_trace = [{}  for _ in range(remaining_B + 1)]
    
    for node in path:
        cost_raw = node_cost.get(node)
        util_list = [float(u) for u in utilities.get(node, [])]
        
        if cost_raw is None:
            continue
        
        cost = int(round(float(cost_raw)))
        base_units = base_allocation.get(node, 0)
        
        # Remaining marginal utilities after base allocation
        remaining_utils = util_list[base_units:]
        
        if cost <= 0:
            # Free: take all positive remaining utilities
            bonus = sum(u for u in remaining_utils if u > 0)
            extra_units = len([u for u in remaining_utils if u > 0])
            if bonus > 0:
                new_dp = dp[:]
                new_trace = [dict(a) for a in alloc_trace]
                for b in range(remaining_B + 1):
                    candidate = dp[b] + bonus
                    if candidate > new_dp[b]:
                        new_dp[b] = candidate
                        new_trace[b] = dict(alloc_trace[b])
                        new_trace[b][node] = extra_units
                dp = new_dp
                alloc_trace = new_trace
            continue
        
        max_extra = remaining_B // cost
        prefix_utils = [0.0]
        accum = 0.0
        for k in range(1, max_extra + 1):
            if k <= len(remaining_utils):
                accum += remaining_utils[k - 1]
            prefix_utils.append(accum)
        
        new_dp = dp[:]
        new_trace = [dict(a) for a in alloc_trace]
        
        for b in range(remaining_B + 1):
            for units in range(len(prefix_utils)):
                cost_here = units * cost
                if b + cost_here > remaining_B:
                    break
                candidate = dp[b] + prefix_utils[units]
                if candidate > new_dp[b + cost_here] + 1e-9:
                    new_dp[b + cost_here] = candidate
                    new_trace[b + cost_here] = dict(alloc_trace[b])
                    if units > 0:
                        new_trace[b + cost_here][node] = units
        
        dp = new_dp
        alloc_trace = new_trace
    
    # Find best
    best_b = 0
    for b in range(remaining_B + 1):
        if dp[b] > dp[best_b]:
            best_b = b
    
    # Combine base + extra
    allocation = dict(base_allocation)
    extra = alloc_trace[best_b]
    for node, extra_units in extra.items():
        allocation[node] = allocation.get(node, 0) + extra_units
    
    return allocation


def solve_stage3(path, allocation, tasks):
    """Schedule tasks using list scheduling (longest-path priority)."""
    operations = tasks.get("operations", [])
    parallel_limit = tasks.get("parallelism_limit", None)
    if parallel_limit is not None:
        parallel_limit = int(parallel_limit)
    
    path_set = set(path)
    ops_on_path = [op for op in operations if op.get("node") in path_set]
    
    if not ops_on_path:
        return []
    
    ops_by_id = {op["id"]: op for op in ops_on_path}
    
    # Build dependency graph
    indeg = defaultdict(int)
    children = defaultdict(list)
    for op in ops_on_path:
        tid = op["id"]
        for dep in op.get("deps", []):
            if dep in ops_by_id:
                indeg[tid] += 1
                children[dep].append(tid)
    
    # Compute longest path from each task (critical path heuristic)
    longest_path = {}
    def compute_longest(tid):
        if tid in longest_path:
            return longest_path[tid]
        op = ops_by_id[tid]
        dur = float(op.get("duration", 0))
        max_child = 0
        for child in children[tid]:
            max_child = max(max_child, compute_longest(child))
        longest_path[tid] = dur + max_child
        return longest_path[tid]
    
    for tid in ops_by_id:
        compute_longest(tid)
    
    # List scheduling
    ready = []
    for op in ops_on_path:
        tid = op["id"]
        if indeg[tid] == 0:
            heapq.heappush(ready, (-longest_path[tid], tid))
    
    usage = defaultdict(int)
    running = []  # (end_time, tid)
    running_count = 0
    start_times = {}
    time = 0.0
    scheduled = set()
    
    def can_start(op):
        node = op["node"]
        req = int(op.get("requires", 0))
        alloc = allocation.get(node, 0)
        if alloc < req:
            return False
        if usage[node] + req > alloc:
            return False
        if parallel_limit is not None and running_count >= parallel_limit:
            return False
        return True
    
    def finish_tasks_at_time():
        nonlocal time, running_count
        while running and abs(running[0][0] - time) < 1e-9:
            et, ft = heapq.heappop(running)
            running_count -= 1
            fop = ops_by_id[ft]
            fn = fop["node"]
            freq = int(fop.get("requires", 0))
            usage[fn] -= freq
            for child in children[ft]:
                if child in ops_by_id:
                    indeg[child] -= 1
                    if indeg[child] == 0 and child not in scheduled:
                        heapq.heappush(ready, (-longest_path[child], child))
    
    max_iters = len(ops_on_path) * len(ops_on_path) + 100
    iters = 0
    
    while (ready or running) and iters < max_iters:
        iters += 1
        
        # Try to start as many ready tasks as possible
        started_any = False
        not_startable = []
        
        temp_ready = []
        while ready:
            temp_ready.append(heapq.heappop(ready))
        
        for priority, tid in temp_ready:
            if tid in scheduled:
                continue
            op = ops_by_id[tid]
            if can_start(op):
                started_any = True
                scheduled.add(tid)
                node = op["node"]
                req = int(op.get("requires", 0))
                usage[node] += req
                running_count += 1
                start_times[tid] = time
                end_time = time + float(op.get("duration", 0))
                heapq.heappush(running, (end_time, tid))
            else:
                not_startable.append((priority, tid))
        
        for item in not_startable:
            heapq.heappush(ready, item)
        
        if not running:
            break
        
        # Advance to next finish event
        next_time = running[0][0]
        time = next_time
        finish_tasks_at_time()
    
    # Handle any unscheduled tasks (can't be scheduled due to capacity)
    for op in ops_on_path:
        tid = op["id"]
        if tid not in start_times:
            start_times[tid] = time
    
    return [{"id": op["id"], "start": start_times[op["id"]]} for op in ops_on_path if op["id"] in start_times]


def solve(input_data):
    """Main solver."""
    graph = input_data["graph"]
    resources = input_data.get("resources", {})
    tasks = input_data.get("tasks", {})
    
    path = solve_stage1(graph)
    allocation = solve_stage2(path, resources, tasks)
    schedule = solve_stage3(path, allocation, tasks)
    
    return {
        "path": path,
        "allocation": allocation,
        "schedule": schedule
    }


if __name__ == "__main__":
    input_data = json.load(sys.stdin)
    result = solve(input_data)
    json.dump(result, sys.stdout)
