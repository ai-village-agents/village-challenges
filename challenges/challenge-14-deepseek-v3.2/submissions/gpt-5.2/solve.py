#!/usr/bin/env python3
"""C14 Multi-Stage Optimization Tournament — GPT-5.2

Reads one JSON instance from stdin and writes a JSON solution to stdout:
  {"path": [...], "allocation": {...}, "schedule": [{"id":..., "start":...}, ...]}

Strategy:
- Stage 1: Dijkstra shortest path with forbidden-node filtering.
- Stage 2: Group-knapsack DP on nodes in the chosen path to maximize utility
  under budget, with a mandatory minimum allocation per node sufficient for
  Stage 3 feasibility (max task `requires` on that node).
- Stage 3: Deterministic list scheduling with precedence + per-node capacity +
  optional global parallelism cap.

Implementation is stdlib-only and deterministic.
"""

from __future__ import annotations

import json
import math
import sys
import heapq
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

EPS = 1e-6


def is_int_like(x: Any) -> bool:
    if isinstance(x, bool):
        return False
    try:
        return abs(float(x) - round(float(x))) < EPS
    except (TypeError, ValueError):
        return False


def build_edge_lookup(edges: List[Dict[str, Any]]) -> Tuple[Dict[Tuple[str, str], float], Dict[str, List[Tuple[str, float]]]]:
    edge_lookup: Dict[Tuple[str, str], float] = {}
    adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for e in edges:
        u = e["from"]
        v = e["to"]
        w = float(e["weight"])
        if (u, v) not in edge_lookup or w < edge_lookup[(u, v)]:
            edge_lookup[(u, v)] = w
        adj[u].append((v, w))
    return edge_lookup, adj


def dijkstra_path(source: str, sink: str, nodes: set, adj: Dict[str, List[Tuple[str, float]]], forbidden: set) -> List[str]:
    if source in forbidden or sink in forbidden:
        return []
    dist: Dict[str, float] = defaultdict(lambda: math.inf)
    prev: Dict[str, Optional[str]] = {}
    dist[source] = 0.0
    heap: List[Tuple[float, str]] = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u] + EPS:
            continue
        if u == sink:
            break
        for v, w in adj.get(u, []):
            if v in forbidden:
                continue
            nd = d + w
            if nd + EPS < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    if dist[sink] == math.inf:
        return []
    path: deque[str] = deque()
    cur: Optional[str] = sink
    while cur is not None:
        path.appendleft(cur)
        cur = prev.get(cur)
    return list(path)


def marginal_utility(units: int, util_list: List[float]) -> float:
    take = min(units, len(util_list))
    return float(sum(util_list[:take]))


def total_utility(allocation: Dict[str, int], utilities: Dict[str, List[float]]) -> float:
    return float(sum(marginal_utility(units, utilities.get(node, [])) for node, units in allocation.items()))


def compute_mandatory_requirements(path: List[str], operations: List[Dict[str, Any]]) -> Dict[str, int]:
    req: Dict[str, int] = defaultdict(int)
    path_set = set(path)
    for op in operations:
        node = op.get("node")
        if node in path_set:
            r = int(op.get("requires", 0))
            if r > req[node]:
                req[node] = r
    # ensure keys exist for all path nodes for simpler handling
    for n in path:
        req.setdefault(n, 0)
    return dict(req)


def budget_int_like(budget: float) -> int:
    if is_int_like(budget):
        return int(round(float(budget)))
    return int(math.floor(float(budget) + EPS))


