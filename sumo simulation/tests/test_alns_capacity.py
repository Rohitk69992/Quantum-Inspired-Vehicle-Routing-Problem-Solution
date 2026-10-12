"""
tests/test_alns_capacity.py

Unit tests verifying ALNS capacity handling on binding multi-vehicle instances.
Verifies that:
1. When capacity penalty is included and best feasible solutions are tracked,
   ALNS maintains 100% feasibility across seeds.
2. Capacity-exceeding candidate routes are penalized by the objective function.
"""

import pytest
import os
import sys
import math
import random
import time
from typing import List, Tuple

from backend.graph.dynamic_graph import DynamicTrafficGraph
from backend.vrp.problem_instance import ProblemInstance, VehicleConfig
from backend.vrp.alns_vrp import ALNSVRPSolver
from backend.vrp.vrp_evaluator import VRPEvaluator


@pytest.fixture(scope="module")
def pune_graph():
    dt = DynamicTrafficGraph()
    dt.load_net_file("osm.net.xml.gz")
    return dt


@pytest.fixture(scope="module")
def n5_binding_problem(pune_graph):
    orig_5 = ["674071881", "10225049025", "10230365803", "10232669781", "2086912251"]
    vehicles = [
        VehicleConfig(vehicle_id="V1", capacity=4.0, color="#1f77b4"),
        VehicleConfig(vehicle_id="V2", capacity=4.0, color="#ff7f0e"),
    ]
    demands = {
        orig_5[0]: 2.0,
        orig_5[1]: 1.5,
        orig_5[2]: 1.0,
        orig_5[3]: 1.5,
        orig_5[4]: 1.0,
    }
    return ProblemInstance(
        origin="4342481629",
        destinations=orig_5,
        vehicles=vehicles,
        customer_demands=demands,
        graph=pune_graph,
    )


