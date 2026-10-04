#!/usr/bin/env python3
"""
scripts/generate_instances.py

Deterministically generates machine-readable benchmark problem instances
for the IEEE T-ITS research evaluation suite on the Pune SUMO network.
All nodes are verified to belong to the largest strongly connected component (SCC)
to guarantee physical reachability on the directed urban road network.
"""

import os
import sys
import json
import random

# Bootstrap workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import networkx as nx
from backend.graph.dynamic_graph import DynamicTrafficGraph


def generate_benchmark_instances():
    net_path = "osm.net.xml.gz"
    if not os.path.exists(net_path):
        raise FileNotFoundError(f"Network file not found: {net_path}")

    print(f"Loading SUMO network topology from {net_path}...")
    dt = DynamicTrafficGraph()
    dt.load_net_file(net_path)

    # Determine largest strongly connected component
    scc = max(nx.strongly_connected_components(dt.graph), key=len)
    scc_list = sorted(list(scc))
    print(f"Loaded network: {dt.graph.number_of_nodes()} nodes, Largest SCC: {len(scc_list)} nodes.")

    depot = "4342481629"
    assert depot in scc, f"Depot {depot} must be in largest SCC"

    # Base 5 customers from original study
    orig_5 = ["674071881", "10225049025", "10230365803", "10232669781", "2086912251"]
    for c in orig_5:
        assert c in scc, f"Customer {c} must be in largest SCC"

    # Fixed seed for deterministic selection of additional SCC nodes
    rng = random.Random(12345)
    candidates = [n for n in scc_list if n != depot and n not in orig_5]

    # Select deterministic additional nodes
    extra_nodes = rng.sample(candidates, 30)
    n8_dest = orig_5 + extra_nodes[:3]
    n10_dest = n8_dest + extra_nodes[3:5]
    n15_dest = n10_dest + extra_nodes[5:10]
    n20_dest = n15_dest + extra_nodes[10:15]

    os.makedirs("benchmarks/instances", exist_ok=True)

    instances = [
        # Quantum-tractable instances (N=3, N=4)
        {
            "id": "pune_q3",
            "name": "Pune Quantum 3-Customer Benchmark",
            "type": "Level_0_Quantum",
            "depot": depot,
            "destinations": orig_5[:3],
            "num_customers": 3,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 100.0, "color": "#1f77b4"}
            ],
            "customer_demands": {c: 1.0 for c in orig_5[:3]},
            "binding_capacity": False,
        },
        {
            "id": "pune_q4",
            "name": "Pune Quantum 4-Customer Benchmark",
            "type": "Level_0_Quantum",
            "depot": depot,
            "destinations": orig_5[:4],
            "num_customers": 4,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 100.0, "color": "#1f77b4"}
            ],
            "customer_demands": {c: 1.0 for c in orig_5[:4]},
            "binding_capacity": False,
        },
        # Level 1 Baseline (Identical to original benchmark)
        {
            "id": "pune_n5_v1_unconstrained",
            "name": "Pune N=5 Single-Vehicle Free-Flow Baseline",
            "type": "Level_1_Baseline",
            "depot": depot,
            "destinations": orig_5,
            "num_customers": 5,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 100.0, "color": "#1f77b4"}
            ],
            "customer_demands": {c: 1.0 for c in orig_5},
            "binding_capacity": False,
        },
        # Level 1 Binding Capacity (Multi-vehicle CVRP)
        {
            "id": "pune_n5_v2_binding",
            "name": "Pune N=5 Two-Vehicle Binding Capacity CVRP",
            "type": "Level_1_Binding",
            "depot": depot,
            "destinations": orig_5,
            "num_customers": 5,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 4.0, "color": "#1f77b4"},
                {"vehicle_id": "V2", "capacity": 4.0, "color": "#ff7f0e"},
            ],
            # Total demand = 2.0 + 1.5 + 1.0 + 1.5 + 1.0 = 7.0 > 4.0 (strictly requires both vehicles)
            "customer_demands": {
                orig_5[0]: 2.0,
                orig_5[1]: 1.5,
                orig_5[2]: 1.0,
                orig_5[3]: 1.5,
                orig_5[4]: 1.0,
            },
            "binding_capacity": True,
        },
        # Level 1 Scale (N=8)
        {
            "id": "pune_n8_v1_unconstrained",
            "name": "Pune N=8 Single-Vehicle Benchmark",
            "type": "Level_1_Scale",
            "depot": depot,
            "destinations": n8_dest,
            "num_customers": 8,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 100.0, "color": "#1f77b4"}
            ],
            "customer_demands": {c: 1.0 for c in n8_dest},
            "binding_capacity": False,
        },
        {
            "id": "pune_n8_v2_binding",
            "name": "Pune N=8 Two-Vehicle Binding Capacity CVRP",
            "type": "Level_1_Binding",
            "depot": depot,
            "destinations": n8_dest,
            "num_customers": 8,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 5.0, "color": "#1f77b4"},
                {"vehicle_id": "V2", "capacity": 5.0, "color": "#ff7f0e"},
            ],
            # Demands: 8 customers with demands summing to 9.0 > 5.0
            "customer_demands": {
                n8_dest[0]: 1.5,
                n8_dest[1]: 1.5,
                n8_dest[2]: 1.0,
                n8_dest[3]: 1.0,
                n8_dest[4]: 1.0,
                n8_dest[5]: 1.0,
                n8_dest[6]: 1.0,
                n8_dest[7]: 1.0,
            },
            "binding_capacity": True,
        },
        # Level 2 Combinatorial Scale (N=10, N=15, N=20)
        {
            "id": "pune_n10_v2_binding",
            "name": "Pune N=10 Two-Vehicle Binding Capacity CVRP",
            "type": "Level_2_Binding",
            "depot": depot,
            "destinations": n10_dest,
            "num_customers": 10,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 6.0, "color": "#1f77b4"},
                {"vehicle_id": "V2", "capacity": 6.0, "color": "#ff7f0e"},
            ],
            "customer_demands": {c: 1.0 for c in n10_dest},
            "binding_capacity": True,
        },
        {
            "id": "pune_n15_v3_binding",
            "name": "Pune N=15 Three-Vehicle Binding Capacity CVRP",
            "type": "Level_2_Scale",
            "depot": depot,
            "destinations": n15_dest,
            "num_customers": 15,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 6.0, "color": "#1f77b4"},
                {"vehicle_id": "V2", "capacity": 6.0, "color": "#ff7f0e"},
                {"vehicle_id": "V3", "capacity": 6.0, "color": "#2ca02c"},
            ],
            "customer_demands": {c: 1.0 for c in n15_dest},
            "binding_capacity": True,
        },
        {
            "id": "pune_n20_v4_binding",
            "name": "Pune N=20 Four-Vehicle Binding Capacity CVRP",
            "type": "Level_2_Scale",
            "depot": depot,
            "destinations": n20_dest,
            "num_customers": 20,
            "vehicles": [
                {"vehicle_id": "V1", "capacity": 6.0, "color": "#1f77b4"},
                {"vehicle_id": "V2", "capacity": 6.0, "color": "#ff7f0e"},
                {"vehicle_id": "V3", "capacity": 6.0, "color": "#2ca02c"},
                {"vehicle_id": "V4", "capacity": 6.0, "color": "#d62728"},
            ],
            "customer_demands": {c: 1.0 for c in n20_dest},
            "binding_capacity": True,
        },
    ]

    for inst in instances:
        out_path = os.path.join("benchmarks", "instances", f"{inst['id']}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(inst, f, indent=2)
        print(f"Generated {out_path} ({inst['num_customers']} customers, {len(inst['vehicles'])} vehicles, binding={inst['binding_capacity']})")

    print(f"\nSuccessfully generated all {len(instances)} benchmark instances.")


if __name__ == "__main__":
    generate_benchmark_instances()
