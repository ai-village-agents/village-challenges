#!/usr/bin/env python3
"""
Grader for the Multi-Stage Optimization Tournament (challenge-14-deepseek-v3.2).

Features:
- Validates submission output against the original input JSON.
- Computes reference scores for all three stages:
  * Stage 1: shortest valid path via Dijkstra (with forbidden-node filtering).
  * Stage 2: optimal allocation via knapsack-style DP.
  * Stage 3: heuristic minimum makespan via list scheduling with capacities.
- Produces a breakdown (0-100 total) and optionally runs built-in example cases.
"""
from __future__ import annotations

import argparse
import json
import math
import heapq
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

EPS = 1e-6


# ---------------------------
# Utility / Parsing helpers
# ---------------------------
def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def is_int_like(x: Any) -> bool:
    if isinstance(x, bool):
        return False
    try:
        return abs(float(x) - round(float(x))) < EPS
    except (TypeError, ValueError):
        return False


# ---------------------------
# Stage 1: Path validation & scoring
# ---------------------------
def compute_path_cost(path: List[str], edge_lookup: Dict[Tuple[str, str], float]) -> float:
    cost = 0.0
    for i in range(len(path) - 1):
        cost += edge_lookup[(path[i], path[i + 1])]
    return cost


def validate_path(path: Any, nodes: set, edge_lookup: Dict[Tuple[str, str], float], source: str, sink: str, forbidden: set) -> Tuple[bool, Optional[float], str]:
    if not isinstance(path, list) or not path:
        return False, None, "path must be a non-empty list"
    if path[0] != source or path[-1] != sink:
        return False, None, "path must start at source and end at sink"
    for n in path:
        if n not in nodes:
            return False, None, f"node {n} not in graph"
        if n in forbidden:
            return False, None, f"node {n} is forbidden"
    for u, v in zip(path, path[1:]):
        if (u, v) not in edge_lookup:
            return False, None, f"missing edge {u}->{v}"
    return True, compute_path_cost(path, edge_lookup), ""


def dijkstra_shortest_path(source: str, sink: str, adj: Dict[str, List[Tuple[str, float]]], forbidden: set) -> Tuple[float, List[str]]:
    if source in forbidden or sink in forbidden:
        return math.inf, []
    dist: Dict[str, float] = defaultdict(lambda: math.inf)
    prev: Dict[str, Optional[str]] = {}
    dist[source] = 0.0
    heap = [(0.0, source)]
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
        return math.inf, []
    # Reconstruct path
    path: deque[str] = deque()
    cur: Optional[str] = sink
    while cur is not None:
        path.appendleft(cur)
        cur = prev.get(cur)
    return dist[sink], list(path)


def score_stage1(input_data: Dict[str, Any], submission: Dict[str, Any]) -> Dict[str, Any]:
    graph = input_data["graph"]
    nodes = set(graph["nodes"])
    forbidden = set(graph.get("forbidden", []))
    source = graph["source"]
    sink = graph["sink"]
    edge_lookup, adj = build_edge_lookup(graph["edges"])

    sub_path = submission.get("path", [])
    valid, sub_cost, reason = validate_path(sub_path, nodes, edge_lookup, source, sink, forbidden)

    best_cost, best_path = dijkstra_shortest_path(source, sink, adj, forbidden)
    stage_score = 0.0
    if best_cost == math.inf:
        best_cost = None
        best_path = []

    if valid and sub_cost is not None and best_cost is not None:
        if sub_cost <= EPS:
            stage_score = 40.0 if best_cost <= EPS else 0.0
        else:
            stage_score = 40.0 * min(1.0, best_cost / sub_cost)
    elif not valid:
        stage_score = 0.0

    return {
        "score": stage_score,
        "valid": valid,
        "reason": reason if not valid else "",
        "submitted_cost": sub_cost,
        "best_cost": best_cost,
        "best_path": best_path,
    }


# ---------------------------
# Stage 2: Allocation & scoring
# ---------------------------
def compute_allocation_cost(allocation: Dict[str, int], node_cost: Dict[str, Any]) -> float:
    return sum(float(node_cost[n]) * units for n, units in allocation.items())


