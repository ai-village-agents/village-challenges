#!/usr/bin/env python3
"""Supply Chain Optimization solver using a min-cost flow LP with PuLP.

Reads a test case JSON from stdin and writes a solution JSON to stdout.
The model splits warehouse/DC nodes into in/out pairs with a zero-cost,
capacity-limited edge to enforce node handling limits.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Iterable, List, Tuple

import pulp


def _as_list(data: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    """Return data[key] or data["nodes"][key] if nested; otherwise empty list."""
    if key in data:
        return data[key] or []
    nodes = data.get("nodes", {})
    return nodes.get(key, []) or []


def _normalize_case(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize inputs regardless of nesting style."""
    suppliers = _as_list(raw, "suppliers")
    warehouses = _as_list(raw, "warehouses")
    dcs = _as_list(raw, "distribution_centers")
    customers = _as_list(raw, "customers")
    edges = raw.get("edges", [])

    return {
        "suppliers": suppliers,
        "warehouses": warehouses,
        "distribution_centers": dcs,
        "customers": customers,
        "edges": edges,
        "metadata": raw.get("metadata", {}),
    }


def _transform_edges(
    edges: List[Dict[str, Any]],
    warehouses: Dict[str, float],
    dcs: Dict[str, float],
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """Split warehouses/DCs into in/out nodes and rewrite edges."""
    node_alias: Dict[str, str] = {}

    def in_node(node: str) -> str:
        if node in warehouses or node in dcs:
            return f"{node}_in"
        return node

    def out_node(node: str) -> str:
        if node in warehouses or node in dcs:
            return f"{node}_out"
        return node

    transformed: List[Dict[str, Any]] = []

    # Original edges rewritten to use split nodes when needed.
    for edge in edges:
        src = str(edge["from"])
        dst = str(edge["to"])
        transformed.append(
            {
                "src": out_node(src),
                "dst": in_node(dst),
                "cost": float(edge["cost"]),
                "capacity": float(edge["capacity"]),
                "orig_from": src,
                "orig_to": dst,
                "kind": "original",
            }
        )

    # Capacity edges for node splitting (zero cost, enforce node capacity).
    for node, cap in warehouses.items():
        node_alias[node] = node  # preserve mapping for output clarity
        transformed.append(
            {
                "src": f"{node}_in",
                "dst": f"{node}_out",
                "cost": 0.0,
                "capacity": float(cap),
                "orig_from": node,
                "orig_to": node,
                "kind": "node_capacity",
            }
        )

    for node, cap in dcs.items():
        node_alias[node] = node
        transformed.append(
            {
                "src": f"{node}_in",
                "dst": f"{node}_out",
                "cost": 0.0,
                "capacity": float(cap),
                "orig_from": node,
                "orig_to": node,
                "kind": "node_capacity",
            }
        )

    return transformed, node_alias


def solve_supply_chain(case: Dict[str, Any]) -> Dict[str, Any]:
    """Build and solve the LP, returning a solution dict."""
    data = _normalize_case(case)
    suppliers = {str(s["id"]): float(s["supply"]) for s in data["suppliers"]}
    warehouses = {str(w["id"]): float(w["capacity"]) for w in data["warehouses"]}
    dcs = {str(d["id"]): float(d["capacity"]) for d in data["distribution_centers"]}
    customers = {str(c["id"]): float(c["demand"]) for c in data["customers"]}
    transformed_edges, _ = _transform_edges(data["edges"], warehouses, dcs)

    prob = pulp.LpProblem("SupplyChainMinCost", pulp.LpMinimize)
    edge_vars: List[Tuple[pulp.LpVariable, Dict[str, Any]]] = []

    for idx, edge in enumerate(transformed_edges):
        var = pulp.LpVariable(
            f"f_{idx}_{edge['src']}_{edge['dst']}",
            lowBound=0,
            upBound=edge["capacity"],
            cat="Continuous",
        )
        edge_vars.append((var, edge))

    prob += pulp.lpSum(var * edge["cost"] for var, edge in edge_vars)

    # Build node set from transformed edges.
    nodes: set[str] = set()
    for edge in transformed_edges:
        nodes.add(edge["src"])
        nodes.add(edge["dst"])

    # Flow conservation and supply/demand constraints.
    for node in nodes:
        inflow = pulp.lpSum(var for var, edge in edge_vars if edge["dst"] == node)
        outflow = pulp.lpSum(var for var, edge in edge_vars if edge["src"] == node)

        if node in suppliers:
            prob += outflow - inflow <= suppliers[node], f"supply_{node}"
        elif node in customers:
            prob += inflow - outflow == customers[node], f"demand_{node}"
        else:
            prob += inflow - outflow == 0, f"balance_{node}"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    status_name = pulp.LpStatus.get(status, "Unknown")

    flows: List[Dict[str, Any]] = []
    total_cost = 0.0
    for var, edge in edge_vars:
        amount = var.value() or 0.0
        if amount <= 1e-9:
            continue
        if edge["kind"] != "node_capacity":
            flows.append(
                {
                    "from": edge["orig_from"],
                    "to": edge["orig_to"],
                    "amount": round(float(amount), 6),
                }
            )
            total_cost += float(amount) * edge["cost"]
        else:
            # Capacity edge cost is zero; no need to emit in flows.
            total_cost += float(amount) * edge["cost"]

    flows.sort(key=lambda f: (f["from"], f["to"]))

    notes = (
        "Min-cost flow LP built with PuLP/CBC. Decision variable f_e for every edge "
        "(including zero-cost capacity arcs that split warehouses/DCs into in/out nodes). "
        "Objective minimizes sum(cost_e * f_e). Constraints: (1) supplier outflow <= supply; "
        "(2) customer inflow == demand; (3) flow conservation on all split nodes; "
        "(4) 0 <= f_e <= edge_capacity and node capacity enforced via in->out arcs."
        f" Solver status: {status_name}."
    )

    return {
        "flows": flows,
        "total_cost": round(total_cost, 6),
        "notes": notes,
    }


def main() -> int:
    try:
        case = json.load(sys.stdin)
    except Exception as exc:  # pragma: no cover - defensive for malformed input
        print(f"Failed to read input JSON: {exc}", file=sys.stderr)
        return 1

    solution = solve_supply_chain(case)
    json.dump(solution, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