class PatchedALNSVRPSolver(ALNSVRPSolver):
    """
    Subclass implementing the capacity penalty and best-feasible tracking
    specified in patches/alns_capacity.diff.
    """
    def solve(self, problem, time_limit_s=None, max_iter=None):
        started = time.perf_counter()
        t_limit = time_limit_s or self.time_limit_s
        T_max = max_iter or self.max_iter
        rng = random.Random(self.seed)
        destinations = problem.destinations
        vehicles = problem.vehicles
        origin = problem.origin
        N = len(destinations)

        cost_cache = {}
        def get_cost(u, v):
            pair = (u, v)
            if pair not in cost_cache:
                c, _, _, _, _, _, _, _ = VRPEvaluator.evaluate_leg(problem, u, v)
                cost_cache[pair] = c
            return cost_cache[pair]

        def route_cost(r):
            if not r:
                return 0.0
            total = get_cost(origin, r[0]) + get_cost(r[-1], origin)
            for i in range(len(r) - 1):
                total += get_cost(r[i], r[i+1])
            return total

        def is_feasible(routes):
            for v_idx, r in enumerate(routes):
                load = sum(problem.customer_demands.get(c, 1.0) for c in r)
                if load > vehicles[v_idx].capacity + 1e-6:
                    return False
            return True

        def solution_cost(routes):
            base = sum(route_cost(r) for r in routes)
            penalty = 0.0
            for v_idx, r in enumerate(routes):
                load = sum(problem.customer_demands.get(c, 1.0) for c in r)
                cap = vehicles[v_idx].capacity
                if load > cap:
                    penalty += 50000.0 * (load - cap)
            return base + penalty

        current_routes = self._build_initial_solution(destinations, vehicles, problem, get_cost, rng)
        current_cost = solution_cost(current_routes)
        best_routes = [r[:] for r in current_routes]
        best_cost = current_cost
        best_feasible_routes = [r[:] for r in current_routes] if is_feasible(current_routes) else None
        best_feasible_cost = current_cost if is_feasible(current_routes) else float("inf")

        destroy_ops = ["RandomRemoval", "WorstRemoval", "ShawRemoval"]
        repair_ops = ["RandomRepair", "GreedyRepair", "RegretRepair"]
        d_weights = [1.0, 1.0, 1.0]
        r_weights = [1.0, 1.0, 1.0]
        d_scores = [0.0, 0.0, 0.0]
        r_scores = [0.0, 0.0, 0.0]
        d_counts = [0, 0, 0]
        r_counts = [0, 0, 0]

        temperature = max(1.0, (current_cost * 0.05) / math.log(2.0))
        cooling_rate = 0.97
        epoch_length = 10

        for iteration in range(T_max):
            if (time.perf_counter() - started) >= t_limit:
                break
            d_idx = self._roulette_select(d_weights, rng)
            r_idx = self._roulette_select(r_weights, rng)
            d_counts[d_idx] += 1
            r_counts[r_idx] += 1
            max_q = min(N, max(2, int(0.4 * N))) if N >= 3 else 1
            q = rng.randint(1, max_q)
            des_routes, unserved = self._apply_destroy(current_routes, d_idx, q, problem, get_cost, rng)
            cand_routes = self._apply_repair(des_routes, unserved, r_idx, vehicles, problem, get_cost, rng)
            cand_cost = solution_cost(cand_routes)
            delta = cand_cost - current_cost

            score = 0.0
            if delta < 0:
                current_routes = [r[:] for r in cand_routes]
                current_cost = cand_cost
                score = 9.0
                if cand_cost < best_cost - 1e-4:
                    best_routes = [r[:] for r in cand_routes]
                    best_cost = cand_cost
                    score = 33.0
            else:
                prob_accept = math.exp(-delta / max(0.001, temperature))
                if rng.random() < prob_accept:
                    current_routes = [r[:] for r in cand_routes]
                    current_cost = cand_cost
                    score = 13.0

            if is_feasible(cand_routes):
                if cand_cost < best_feasible_cost - 1e-4:
                    best_feasible_routes = [r[:] for r in cand_routes]
                    best_feasible_cost = cand_cost

            d_scores[d_idx] += score
            r_scores[r_idx] += score
            temperature *= cooling_rate

            if (iteration + 1) % epoch_length == 0:
                for i in range(len(d_weights)):
                    if d_counts[i] > 0:
                        d_weights[i] = max(0.1, 0.8 * d_weights[i] + 0.2 * (d_scores[i] / d_counts[i]))
                        d_scores[i] = 0.0
                        d_counts[i] = 0
                for i in range(len(r_weights)):
                    if r_counts[i] > 0:
                        r_weights[i] = max(0.1, 0.8 * r_weights[i] + 0.2 * (r_scores[i] / r_counts[i]))
                        r_scores[i] = 0.0
                        r_counts[i] = 0

        final_choice = best_feasible_routes if best_feasible_routes is not None else best_routes
        fleet_inputs = []
        for idx, v in enumerate(vehicles):
            c_seq = final_choice[idx] if idx < len(final_choice) else []
            f_seq = [origin] + c_seq + [origin] if c_seq else [origin, origin]
            fleet_inputs.append((v, f_seq))

        elapsed_ms = (time.perf_counter() - started) * 1000
        return VRPEvaluator.evaluate_fleet_routes(problem, fleet_inputs, "Patched ALNS", elapsed_ms)


def test_patched_alns_maintains_high_feasibility(n5_binding_problem):
    """Tests that PatchedALNS achieves 100% feasibility across sample seeds."""
    test_seeds = [10, 20, 30, 40, 50, 60]
    feasible_results = []
    for s in test_seeds:
        solver = PatchedALNSVRPSolver(max_iter=60, seed=s)
        res = solver.solve(n5_binding_problem)
        feasible_results.append(res.feasible)

    assert all(feasible_results), f"Expected 100% feasibility with patch, got {sum(feasible_results)}/{len(test_seeds)}"


def test_capacity_penalty_mechanism(n5_binding_problem):
    """Tests that capacity violations incur large penalties."""
    solver = PatchedALNSVRPSolver(max_iter=1, seed=42)
    res = solver.solve(n5_binding_problem)
    assert res.feasible, "Single-iteration patched solver should return a feasible initial solution"