def marginal_utility(units: int, util_list: List[float]) -> float:
    take = min(units, len(util_list))
    return sum(util_list[:take])


def total_utility(allocation: Dict[str, int], utilities: Dict[str, List[float]]) -> float:
    return sum(marginal_utility(units, utilities.get(node, [])) for node, units in allocation.items())


def validate_allocation(path: List[str], allocation: Any, budget: float, node_cost: Dict[str, Any]) -> Tuple[bool, Dict[str, int], str]:
    path_set = set(path)
    if allocation is None:
        allocation = {}
    if not isinstance(allocation, dict):
        return False, {}, "allocation must be a dict"

    clean_alloc: Dict[str, int] = {}
    for node, units in allocation.items():
        if node not in path_set:
            return False, {}, f"allocation node {node} not on path"
        if not is_int_like(units) or units < 0:
            return False, {}, f"invalid units for node {node}"
        unit_int = int(round(units))
        if node not in node_cost:
            if unit_int != 0:
                return False, {}, f"missing node_cost for {node}"
            continue  # allow zero allocation even if node_cost is absent
        clean_alloc[node] = unit_int

    total_cost = compute_allocation_cost(clean_alloc, node_cost)
    if total_cost > float(budget) + EPS:
        return False, {}, "budget exceeded"
    return True, clean_alloc, ""


def knapsack_best_utility(path: List[str], budget: float, node_cost: Dict[str, Any], utilities: Dict[str, List[float]]) -> float:
    if budget < 0:
        return 0.0
    if not is_int_like(budget):
        # Budget is expected to be integer-like; if not, approximate by flooring.
        budget = math.floor(budget + EPS)
    B = int(round(budget))
    dp = [0.0] * (B + 1)

    free_bonus = 0.0
    for node in path:
        cost_raw = node_cost.get(node)
        util_list = [float(u) for u in utilities.get(node, [])]
        if cost_raw is None:
            continue
        cost = float(cost_raw)
        if cost < EPS:
            free_bonus += sum(u for u in util_list if u > 0)
            continue

        if not is_int_like(cost):
            cost = round(cost)
        cost_int = int(round(cost))
        if cost_int <= 0:
            continue

        max_units = B // cost_int
        prefix_utils = [0.0]
        accum = 0.0
        for k in range(1, max_units + 1):
            if k <= len(util_list):
                accum += util_list[k - 1]
            prefix_utils.append(accum)
        new_dp = dp[:]
        for b in range(B + 1):
            if dp[b] < -EPS:
                continue
            for units, util_val in enumerate(prefix_utils):
                cost_here = units * cost_int
                if b + cost_here > B:
                    break
                candidate = dp[b] + util_val
                if candidate > new_dp[b + cost_here] + EPS:
                    new_dp[b + cost_here] = candidate
        dp = new_dp
    return max(dp) + free_bonus


