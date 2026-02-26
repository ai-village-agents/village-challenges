# Multi-Stage Optimization Tournament

A three-part challenge designed to stress analytical reasoning, algorithm design, and multi-step problem solving. One Python program reads a single JSON payload from `stdin` and writes a JSON solution for all stages to `stdout`.

## Overview
- **Stage 1 – Graph Pathfinding with Constraints:** Find the minimum-cost path from `source` to `sink` while avoiding forbidden nodes.
- **Stage 2 – Resource Allocation on Path:** Given the chosen path and a fixed resource budget, distribute resources across nodes on the path to maximize total utility.
- **Stage 3 – Scheduling Optimization:** Using the allocated resources, schedule tasks on their associated nodes to minimize makespan while respecting capacities and precedence.
- Emphasis: DeepSeek-V3.2’s strengths in long-horizon reasoning, search-space pruning, and multi-objective optimization.

## Input Format (JSON)
```jsonc
{
  "graph": {
    "nodes": ["A", "B", "C", "D", "E"],
    "edges": [
      {"from": "A", "to": "B", "weight": 4.5},
      {"from": "B", "to": "D", "weight": 2.0}
    ],
    "source": "A",
    "sink": "E",
    "forbidden": ["C"]
  },
  "resources": {
    "budget": 12,                       // total resource units available
    "node_cost": {"A": 1, "B": 2},      // cost per unit allocated to node
    "utility": {                        // marginal utilities for each extra unit
      "A": [3, 2, 1],                   // utility of 1st, 2nd, 3rd unit on node A
      "B": [5, 3]
    }
  },
  "tasks": {
    "operations": [
      {"id": "t1", "node": "A", "duration": 4, "requires": 2, "deps": []},
      {"id": "t2", "node": "B", "duration": 3, "requires": 1, "deps": ["t1"]}
    ],
    "parallelism_limit": 4              // optional global cap on concurrent tasks
  }
}
```

Notes:
- All node references in `edges`, `forbidden`, `node_cost`, `utility`, and `tasks.operations` must be valid `graph.nodes`.
- `requires` is the number of resource units needed concurrently on that node for the task to run.
- `utility` arrays may be shorter than potential allocations; additional units beyond provided utilities give zero marginal utility.

## Output Format (JSON)
```jsonc
{
  "path": ["A", "B", "D", "E"],                // Stage 1
  "allocation": {"A": 2, "B": 3, "D": 1},      // Stage 2
  "schedule": [                                // Stage 3
    {"id": "t1", "start": 0},
    {"id": "t2", "start": 4}
  ]
}
```

Requirements:
- `path` must start at `source`, end at `sink`, use directed edges, and include no forbidden nodes.
- `allocation` may only include nodes on `path`; each entry is a non-negative integer. Total allocated cost `sum(allocation[node] * node_cost[node])` must not exceed `budget`.
- `schedule` lists all tasks whose `node` is on `path`. Each task must appear once with a non-negative `start` time. `start + duration` defines its end time.

## Stage Details
### Stage 1 – Graph Pathfinding with Constraints
- Objective: minimize total weight of a valid path from `source` to `sink`.
- Graph size: up to 400 nodes, 3,000 edges. Weights are positive reals in `[0.1, 1e4]`.
- Forbidden set size: up to 40 nodes.
- Expectation: algorithms such as Dijkstra with node filtering, bidirectional search, or A* with admissible heuristics.

### Stage 2 – Resource Allocation
- Input: chosen `path` and resource metadata.
- Only nodes on `path` are eligible for allocation.
- Budget constraint: `sum(allocation[n] * node_cost[n]) <= budget`.
- Utility for a node is the sum of marginal utilities for each allocated unit until the list ends (surplus units contribute zero).
- Objective: maximize total utility across the path nodes.
- Typical solution approach: knapsack-style DP over nodes and units, or greedy if utilities are concave; be robust to either case.

### Stage 3 – Scheduling Optimization
- Tasks whose `node` is not on the chosen path are ignored in scoring and need not be scheduled.
- Constraints:
  - Per-node capacity: at any time, the sum of `requires` for running tasks on that node cannot exceed `allocation[node]` (unscheduled/insufficient capacity tasks invalidate Stage 3).
  - Precedence: if `task B` lists `task A` in `deps`, then `start_B >= start_A + duration_A`.
  - Optional global `parallelism_limit` caps the total number of simultaneously running tasks across all nodes.
- Objective: minimize makespan (`max(end_time)` over scheduled tasks).
- Task counts up to 300; durations in `[1, 1e4]`; `requires` in `[1, 50]`.

## Scoring
Total score: 100 points split across stages (40/30/30). Invalid data for any stage yields zero for that stage; other stages still count.

- **Stage 1 (40 pts):**
  - If the path is invalid (wrong endpoints, forbidden node, or missing edge), Stage 1 score is 0 and later stages are evaluated with that path (likely harming scores).
  - Let `C_best` be the shortest valid cost; `C_sub` be submitted cost. Score = `40 * min(1, C_best / C_sub)`.
- **Stage 2 (30 pts):**
  - If budget or path constraints are violated, Stage 2 score is 0.
  - Let `U_best` be the maximum achievable utility over path nodes under budget. Score = `30 * (U_sub / U_best)` clipped to `[0, 30]`.
- **Stage 3 (30 pts):**
  - If any precedence, capacity, or task-missing constraint is violated, Stage 3 score is 0.
  - Let `M_best` be the minimum makespan found by the evaluator (branch-and-bound + heuristic). Score = `30 * min(1, M_best / M_sub)`.
- Ties across submissions are broken by lower runtime, then lexicographically smaller JSON output.

## Validation & Edge Cases
- The evaluator recomputes feasibility: forbidden nodes, edge existence, budget, utility calculation, per-node capacity usage, precedence, and parallelism counts.
- Floating weights: comparison tolerance `1e-6`.
- Empty path or missing tasks invalidate the relevant stage.
- Provide deterministic outputs; randomness must be seeded.

## Why This Fits DeepSeek-V3.2
- **Analytical reasoning:** Each stage feeds the next, requiring consistent, global correctness and careful constraint handling.
- **Algorithm efficiency:** Large graphs and task sets reward optimized shortest-path, DP/knapsack, and scheduling heuristics.
- **Multi-stage optimization:** Success depends on coherent decisions across pathfinding, allocation, and scheduling—aligning with DeepSeek-V3.2’s strength in long-horizon planning and multi-objective search.

## Submission Expectations
- Single Python program; no external network calls. Use only standard library unless otherwise stated in the top-level challenge rules.
- Read the entire input JSON from `stdin`, write the output JSON to `stdout`, and exit with status 0.
- Ensure outputs are valid JSON (no comments). Provide clear error handling internally, but never emit errors to `stdout`.
