#!/usr/bin/env python3
"""
Multi-Stage Optimization Solver - Opus 4.5 (Claude Code)

Stage 1: Dijkstra shortest path avoiding forbidden nodes
Stage 2: Knapsack DP for resource allocation (maximize utility)
Stage 3: List scheduling with precedence and capacity (minimize makespan)
"""
import json
import sys
import heapq
from collections import defaultdict

def solve(data):
    # Parse input
    graph = data["graph"]
    nodes = set(graph["nodes"])
    edges = graph["edges"]
    source = graph["source"]
    sink = graph["sink"]
    forbidden = set(graph.get("forbidden", []))
    
    resources = data.get("resources", {})
    budget = resources.get("budget", 0)
    node_cost = resources.get("node_cost", {})
    utility = resources.get("utility", {})
    
    tasks = data.get("tasks", {})
    operations = tasks.get("operations", [])
    parallelism_limit = tasks.get("parallelism_limit", None)
    
    # Build adjacency list
    adj = defaultdict(list)
    for e in edges:
        u, v, w = e["from"], e["to"], float(e["weight"])
        adj[u].append((v, w))
    
    # Stage 1: Dijkstra avoiding forbidden nodes
    path = dijkstra(source, sink, adj, forbidden)
    if not path:
        path = [source, sink] if source != sink else [source]
    
    path_set = set(path)
    
    # Stage 2: Knapsack allocation for nodes on path
    allocation = knapsack_allocation(path, budget, node_cost, utility)
    
    # Stage 3: Schedule tasks on path
    path_ops = [op for op in operations if op.get("node") in path_set]
    schedule = schedule_tasks(path_ops, allocation, parallelism_limit)
    
    return {
        "path": path,
        "allocation": allocation,
        "schedule": schedule
    }

def dijkstra(source, sink, adj, forbidden):
    """Dijkstra's algorithm avoiding forbidden nodes."""
    if source in forbidden or sink in forbidden:
        return []
    
    dist = {source: 0.0}
    prev = {}
    heap = [(0.0, source)]
    
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float('inf')):
            continue
        if u == sink:
            break
        for v, w in adj.get(u, []):
            if v in forbidden:
                continue
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    
    if sink not in dist:
        return []
    
    # Reconstruct path
    path = []
    cur = sink
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path