def choose_allocation(
    path: List[str],
    budget: float,
    node_cost: Dict[str, float],
    utilities: Dict[str, List[float]],
    mandatory: Dict[str, int],
) -> Dict[str, int]:
    """Maximize utility on path under budget, with mandatory minimum units per node.

    For zero-cost nodes, allocate all units with positive marginal utility (plus mandatory).
    """

    # If budget is negative, trivial.
    if budget < -EPS or not path:
        return {}

    B = budget_int_like(budget)

    alloc: Dict[str, int] = {}

    # First, apply mandatory minimums and handle zero-cost nodes.
    mandatory_cost = 0
    for n in path:
        m = int(mandatory.get(n, 0))
        if m < 0:
            m = 0
        if m == 0:
            continue
        if n not in node_cost:
            # Can't allocate to nodes without node_cost (grader would invalidate Stage 2);
            # keep allocation empty for that node.
            return {}
        c = float(node_cost[n])
        if c > EPS:
            if not is_int_like(c):
                c = round(c)
            mandatory_cost += int(round(c)) * m
        # c ~ 0 => no budget impact
        alloc[n] = m

    if mandatory_cost > B:
        # Infeasible within budget.
        return {}

    # For cost ~ 0 nodes: take all positive marginal utilities for free.
    for n in path:
        if n not in node_cost:
            continue
        c = float(node_cost[n])
        if c < EPS:
            # allocate enough units to capture positive marginal utility
            util_list = [float(x) for x in utilities.get(n, [])]
            extra = 0
            for u in util_list:
                if u > 0:
                    extra += 1
                else:
                    break
            alloc[n] = max(alloc.get(n, 0), int(mandatory.get(n, 0)) + extra)

    remaining = B - mandatory_cost

    # Group knapsack over nodes (excluding zero-cost nodes already handled).
    # For each node, options = add k extra units (beyond current alloc baseline) at cost k*cost_int
    groups: List[Tuple[str, List[Tuple[int, float, int]]]] = []
    for n in path:
        if n not in node_cost:
            continue
        c = float(node_cost[n])
        if c < EPS:
            continue
        if not is_int_like(c):
            c = round(c)
        cost_int = int(round(c))
        if cost_int <= 0:
            continue

        base = int(alloc.get(n, 0))
        util_list = [float(x) for x in utilities.get(n, [])]

        options: List[Tuple[int, float, int]] = [(0, 0.0, 0)]  # (extra_cost, extra_utility, extra_units)
        accum = 0.0
        max_add = (remaining // cost_int) if cost_int > 0 else 0
        # additional units beyond utility list add zero utility; no point allocating.
        max_add = min(max_add, max(0, len(util_list) - base))
        for k in range(1, max_add + 1):
            accum += util_list[base + k - 1]
            options.append((k * cost_int, accum, k))
        groups.append((n, options))

    # DP: dp[w] = best util; store predecessor for reconstruction.
    dp = {0: 0.0}
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}  # (g_idx, w)->(prev_w, opt_idx)

    for g_idx, (n, options) in enumerate(groups):
        new_dp: Dict[int, float] = {}
        new_parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for w, val in dp.items():
            for opt_idx, (dcost, dutil, dunits) in enumerate(options):
                nw = w + dcost
                if nw > remaining:
                    continue
                cand = val + dutil
                if cand > new_dp.get(nw, -1e100) + EPS:
                    new_dp[nw] = cand
                    new_parent[(g_idx, nw)] = (w, opt_idx)
        dp = new_dp
        parent.update(new_parent)

    if not dp:
        return alloc

    best_w = max(dp, key=lambda w: (dp[w], -w))

    # Backtrack chosen option per group.
    w = best_w
    for g_idx in range(len(groups) - 1, -1, -1):
        n, options = groups[g_idx]
        prev_w, opt_idx = parent[(g_idx, w)]
        extra_units = options[opt_idx][2]
        if extra_units:
            alloc[n] = int(alloc.get(n, 0) + extra_units)
        w = prev_w

    return alloc


