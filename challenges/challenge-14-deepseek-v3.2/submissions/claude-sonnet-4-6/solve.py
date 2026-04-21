import json
import sys
import heapq
from collections import defaultdict
import math

EPS = 1e-9


def dijkstra(source, sink, adj, forbidden):
    if source in forbidden or sink in forbidden:
        return float('inf'), []
    dist = defaultdict(lambda: float('inf'))
    prev = {}
    dist[source] = 0.0
    heap = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u] + EPS:
            continue
        if u == sink:
            break
        for v, w in adj[u]:
            if v in forbidden:
                continue
            nd = d + w
            if nd + EPS < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    if dist[sink] == float('inf'):
        return float('inf'), []
    path = []
    cur = sink
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return dist[sink], path


def solve_stage2_with_minimums(path, budget, node_cost, utilities, min_alloc):
    """
    Group knapsack with lower bounds.
    min_alloc[node] = minimum units to allocate (for Stage 3 validity).
    """
    if budget < -EPS:
        return {}
    
    # Compute mandatory cost
    mandatory_cost = 0
    for node in path:
        m = min_alloc.get(node, 0)
        if m > 0:
            c = float(node_cost.get(node, 0))
            if c > EPS:
                mandatory_cost += m * int(round(c))
    
    if mandatory_cost > budget + EPS:
        # Can't afford minimums - fall back to pure optimization (Stage 3 invalid)
        min_alloc_used = {}
    else:
        min_alloc_used = min_alloc
        budget = budget - mandatory_cost

    # Budget remaining after mandatory allocations
    if abs(budget - round(budget)) < EPS:
        B = int(round(budget))
    else:
        B = int(math.floor(budget + EPS))
    
    if B < 0:
        B = 0

    # Build group knapsack: for each path node, options are number of EXTRA units above min
    # (plus mandatory ones as base)
    groups = []  # (node, cost_int, util_list starting from min_alloc)
    
    for node in path:
        cost_raw = node_cost.get(node)
        if cost_raw is None:
            continue
        cost_f = float(cost_raw)
        base = min_alloc_used.get(node, 0)
        full_util_list = [float(u) for u in utilities.get(node, [])]
        
        if cost_f < EPS:
            # Free node - take all remaining utils above base
            free_utils = full_util_list[base:] if base < len(full_util_list) else []
            groups.append((node, 0, free_utils, base))
            continue
        
        cost_int = max(1, int(round(cost_f)))
        # Utils starting from base (i.e., 1st extra unit, 2nd extra unit, ...)
        extra_utils = full_util_list[base:] if base < len(full_util_list) else []
        groups.append((node, cost_int, extra_utils, base))
    
    # DP: dp[b] = max extra utility with extra budget b
    dp = [-1.0] * (B + 1)
    dp[0] = 0.0
    # For reconstruction
    choice = {}  # (g_idx, b_after) -> (b_before, extra_units)
    
    for g_idx, (node, cost_int, extra_utils, base) in enumerate(groups):
        if cost_int == 0:
            # Free node: always take all positive marginal utils
            free_util = sum(u for u in extra_utils if u > 0)
            new_dp = list(dp)
            for b in range(B + 1):
                if dp[b] >= -EPS:
                    if dp[b] + free_util > new_dp[b] + EPS:
                        new_dp[b] = dp[b] + free_util
                        choice[(g_idx, b)] = (b, len([u for u in extra_utils if u > 0]))
            dp = new_dp
            continue
        
        # Options: 0, 1, ..., max_extra units
        max_extra = B // cost_int
        # Compute prefix utilities (only if they add value)
        prefix_utils = [0.0]  # 0 extra units
        accum = 0.0
        for k in range(min(max_extra, len(extra_utils))):
            accum += extra_utils[k]
            prefix_utils.append(accum)
        
        new_dp = list(dp)
        for b in range(B + 1):
            if dp[b] < -EPS:
                continue
            for extra, util_val in enumerate(prefix_utils):
                cost_here = extra * cost_int
                if b + cost_here > B:
                    break
                candidate = dp[b] + util_val
                new_b = b + cost_here
                if candidate > new_dp[new_b] + EPS:
                    new_dp[new_b] = candidate
                    choice[(g_idx, new_b)] = (b, extra)
        dp = new_dp
    
    # Find best
    best_b = max(range(B + 1), key=lambda x: dp[x] if dp[x] >= -EPS else -float('inf'))
    
    # Backtrack
    allocation = {}
    # Start with mandatory
    for node, m in min_alloc_used.items():
        if m > 0:
            allocation[node] = m
    
    curr_b = best_b
    for g_idx in range(len(groups) - 1, -1, -1):
        node, cost_int, extra_utils, base = groups[g_idx]
        if (g_idx, curr_b) in choice:
            prev_b, extra = choice[(g_idx, curr_b)]
            if extra > 0:
                allocation[node] = allocation.get(node, 0) + extra
            curr_b = prev_b
    
    return allocation


def compute_critical_path(ops_by_id, children):
    """Compute longest path length from each task to completion."""
    memo = {}

    def lp(tid):
        if tid in memo:
            return memo[tid]
        op = ops_by_id[tid]
        duration = float(op.get('duration', 0))
        result = duration
        for child in children.get(tid, []):
            result = max(result, duration + lp(child))
        memo[tid] = result
        return result

    for tid in ops_by_id:
        lp(tid)
    return memo