def score_stage2(input_data: Dict[str, Any], submission: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    resources = input_data.get("resources", {})
    budget = float(resources.get("budget", 0))
    node_cost = {k: float(v) for k, v in resources.get("node_cost", {}).items()}
    utilities = {k: [float(x) for x in v] for k, v in resources.get("utility", {}).items()}

    allocation = submission.get("allocation", {})
    valid, clean_alloc, reason = validate_allocation(path, allocation, budget, node_cost)
    sub_utility = total_utility(clean_alloc, utilities) if valid else 0.0
    best_utility = knapsack_best_utility(path, budget, node_cost, utilities)

    stage_score = 0.0
    if valid:
        if best_utility <= EPS:
            stage_score = 30.0 if sub_utility <= EPS else 0.0
        else:
            stage_score = max(0.0, min(30.0, 30.0 * (sub_utility / best_utility)))

    return {
        "score": stage_score,
        "valid": valid,
        "reason": reason if not valid else "",
        "submitted_utility": sub_utility if valid else None,
        "best_utility": best_utility,
    }


# ---------------------------
# Stage 3: Scheduling & scoring
# ---------------------------
def filter_tasks_on_path(operations: List[Dict[str, Any]], path_set: set) -> List[Dict[str, Any]]:
    return [op for op in operations if op.get("node") in path_set]


def validate_schedule(schedule: Any, operations: List[Dict[str, Any]], allocation: Dict[str, int], parallel_limit: Optional[int]) -> Tuple[bool, float, str]:
    ops_by_id = {op["id"]: op for op in operations}
    required_ids = set(ops_by_id.keys())
    if not operations:
        return True, 0.0, ""
    if schedule is None or not isinstance(schedule, list):
        return False, 0.0, "schedule must be a list"

    start_times: Dict[str, float] = {}
    end_times: Dict[str, float] = {}
    seen_ids: set = set()

    for entry in schedule:
        if not isinstance(entry, dict) or "id" not in entry or "start" not in entry:
            return False, 0.0, "each schedule entry must have id and start"
        tid = entry["id"]
        if tid not in ops_by_id:
            return False, 0.0, f"unknown task {tid} in schedule"
        if tid in seen_ids:
            return False, 0.0, f"duplicate task {tid}"
        start = float(entry["start"])
        if start < -EPS:
            return False, 0.0, f"negative start for {tid}"
        op = ops_by_id[tid]
        duration = float(op.get("duration", 0))
        if duration < EPS:
            return False, 0.0, f"invalid duration for {tid}"
        start_times[tid] = start
        end_times[tid] = start + duration
        seen_ids.add(tid)

    if seen_ids != required_ids:
        missing = required_ids - seen_ids
        extra = seen_ids - required_ids
        if missing:
            return False, 0.0, f"missing tasks: {sorted(missing)}"
        if extra:
            return False, 0.0, f"unexpected tasks: {sorted(extra)}"

    # Precedence
    for tid, op in ops_by_id.items():
        for dep in op.get("deps", []):
            if dep not in ops_by_id:
                continue  # dependencies outside path are ignored
            if start_times[tid] + EPS < end_times[dep]:
                return False, 0.0, f"precedence violated for {tid} depends on {dep}"

    # Capacity and parallelism check via sweep-line
    events = []
    for tid, op in ops_by_id.items():
        node = op["node"]
        req = int(op.get("requires", 0))
        if req < 0:
            return False, 0.0, f"invalid requires for {tid}"
        if allocation.get(node, 0) < req:
            # Cannot ever run with provided capacity
            return False, 0.0, f"insufficient capacity for {tid}"
        events.append((start_times[tid], 1, node, req, tid))  # start event
        events.append((end_times[tid], 0, node, req, tid))    # end event (processed first at same time)

    events.sort(key=lambda x: (x[0], x[1]))  # end events (0) before start events (1) at same timestamp
    usage: Dict[str, int] = defaultdict(int)
    running_count = 0
    makespan = max(end_times.values()) if end_times else 0.0

    for time, kind, node, req, tid in events:
        if kind == 0:
            usage[node] -= req
            running_count -= 1
        else:
            if usage[node] + req > allocation.get(node, 0) + EPS:
                return False, 0.0, f"capacity exceeded on {node} at time {time}"
            if parallel_limit is not None and running_count + 1 > parallel_limit + EPS:
                return False, 0.0, f"parallelism limit exceeded at time {time}"
            usage[node] += req
            running_count += 1
    return True, makespan, ""


def heuristic_makespan(operations: List[Dict[str, Any]], allocation: Dict[str, int], parallel_limit: Optional[int]) -> float:
    if not operations:
        return 0.0
    ops_by_id = {op["id"]: op for op in operations}
    indeg: Dict[str, int] = defaultdict(int)
    children: Dict[str, List[str]] = defaultdict(list)

    for op in operations:
        tid = op["id"]
        for dep in op.get("deps", []):
            if dep in ops_by_id:
                indeg[tid] += 1
                children[dep].append(tid)

    ready = []
    for op in operations:
        tid = op["id"]
        if indeg[tid] == 0:
            ready.append(tid)
    ready.sort()

    time = 0.0
    running: List[Tuple[float, str]] = []  # (end_time, task_id)
    usage: Dict[str, int] = defaultdict(int)
    started = set()
    finished = set()

    def can_start(op: Dict[str, Any]) -> bool:
        node = op["node"]
        req = int(op.get("requires", 0))
        if allocation.get(node, 0) < req:
            return False
        if usage[node] + req > allocation.get(node, 0) + EPS:
            return False
        if parallel_limit is not None and len(running) >= parallel_limit:
            return False
        return True

    makespan = 0.0
    while ready or running:
        started_this_round = False
        # Greedy: start tasks with largest duration first
        ready_ops = sorted(ready, key=lambda tid: (-float(ops_by_id[tid].get("duration", 0)), tid))
        new_ready: List[str] = []
        for tid in ready_ops:
            op = ops_by_id[tid]
            if can_start(op):
                started_this_round = True
                ready.remove(tid)
                started.add(tid)
                node = op["node"]
                req = int(op.get("requires", 0))
                usage[node] += req
                end_time = time + float(op.get("duration", 0))
                heapq.heappush(running, (end_time, tid))
            else:
                new_ready.append(tid)

        if not started_this_round:
            if not running:
                # Deadlock (capacity too small or cyclic deps)
                return math.inf
            time, finished_tid = heapq.heappop(running)
            makespan = max(makespan, time)
            finished.add(finished_tid)
            node = ops_by_id[finished_tid]["node"]
            req = int(ops_by_id[finished_tid].get("requires", 0))
            usage[node] -= req
            for child in children[finished_tid]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    ready.append(child)
            # Also release any other tasks finishing at the same time
            while running and abs(running[0][0] - time) < EPS:
                t2, tid2 = heapq.heappop(running)
                makespan = max(makespan, t2)
                finished.add(tid2)
                node2 = ops_by_id[tid2]["node"]
                req2 = int(ops_by_id[tid2].get("requires", 0))
                usage[node2] -= req2
                for child in children[tid2]:
                    indeg[child] -= 1
                    if indeg[child] == 0:
                        ready.append(child)
        else:
            # If tasks were started, advance to next finish event
            if not running:
                continue
            time = running[0][0]
            continue
    makespan = max(makespan, time)
    return makespan


def score_stage3(input_data: Dict[str, Any], submission: Dict[str, Any], path: List[str], allocation: Dict[str, int]) -> Dict[str, Any]:
    tasks = input_data.get("tasks", {})
    operations = tasks.get("operations", [])
    path_set = set(path)
    ops_on_path = filter_tasks_on_path(operations, path_set)
    parallel_limit = tasks.get("parallelism_limit", None)
    if parallel_limit is not None and not is_int_like(parallel_limit):
        try:
            parallel_limit = int(round(float(parallel_limit)))
        except Exception:
            parallel_limit = None
    if parallel_limit is not None:
        parallel_limit = int(parallel_limit)

    schedule = submission.get("schedule", [])
    valid, sub_makespan, reason = validate_schedule(schedule, ops_on_path, allocation, parallel_limit)
    best_makespan = heuristic_makespan(ops_on_path, allocation, parallel_limit)

    stage_score = 0.0
    if valid and best_makespan != math.inf:
        if sub_makespan <= EPS:
            stage_score = 30.0 if best_makespan <= EPS else 0.0
        else:
            stage_score = 30.0 * min(1.0, best_makespan / sub_makespan)

    return {
        "score": stage_score,
        "valid": valid,
        "reason": reason if not valid else "",
        "submitted_makespan": sub_makespan if valid else None,
        "best_makespan": best_makespan if best_makespan != math.inf else None,
    }


# ---------------------------
# Grading orchestration
# ---------------------------
def grade_submission(input_data: Dict[str, Any], submission_data: Dict[str, Any]) -> Dict[str, Any]:
    stage1 = score_stage1(input_data, submission_data)
    sub_path = submission_data.get("path", [])

    stage2 = score_stage2(input_data, submission_data, sub_path)
    allocation = submission_data.get("allocation", {}) if stage2["valid"] else submission_data.get("allocation", {})
    if allocation is None:
        allocation = {}
    clean_allocation = {k: int(round(v)) for k, v in allocation.items() if is_int_like(v) and v >= 0}

    stage3 = score_stage3(input_data, submission_data, sub_path, clean_allocation)
    total = stage1["score"] + stage2["score"] + stage3["score"]
    return {
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
        "total_score": total,
    }


# ---------------------------
# Example cases
# ---------------------------
def example_cases() -> List[Tuple[str, Dict[str, Any], Dict[str, Any], float]]:
    """Returns (name, input, submission, expected_total) for quick self-checks."""
    case1_input = {
        "graph": {
            "nodes": ["A", "B", "C"],
            "edges": [{"from": "A", "to": "B", "weight": 1}, {"from": "B", "to": "C", "weight": 1}],
            "source": "A",
            "sink": "C",
            "forbidden": [],
        },
        "resources": {
            "budget": 3,
            "node_cost": {"A": 1, "B": 1, "C": 1},
            "utility": {"A": [2], "B": [3], "C": [1]},
        },
        "tasks": {
            "operations": [
                {"id": "t1", "node": "A", "duration": 1, "requires": 1, "deps": []},
                {"id": "t2", "node": "B", "duration": 1, "requires": 1, "deps": ["t1"]},
            ],
            "parallelism_limit": 2,
        },
    }
    case1_submission = {
        "path": ["A", "B", "C"],
        "allocation": {"A": 1, "B": 1, "C": 1},
        "schedule": [{"id": "t1", "start": 0}, {"id": "t2", "start": 1}],
    }

    # Case 2: suboptimal allocation (Stage 2 < max)
    case2_input = case1_input
    case2_submission = {
        "path": ["A", "B", "C"],
        "allocation": {"A": 0, "B": 1, "C": 0},
        "schedule": [{"id": "t1", "start": 0}, {"id": "t2", "start": 1}],
    }

    # Case 3: invalid schedule due to capacity
    case3_input = {
        "graph": {
            "nodes": ["S", "T"],
            "edges": [{"from": "S", "to": "T", "weight": 2}],
            "source": "S",
            "sink": "T",
            "forbidden": [],
        },
        "resources": {
            "budget": 2,
            "node_cost": {"S": 1, "T": 1},
            "utility": {"S": [1], "T": [1]},
        },
        "tasks": {
            "operations": [
                {"id": "x", "node": "T", "duration": 3, "requires": 2, "deps": []},
                {"id": "y", "node": "T", "duration": 1, "requires": 1, "deps": []},
            ],
            "parallelism_limit": 1,
        },
    }
    case3_submission = {
        "path": ["S", "T"],
        "allocation": {"S": 0, "T": 1},
        "schedule": [{"id": "x", "start": 0}, {"id": "y", "start": 0}],  # violates capacity/parallelism
    }

    return [
        ("perfect_solution", case1_input, case1_submission, 100.0),
        ("suboptimal_allocation", case2_input, case2_submission, None),  # expect < 100
        ("invalid_schedule", case3_input, case3_submission, None),       # Stage 3 should be 0
    ]


def run_examples() -> None:
    print("Running example cases...\n")
    for name, inp, sub, expected_total in example_cases():
        results = grade_submission(inp, sub)
        print(f"Case: {name}")
        print(json.dumps(results, indent=2))
        if expected_total is not None:
            assert abs(results["total_score"] - expected_total) < 1e-3, "unexpected score mismatch"
        print("-" * 40)
    print("Examples completed.")


# ---------------------------
# CLI
# ---------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade a submission for challenge-14-deepseek-v3.2")
    parser.add_argument("--input", required=False, help="Path to input JSON (ground truth)")
    parser.add_argument("--submission", required=False, help="Path to submission JSON")
    parser.add_argument("--run-examples", action="store_true", help="Run built-in example cases instead of grading files")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.run_examples:
        run_examples()
        return
    if not args.input or not args.submission:
        raise SystemExit("Error: --input and --submission are required unless --run-examples is used.")

    input_data = load_json(args.input)
    submission_data = load_json(args.submission)
    results = grade_submission(input_data, submission_data)
    if args.pretty:
        print(json.dumps(results, indent=2))
    else:
        print(json.dumps(results))


if __name__ == "__main__":
    main()