def list_schedule(
    operations: List[Dict[str, Any]],
    allocation: Dict[str, int],
    parallel_limit: Optional[int],
) -> List[Dict[str, Any]]:
    """Produce a feasible schedule (start times) via list scheduling.

    Only operations provided here are scheduled; caller should already filter to ops-on-path.
    """
    if not operations:
        return []

    ops_by_id = {op["id"]: op for op in operations}
    indeg: Dict[str, int] = defaultdict(int)
    children: Dict[str, List[str]] = defaultdict(list)

    for op in operations:
        tid = op["id"]
        for dep in op.get("deps", []):
            if dep in ops_by_id:
                indeg[tid] += 1
                children[dep].append(tid)

    ready: List[str] = [op["id"] for op in operations if indeg[op["id"]] == 0]
    ready.sort()

    time = 0.0
    running: List[Tuple[float, str]] = []  # heap of (end_time, task_id)
    node_usage: Dict[str, int] = defaultdict(int)

    schedule: List[Dict[str, Any]] = []
    started: set[str] = set()

    def can_start(op: Dict[str, Any]) -> bool:
        node = op["node"]
        req = int(op.get("requires", 0))
        if allocation.get(node, 0) < req:
            return False
        if node_usage[node] + req > allocation.get(node, 0) + EPS:
            return False
        if parallel_limit is not None and len(running) >= parallel_limit:
            return False
        return True

    while ready or running:
        started_this_round = False
        # Start as many as possible at current time, greedy by duration desc then id.
        ready_ops = sorted(ready, key=lambda tid: (-float(ops_by_id[tid].get("duration", 0)), tid))
        for tid in ready_ops:
            if tid not in ready:
                continue
            op = ops_by_id[tid]
            if can_start(op):
                started_this_round = True
                ready.remove(tid)
                started.add(tid)
                node = op["node"]
                req = int(op.get("requires", 0))
                dur = float(op.get("duration", 0))
                schedule.append({"id": tid, "start": time})
                node_usage[node] += req
                heapq.heappush(running, (time + dur, tid))

        if not started_this_round:
            if not running:
                break
            # Advance to next completion time and release all finished at that time.
            t_next, tid_done = heapq.heappop(running)
            time = t_next
            op_done = ops_by_id[tid_done]
            node_done = op_done["node"]
            node_usage[node_done] -= int(op_done.get("requires", 0))
            for child in children.get(tid_done, []):
                indeg[child] -= 1
                if indeg[child] == 0:
                    ready.append(child)
            # release others finishing at same time
            while running and abs(running[0][0] - time) < EPS:
                t2, tid2 = heapq.heappop(running)
                op2 = ops_by_id[tid2]
                node2 = op2["node"]
                node_usage[node2] -= int(op2.get("requires", 0))
                for child in children.get(tid2, []):
                    indeg[child] -= 1
                    if indeg[child] == 0:
                        ready.append(child)
            ready.sort()
        else:
            # If we started something, jump to next finish event time (without releasing yet).
            if running:
                time = running[0][0]

    # Ensure deterministic order in output (grader doesn't require, but nice).
    schedule.sort(key=lambda e: (float(e["start"]), str(e["id"])))
    return schedule


def main() -> int:
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        # Must not emit errors to stdout.
        return 0

    graph = input_data.get("graph", {})
    nodes = set(graph.get("nodes", []))
    forbidden = set(graph.get("forbidden", []))
    source = graph.get("source")
    sink = graph.get("sink")
    edges = graph.get("edges", [])

    _, adj = build_edge_lookup(edges)

    path: List[str] = []
    if isinstance(source, str) and isinstance(sink, str) and source in nodes and sink in nodes:
        path = dijkstra_path(source, sink, nodes, adj, forbidden)

    if not path:
        json.dump({"path": [], "allocation": {}, "schedule": []}, sys.stdout)
        sys.stdout.write("\n")
        return 0

    resources = input_data.get("resources", {})
    budget = float(resources.get("budget", 0.0))
    node_cost = {k: float(v) for k, v in resources.get("node_cost", {}).items()}
    utilities = {k: [float(x) for x in v] for k, v in resources.get("utility", {}).items()}

    tasks = input_data.get("tasks", {})
    operations_all = tasks.get("operations", [])

    mandatory = compute_mandatory_requirements(path, operations_all)
    allocation = choose_allocation(path, budget, node_cost, utilities, mandatory)

    # Stage 3: schedule only tasks whose node is on the path.
    path_set = set(path)
    operations = [op for op in operations_all if op.get("node") in path_set]

    parallel_limit = tasks.get("parallelism_limit", None)
    if parallel_limit is not None:
        if is_int_like(parallel_limit):
            parallel_limit = int(round(float(parallel_limit)))
        else:
            parallel_limit = None

    schedule: List[Dict[str, Any]] = []
    if allocation and operations:
        schedule = list_schedule(operations, allocation, parallel_limit)
    elif not operations:
        schedule = []
    else:
        # Allocation infeasible under budget or missing node_cost; output empty schedule.
        schedule = []

    json.dump({"path": path, "allocation": allocation, "schedule": schedule}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
