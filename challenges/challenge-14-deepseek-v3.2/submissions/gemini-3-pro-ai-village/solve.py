import json
import sys
import heapq
from collections import defaultdict

def solve():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
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
        
    def get_shortest_path(src, dst):
        if src in forbidden or dst in forbidden:
            return None
        dist = {node: float('inf') for node in nodes}
        parent = {node: None for node in nodes}
        dist[src] = 0
        pq = [(0, src)]
        
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]: continue
            if u == dst: break
            
            for v, w in adj[u]:
                if v not in forbidden:
                    if dist[u] + w < dist[v]:
                        dist[v] = dist[u] + w
                        parent[v] = u
                        heapq.heappush(pq, (dist[v], v))
                        
        if dist[dst] == float('inf'): return None
        path = []
        curr = dst
        while curr:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]

    path = get_shortest_path(source, sink)
    if not path:
        print(json.dumps({"path": [], "allocation": {}, "schedule": []}))
        return

    # --- Stage 2: Resource Allocation ---
    resources = input_data['resources']
    budget = float(resources['budget'])
    node_costs = {k: float(v) for k,v in resources.get('node_cost', {}).items()}
    utilities = {k: [float(x) for x in v] for k,v in resources.get('utility', {}).items()}
    
    # Identify minimum requirements for Stage 3 validity
    tasks_data = input_data['tasks']
    all_ops = tasks_data.get('operations', [])
    path_set = set(path)
    path_ops = [op for op in all_ops if op['node'] in path_set]
    
    min_reqs = defaultdict(int)
    for op in path_ops:
        min_reqs[op['node']] = max(min_reqs[op['node']], int(op.get('requires', 1)))
        
    # Calculate cost to meet minimums
    mandatory_cost = 0
    current_allocation = defaultdict(int)
    possible_stage3 = True
    
    for node in path:
        req = min_reqs[node]
        cost = node_costs.get(node, 0)
        if mandatory_cost + req * cost > budget:
            possible_stage3 = False
            break
        mandatory_cost += req * cost
        current_allocation[node] = req

    # If we can't meet min reqs, reset and just optimize Stage 2 (ignoring Stage 3)
    if not possible_stage3:
        mandatory_cost = 0
        current_allocation = defaultdict(int)
        # In this mode, min_reqs doesn't matter, we start from 0
        start_units = {node: 0 for node in path}
    else:
        start_units = {node: min_reqs[node] for node in path}

    # Use remaining budget to maximize utility
    # We can treat each additional unit as an item (cost, utility gain)
    # Utility is diminishing? Usually. If not, we should bundle.
    # Assuming diminishing or independent enough for greedy/DP.
    # Let's use a simple greedy approach for the knapsack if items are small relative to budget,
    # or just list all potential next units.
    
    remaining_budget = budget - mandatory_cost
    
    # Potential next units
    # Heap of (-marginal_utility/cost, cost, node, unit_index)
    # Actually, strictly we should use DP if costs vary and budget is tight.
    # But budget is usually small integer in these problems? Or large?
    # Challenge says "budget": 12. Small. DP is fine.
    
    # Items for DP:
    # For each node, subsequent units starting from start_units[node] + 1
    # up to len(utilities[node])
    
    items = []
    for node in path:
        start = start_units[node]
        node_utils = utilities.get(node, [])
        cost = int(node_costs.get(node, 0)) # forcing int for DP
        if cost <= 0: cost = 0 # Handle 0 cost?
        
        for i in range(start, len(node_utils)):
            u_gain = node_utils[i]
            items.append((cost, u_gain, node))

    # Knapsack DP
    # dp[w] = max utility with weight w
    # We need to reconstruct counts.
    # Since items order for a node matters (marginal util), we should process node-by-node (Group Knapsack)?
    # Or if utils are diminishing, greedy by ratio works for fractional, but this is 0/1.
    # Correct is DP.
    # But wait, if I treat (unit 3) as an item, I can't take it unless I took (unit 2).
    # So it IS a Group Knapsack where options are:
    # 0 extra units, 1 extra unit, 2 extra units...
    
    groups = []
    for node in path:
        start = start_units[node]
        node_utils = utilities.get(node, [])
        cost = int(node_costs.get(node, 0))
        
        options = [] # (cost, util, count_increment)
        # Option 0: add nothing
        options.append((0, 0.0, 0))
        
        current_cost = 0
        current_util = 0.0
        for i in range(start, len(node_utils)):
            current_cost += cost
            current_util += node_utils[i]
            options.append((current_cost, current_util, i - start + 1))
        groups.append((node, options))
        
    B = int(remaining_budget)
    # dp[w] = max_util
    # reconstruct: path_choice[group_idx][w] = option_idx
    dp = {0: 0.0}
    path_choice = {}
    
    for g_idx, (node, options) in enumerate(groups):
        new_dp = {}
        for w, val in dp.items():
            for opt_idx, (opt_cost, opt_util, opt_count) in enumerate(options):
                if w + opt_cost <= B:
                    new_w = w + opt_cost
                    new_val = val + opt_util
                    if new_val > new_dp.get(new_w, -1.0):
                        new_dp[new_w] = new_val
                        path_choice[(g_idx, new_w)] = (w, opt_idx) # store prev_w to backtrack
        dp = new_dp
        
    # Find best
    best_w = max(dp, key=dp.get)
    
    # Backtrack
    final_allocation = current_allocation.copy()
    curr_w = best_w
    for g_idx in range(len(groups)-1, -1, -1):
        node, options = groups[g_idx]
        if (g_idx, curr_w) in path_choice:
            prev_w, opt_idx = path_choice[(g_idx, curr_w)]
            count_inc = options[opt_idx][2]
            final_allocation[node] += count_inc
            curr_w = prev_w
            
    # --- Stage 3: Schedule ---
    # Greedy List Scheduling
    # Re-verify we meet requirements (we should if possible_stage3 is True)
    
    schedule = []
    if possible_stage3:
        # Build dependency graph
        op_map = {op['id']: op for op in path_ops}
        adj_tasks = defaultdict(list)
        indegree = {op['id']: 0 for op in path_ops}
        
        for op in path_ops:
            tid = op['id']
            for dep in op.get('deps', []):
                if dep in op_map:
                    adj_tasks[dep].append(tid)
                    indegree[tid] += 1
                    
        # Calculate priorities (Depth / Longest Path to sink)
        memo_depth = {}
        def get_depth(tid):
            if tid in memo_depth: return memo_depth[tid]
            d = 0
            for child in adj_tasks[tid]:
                d = max(d, 1 + get_depth(child))
            memo_depth[tid] = d
            return d
            
        ready = [op['id'] for op in path_ops if indegree[op['id']] == 0]
        
        running = [] # (finish_time, tid, node, req)
        node_usage = defaultdict(int)
        current_time = 0
        completed_count = 0
        total_tasks = len(path_ops)
        
        parallel_limit = tasks_data.get('parallelism_limit')
        if parallel_limit is None: parallel_limit = float('inf')
        
        while completed_count < total_tasks:
            # 1. Release finished tasks
            running.sort() # earliest finish
            while running and running[0][0] <= current_time:
                ft, tid, node, req = heapq.heappop(running)
                node_usage[node] -= req
                completed_count += 1
                for child in adj_tasks[tid]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        ready.append(child)
            
            # 2. Schedule ready tasks
            # Sort by depth desc (CP rule)
            ready.sort(key=lambda t: (-get_depth(t), -op_map[t]['duration']))
            
            # Attempt to schedule
            not_schedulable = []
            while ready:
                tid = ready.pop(0)
                op = op_map[tid]
                node = op['node']
                req = int(op.get('requires', 0))
                
                # Check capacity
                if node_usage[node] + req <= final_allocation.get(node, 0):
                    # Check parallelism
                    if len(running) < parallel_limit:
                        # Schedule
                        schedule.append({"id": tid, "start": current_time})
                        ft = current_time + op['duration']
                        heapq.heappush(running, (ft, tid, node, req))
                        node_usage[node] += req
                        continue
                
                not_schedulable.append(tid)
            
            ready = not_schedulable
            
            # 3. Advance time
            if completed_count < total_tasks:
                if running:
                    # Jump to next event
                    current_time = running[0][0]
                else:
                    # Deadlock? Should not happen if capacity is sufficient
                    break
    
    # Output
    result = {
        "path": path,
        "allocation": final_allocation,
        "schedule": schedule
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    solve()
