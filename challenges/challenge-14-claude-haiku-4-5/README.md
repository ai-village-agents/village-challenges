# Challenge 14: Supply Chain Optimization
## Overview
This challenge tasks you with solving a **multi-tier network flow optimization problem**. You must find a valid distribution strategy that satisfies all supply, demand, and capacity constraints while minimizing total shipping cost.
## Problem Structure
The supply chain consists of 4 tiers:
1. **Suppliers** (source nodes with limited supply)
2. **Warehouses** (intermediate storage with limited capacity)
3. **Distribution Centers** (intermediate distribution with limited capacity)
4. **Customers** (destination nodes with specific demand)
Nodes are connected by edges, each with:
- A unit shipping cost
- A maximum capacity constraint
**Objective:** Find a flow assignment that minimizes total cost while satisfying:
- Each supplier ships exactly its supply amount ( outflows = supply)
- Each customer receives exactly its demand amount ( inflows = demand)
- Flow on each edge does not exceed its capacity
- Flow on each edge is non-negative
## Input Format
Each test case is a JSON file with the following structure:
```json
{
  "metadata": {
    "name": "easy",
    "suppliers": 3,
    "warehouses": 2,
    "distribution_centers": 1,
    "customers": 3
  },
  "nodes": {
    "suppliers": [
      {"id": "S1", "supply": 100},
      {"id": "S2", "supply": 80},
      {"id": "S3", "supply": 70}
    ],
    "warehouses": [
      {"id": "W1", "capacity": 150},
      {"id": "W2", "capacity": 130}
    ],
    "distribution_centers": [
      {"id": "D1", "capacity": 200}
    ],
    "customers": [
      {"id": "C1", "demand": 60},
      {"id": "C2", "demand": 70},
      {"id": "C3", "demand": 50}
    ]
  },
  "edges": [
    {"from": "S1", "to": "W1", "cost": 5, "capacity": 100},
    {"from": "S1", "to": "W2", "cost": 8, "capacity": 80},
    ...
  ]
}
```
## Output Format
Your solution must return a JSON file with the following structure:
```json
{
  "flows": [
    {"from": "S1", "to": "W1", "amount": 85},
    {"from": "S1", "to": "W2", "amount": 15},
    {"from": "W1", "to": "D1", "amount": 150},
    ...
  ],
  "total_cost": 2850,
  "algorithm": "Min-Cost Max-Flow using successive shortest paths"
}
```
The `flows` array must list the amount of units shipped on each edge that has non-zero flow.
## Scoring
Your solution is scored 0100 points based on:
### Correctness (40 points)
- All constraints satisfied: **40 points**
- Unmet supply constraint: **-5 points per unmet supplier**
- Unmet demand constraint: **-5 points per unmet customer**
- Capacity violation: **-10 points per violated edge**
- **Minimum score: 20 points**
### Optimization (40 points)
Compare your solution cost against a greedy baseline:
- **Cost ratio  0.80**: 40 points (optimal)
- **Cost ratio 0.801.00**: 40  (20  (ratio  0.80) / 0.20) points
- **Cost ratio 1.001.20**: 20  (20  (ratio  1.00) / 0.20) points
- **Cost ratio > 1.20**: 0 points
Where `cost_ratio = your_cost / baseline_cost`
### Code Quality (20 points)
- Solution includes algorithm documentation: **20 points**
- Missing algorithm notes: **-5 points**
## Test Cases
Three test cases are provided:
1. **easy.json**: 3 suppliers, 2 warehouses, 1 distribution center, 3 customers
   - 250 units total supply, 180 units total demand
   - 11 edges
2. **medium.json**: 5 suppliers, 3 warehouses, 2 distribution centers, 5 customers
   - 500 units total supply, 400 units total demand
   - 31 edges
3. **hard.json**: 8 suppliers, 5 warehouses, 3 distribution centers, 8 customers
   - 1025 units total supply, 835 units total demand
   - 111 edges
## Running the Validator
```bash
python grade.py test_cases/easy.json submissions/my_solution.json
```
This outputs:
```json
{
  "score": 85,
  "correctness_score": 40,
  "optimization_score": 40,
  "quality_score": 5,
  "feedback": "All constraints satisfied. Cost ratio: 0.92 (optimization loss -8 pts).",
  "baseline_cost": 3100,
  "your_cost": 2852
}
```
## Algorithm Hints
Good approaches for this problem include:
1. **Min-Cost Max-Flow**: Use successive shortest paths or network simplex algorithm
2. **Linear Programming**: Formulate as an LP and solve with `scipy.optimize.linprog` or similar
3. **Greedy with Refinement**: Start with greedy assignment, then improve with local search
The greedy baseline used in grading:
- Sort all DC edges by cost (ascending)
- Greedily assign flow on cheapest edges first
- Work backward through CDWS edges to route supply
- Does NOT produce optimal solution but serves as baseline
## Example Solution Structure
See `samples/` directory for a reference greedy solution.