def solve_stage3(path_ops, allocation, parallel_limit):
    """List scheduling with capacity and precedence constraints."""
    if not path_ops:
        return []

    ops_by_id = {op['id']: op for op in path_ops}
    children = defaultdict(list)
    indegree = defaultdict(int)

    for op in path_ops:
        tid = op['id']
        for dep in op.get('deps', []):
            if dep in ops_by_id:
                children[dep].append(tid)
                indegree[tid] += 1

    cp_length = compute_critical_path(ops_by_id, children)
    
    # Topological order for ASAP analysis
    ind_copy = dict(indegree)
    topo_order = []
    queue = sorted([tid for tid in ops_by_id if ind_copy.get(tid, 0) == 0])
    heapq.heapify(queue)
    while queue:
        tid = heapq.heappop(queue)
        topo_order.append(tid)
        for child in children[tid]:
            ind_copy[child] -= 1
            if ind_copy[child] == 0:
                heapq.heappush(queue, child)

    # Simulation-based list scheduling
    schedule = {}
    end_times = {}
    running = []  # heap of (end_time, tid)
    node_usage = defaultdict(int)
    running_count = 0
    completed = set()
    
    p_limit = parallel_limit if parallel_limit is not None else float('inf')
    
    # Initially ready tasks
    ready = []
    for tid in ops_by_id:
        if indegree.get(tid, 0) == 0:
            heapq.heappush(ready, (-cp_length[tid], tid))
    
    current_time = 0.0
    deferred = []  # tasks ready but couldn't run due to capacity
    
    total_tasks = len(path_ops)
    
    while len(completed) < total_tasks:
        # Merge ready and deferred, re-sort by priority
        all_ready = list(ready) + deferred
        all_ready.sort()
        ready = []
        deferred = []
        
        scheduled_any = False
        for priority, tid in all_ready:
            op = ops_by_id[tid]
            node = op['node']
            req = int(op.get('requires', 0))
            alloc = allocation.get(node, 0)
            
            # Check all deps completed
            if any(dep in ops_by_id and dep not in completed 
                   for dep in op.get('deps', [])):
                deferred.append((priority, tid))
                continue
            
            if (node_usage[node] + req <= alloc and
                    running_count < p_limit):
                schedule[tid] = current_time
                end_time = current_time + float(op.get('duration', 0))
                end_times[tid] = end_time
                heapq.heappush(running, (end_time, tid))
                node_usage[node] += req
                running_count += 1
                scheduled_any = True
            else:
                deferred.append((priority, tid))
        
        if not running:
            break  # deadlock
        
        # Advance to next completion
        next_end, finished_tid = heapq.heappop(running)
        current_time = next_end
        running_count -= 1
        
        # Release all tasks finishing at this time
        finished_batch = [finished_tid]
        while running and abs(running[0][0] - current_time) < EPS:
            _, tid2 = heapq.heappop(running)
            finished_batch.append(tid2)
            running_count -= 1
        
        for tid in finished_batch:
            op = ops_by_id[tid]
            node = op['node']
            req = int(op.get('requires', 0))
            node_usage[node] -= req
            completed.add(tid)
            for child in children[tid]:
                # Check if child is now ready
                child_deps_done = all(dep not in ops_by_id or dep in completed
                                     for dep in ops_by_id[child].get('deps', []))
                if child_deps_done:
                    # Avoid duplicates
                    already = any(t == child for _, t in deferred) or any(t == child for _, t in ready)
                    if not already:
                        heapq.heappush(ready, (-cp_length[child], child))
    
    return [{"id": tid, "start": schedule[tid]} for tid in schedule]


def solve():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"path": [], "allocation": {}, "schedule": []}))
        return

    # --- Stage 1: Shortest Path ---
    graph = input_data['graph']
    nodes = set(graph['nodes'])
    edges_list = graph['edges']
    source = graph['source']
    sink = graph['sink']
    forbidden = set(graph.get('forbidden', []))

    adj = defaultdict(list)
    for e in edges_list:
        adj[e['from']].append((e['to'], float(e['weight'])))

    _, path = dijkstra(source, sink, adj, forbidden)

    if not path:
        print(json.dumps({"path": [], "allocation": {}, "schedule": []}))
        return

    # --- Stage 2: Resource Allocation ---
    resources = input_data.get('resources', {})
    budget = float(resources.get('budget', 0))
    node_cost = {k: float(v) for k, v in resources.get('node_cost', {}).items()}
    utilities = {k: [float(x) for x in v] for k, v in resources.get('utility', {}).items()}

    # Determine minimum allocation per node for Stage 3 validity
    tasks_data = input_data.get('tasks', {})
    all_ops = tasks_data.get('operations', [])
    path_set = set(path)
    path_ops = [op for op in all_ops if op.get('node') in path_set]

    min_alloc = defaultdict(int)
    for op in path_ops:
        node = op['node']
        req = int(op.get('requires', 0))
        min_alloc[node] = max(min_alloc[node], req)

    allocation = solve_stage2_with_minimums(path, budget, node_cost, utilities, dict(min_alloc))

    # --- Stage 3: Scheduling ---
    parallel_limit = tasks_data.get('parallelism_limit')
    if parallel_limit is not None:
        try:
            parallel_limit = int(round(float(parallel_limit)))
        except Exception:
            parallel_limit = None

    schedule = solve_stage3(path_ops, allocation, parallel_limit)

    result = {
        "path": path,
        "allocation": allocation,
        "schedule": schedule
    }
    print(json.dumps(result))


if __name__ == "__main__":
    solve()