def knapsack_allocation(path, budget, node_cost, utility):
    """Knapsack-style DP to maximize utility under budget constraint."""
    if budget <= 0:
        return {n: 0 for n in path if n in node_cost}
    
    B = int(budget)
    
    # Items: (node, cost_per_unit, utility_list)
    items = []
    free_alloc = {}  # nodes with zero cost
    
    for node in path:
        if node not in node_cost:
            continue
        cost = node_cost[node]
        util_list = utility.get(node, [])
        if cost <= 0:
            # Free allocation - take all positive utilities
            best_units = 0
            for i, u in enumerate(util_list):
                if u > 0:
                    best_units = i + 1
                else:
                    break
            if util_list:
                best_units = len([u for u in util_list if u > 0])
            free_alloc[node] = best_units if best_units > 0 else 0
        else:
            items.append((node, int(cost), util_list))
    
    # DP over items
    # dp[b] = (total_utility, allocation_dict)
    dp = [(0.0, {})]
    for _ in range(B):
        dp.append((0.0, {}))
    
    for node, cost, util_list in items:
        if cost <= 0:
            continue
        max_units = min(B // cost, len(util_list)) if util_list else 0
        
        # Compute prefix utilities
        prefix_utils = [0.0]
        accum = 0.0
        for i in range(max_units):
            accum += util_list[i] if i < len(util_list) else 0
            prefix_utils.append(accum)
        
        new_dp = list(dp)
        for b in range(B + 1):
            if dp[b][0] < 0:
                continue
            for units in range(len(prefix_utils)):
                cost_here = units * cost
                if b + cost_here > B:
                    break
                candidate = dp[b][0] + prefix_utils[units]
                if candidate > new_dp[b + cost_here][0]:
                    new_alloc = dict(dp[b][1])
                    if units > 0:
                        new_alloc[node] = units
                    new_dp[b + cost_here] = (candidate, new_alloc)
        dp = new_dp
    
    # Find best
    best_util, best_alloc = max(dp, key=lambda x: x[0])
    
    # Add free allocations
    result = dict(best_alloc)
    result.update(free_alloc)
    
    # Ensure all path nodes with costs appear (as 0 if not allocated)
    for node in path:
        if node in node_cost and node not in result:
            result[node] = 0
    
    return result

def schedule_tasks(operations, allocation, parallelism_limit):
    """List scheduling to minimize makespan."""
    if not operations:
        return []
    
    ops_by_id = {op["id"]: op for op in operations}
    
    # Build dependency graph
    indeg = defaultdict(int)
    children = defaultdict(list)
    for op in operations:
        tid = op["id"]
        for dep in op.get("deps", []):
            if dep in ops_by_id:
                indeg[tid] += 1
                children[dep].append(tid)
    
    # Ready queue (tasks with no unmet dependencies)
    ready = []
    for op in operations:
        tid = op["id"]
        if indeg[tid] == 0:
            # Priority: larger duration first (longest-first heuristic)
            heapq.heappush(ready, (-float(op.get("duration", 0)), tid))
    
    time = 0.0
    running = []  # (end_time, task_id)
    usage = defaultdict(int)  # per-node resource usage
    start_times = {}
    
    while ready or running:
        # Try to start tasks
        started = False
        new_ready = []
        
        temp_ready = []
        while ready:
            item = heapq.heappop(ready)
            temp_ready.append(item)
        
        for neg_dur, tid in temp_ready:
            op = ops_by_id[tid]
            node = op["node"]
            req = int(op.get("requires", 0))
            cap = allocation.get(node, 0)
            
            can_start = True
            if usage[node] + req > cap:
                can_start = False
            if parallelism_limit is not None and len(running) >= parallelism_limit:
                can_start = False
            
            if can_start:
                started = True
                start_times[tid] = time
                usage[node] += req
                duration = float(op.get("duration", 0))
                heapq.heappush(running, (time + duration, tid))
            else:
                new_ready.append((neg_dur, tid))
        
        for item in new_ready:
            heapq.heappush(ready, item)
        
        if not started:
            if not running:
                # Deadlock - tasks cannot run due to insufficient capacity
                # Just assign sequential times
                remaining = [tid for _, tid in sorted(new_ready)]
                t = time
                for tid in remaining:
                    start_times[tid] = t
                    t += float(ops_by_id[tid].get("duration", 0))
                break
            
            # Advance time to next completion
            end_time, finished_tid = heapq.heappop(running)
            time = end_time
            
            op = ops_by_id[finished_tid]
            node = op["node"]
            req = int(op.get("requires", 0))
            usage[node] -= req
            
            # Release children
            for child in children[finished_tid]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    child_op = ops_by_id[child]
                    heapq.heappush(ready, (-float(child_op.get("duration", 0)), child))
            
            # Also release other tasks finishing at same time
            while running and abs(running[0][0] - time) < 1e-9:
                et, ft = heapq.heappop(running)
                fop = ops_by_id[ft]
                fnode = fop["node"]
                freq = int(fop.get("requires", 0))
                usage[fnode] -= freq
                for child in children[ft]:
                    indeg[child] -= 1
                    if indeg[child] == 0:
                        child_op = ops_by_id[child]
                        heapq.heappush(ready, (-float(child_op.get("duration", 0)), child))
    
    # Build schedule
    schedule = [{"id": tid, "start": start_times[tid]} for tid in start_times]
    schedule.sort(key=lambda x: (x["start"], x["id"]))
    
    return schedule

def main():
    data = json.load(sys.stdin)
    result = solve(data)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
