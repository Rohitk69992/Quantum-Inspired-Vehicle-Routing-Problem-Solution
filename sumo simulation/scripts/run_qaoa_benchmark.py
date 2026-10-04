#!/usr/bin/env python3
"""
scripts/run_qaoa_benchmark.py

Executes the quantum approximate optimization algorithm (QAOA) benchmark
for N=3 and N=4 customer instances on the Pune road network using the
corrected closed-tour position-variable QUBO formulation.

Author: Rohit Korade
Venue: IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS)
"""

import os
import sys
import time
import json
import yaml

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.graph.dynamic_graph import DynamicTrafficGraph
from backend.vrp.problem_instance import ProblemInstance, VehicleConfig
from backend.vrp.qaoa_vrp import QAOAVRPSolver
from backend.vrp.exact_mip_vrp import ExactMIPVRPSolver
from backend.vrp.dijkstra_vrp import DijkstraVRPSolver


def run_qaoa_experiments():
    print("=" * 70)
    print("STARTING QAOA BENCHMARK EXPERIMENTS (Corrected Closed-Tour QUBO)")
    print("=" * 70)

    # Load dynamic graph topology
    net_path = "osm.net.xml.gz"
    print(f"Loading SUMO network topology: {net_path}...")
    dt_graph = DynamicTrafficGraph()
    dt_graph.load_net_file(net_path)

    instances_to_run = [
        ("benchmarks/instances/pune_q3.json", 3),
        ("benchmarks/instances/pune_q4.json", 4),
    ]

    seeds = [10, 20, 30, 40, 50, 60]
    qaoa_results = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "backend": "Qiskit Statevector Simulator",
            "ansatz": "p=1 QAOA with Standard X-mixer",
            "seeds": seeds,
        },
        "instances": {},
    }

    for inst_file, N in instances_to_run:
        with open(inst_file, "r", encoding="utf-8") as f:
            inst_data = json.load(f)

        inst_id = inst_data["id"]
        print(f"\nRunning QAOA on {inst_id} (N={N} customers, N^2={N*N} qubits)...")

        prob = ProblemInstance(
            origin=inst_data["depot"],
            destinations=inst_data["destinations"],
            graph=dt_graph,
            vehicles=[VehicleConfig("V1", 100.0)],
            customer_demands={c: 1.0 for c in inst_data["destinations"]},
        )

        # Exact Reference via MIP
        mip_solver = ExactMIPVRPSolver(time_limit=10.0)
        mip_res = mip_solver.solve(prob)
        print(f"  Exact MIP Reference: Cost={mip_res.total_cost:.2f}s, Time={mip_res.computation_time_ms:.1f}ms")

        # Exhaustive Reference
        dijkstra_solver = DijkstraVRPSolver()
        dijkstra_res = dijkstra_solver.solve(prob)
        print(f"  Exhaustive Reference: Cost={dijkstra_res.total_cost:.2f}s, Time={dijkstra_res.computation_time_ms:.1f}ms")

        runs = []
        for seed in seeds:
            solver = QAOAVRPSolver(maxiter=20, restarts=2, seed=seed)
            res = solver.solve(prob, reps=1, shots=1024)
            gap = ((res.total_cost - mip_res.total_cost) / mip_res.total_cost * 100.0) if mip_res.feasible else 0.0

            sd = res.solver_details or {}
            runs.append({
                "seed": seed,
                "cost": res.total_cost,
                "travel_time": res.total_travel_time,
                "distance": res.total_distance,
                "runtime_ms": res.computation_time_ms,
                "feasible": res.feasible,
                "optimality_gap_pct": gap,
                "qubits": sd.get("qaoa_qubits", N * N),
                "penalty_P": sd.get("penalty_multiplier_P"),
                "selected_bitstring": sd.get("selected_feasible_bitstring"),
                "selected_probability": sd.get("selected_probability"),
                "most_likely_bitstring": sd.get("most_likely_bitstring"),
                "most_likely_probability": sd.get("most_likely_probability"),
                "variational_parameters": sd.get("qubo_details", {}).get("variational_parameters", {}),
            })
            print(f"    Seed {seed}: Cost={res.total_cost:.2f}s, Gap={gap:.2f}%, Feasible={res.feasible}, P(feas)={runs[-1]['selected_probability']:.4f}, Time={res.computation_time_ms:.1f}ms")

        qaoa_results["instances"][inst_id] = {
            "num_customers": N,
            "num_qubits": N * N,
            "exact_mip_cost": mip_res.total_cost,
            "exact_mip_time_ms": mip_res.computation_time_ms,
            "exhaustive_cost": dijkstra_res.total_cost,
            "runs": runs,
        }

    os.makedirs("results/raw", exist_ok=True)
    out_path = "results/raw/qaoa_raw_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(qaoa_results, f, indent=2)
    print(f"\n[OUTPUT] QAOA results written to {out_path}")


if __name__ == "__main__":
    run_qaoa_experiments()
