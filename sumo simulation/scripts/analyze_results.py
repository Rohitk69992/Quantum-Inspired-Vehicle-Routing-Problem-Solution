#!/usr/bin/env python3
"""
scripts/analyze_results.py

Performs rigorous non-parametric statistical hypothesis testing and effect size analysis
on raw benchmark results for IEEE T-ITS.

Methodological components:
1. Descriptive Statistics: Mean, SD, Median, IQR, 95% Bootstrap Confidence Intervals (2000 resamples).
2. Omnibus Ranking: Friedman Test & Iman-Davenport F-statistic across benchmark instances.
3. Post-Hoc Pairwise Testing: Wilcoxon signed-rank test with Pratt zero-handling.
4. Familywise Error Rate Control: Holm Step-Down adjusted p-values.
5. Non-Parametric Effect Size: Vargha-Delaney A12 metric with magnitude classification.
"""

import os
import sys
import json
import numpy as np
import scipy.stats as stats
from typing import Dict, List, Any, Tuple

# Bootstrap sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def compute_bootstrap_ci(data: List[float], n_bootstraps: int = 2000, ci_level: float = 0.95, seed: int = 42) -> Tuple[float, float]:
    """Computes percentile bootstrap confidence interval for the sample mean."""
    if len(data) < 2:
        val = data[0] if data else 0.0
        return (val, val)
    rng = np.random.default_rng(seed)
    boot_means = [np.mean(rng.choice(data, size=len(data), replace=True)) for _ in range(n_bootstraps)]
    alpha = (1.0 - ci_level) / 2.0
    lower = float(np.percentile(boot_means, alpha * 100))
    upper = float(np.percentile(boot_means, (1.0 - alpha) * 100))
    return (round(lower, 2), round(upper, 2))


def compute_vargha_delaney_a12(sample_a: List[float], sample_b: List[float]) -> Tuple[float, str]:
    """
    Computes Vargha-Delaney A12 non-parametric effect size.
    A12 measures the probability that a random observation from A is lower (better) than B.
    """
    na = len(sample_a)
    nb = len(sample_b)
    if na == 0 or nb == 0:
        return 0.5, "negligible"

    # Compute Mann-Whitney U for sample_a vs sample_b
    u_stat, _ = stats.mannwhitneyu(sample_a, sample_b, alternative="two-sided")
    # For minimization: A12 = (na*nb + (na*(na+1))/2 - R1) / (na*nb)
    # We report standard A12: P(A < B) + 0.5 * P(A == B)
    less_count = sum(1.0 for x in sample_a for y in sample_b if x < y)
    equal_count = sum(1.0 for x in sample_a for y in sample_b if x == y)
    a12 = (less_count + 0.5 * equal_count) / (na * nb)

    diff = abs(a12 - 0.5)
    if diff < 0.06:
        mag = "negligible"
    elif diff < 0.14:
        mag = "small"
    elif diff < 0.21:
        mag = "medium"
    else:
        mag = "large"

    return round(float(a12), 4), mag


def run_statistical_analysis():
    print("=" * 70)
    print("STARTING STATISTICAL METHODOLOGY AUDIT & ANALYSIS")
    print("=" * 70)

    raw_path = "results/raw/benchmark_raw_results.json"
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw benchmark results missing: {raw_path}. Run scripts/run_experiments.py first.")

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    instances = data.get("instances", {})
    analyzed_data: Dict[str, Any] = {
        "metadata": data.get("metadata", {}),
        "instances": {},
        "omnibus_tests": {},
        "pairwise_comparisons": {},
    }

    # Track mean costs per algorithm across instances for Friedman test
    algo_names = ["HGS", "ALNS", "QPSO"]
    instance_means_for_friedman = {algo: [] for algo in algo_names}
    instances_evaluated = []

    for inst_id, inst_info in instances.items():
        solvers = inst_info.get("solvers", {})
        inst_summary = {
            "instance_id": inst_id,
            "type": inst_info.get("type"),
            "num_customers": inst_info.get("num_customers"),
            "num_vehicles": inst_info.get("num_vehicles"),
            "binding_capacity": inst_info.get("binding_capacity"),
            "algorithms": {},
        }

        # Exact MIP
        if "Exact_MIP" in solvers:
            mip = solvers["Exact_MIP"]
            inst_summary["algorithms"]["Exact_MIP"] = {
                "feasible": mip["feasible"],
                "cost": round(float(mip["total_cost"]), 2),
                "runtime_ms": round(float(mip["computation_time_ms"]), 2),
                "distance_m": round(float(mip["total_distance"]), 2),
            }

        # Exhaustive
        if "Exhaustive_Baseline" in solvers:
            ex = solvers["Exhaustive_Baseline"]
            inst_summary["algorithms"]["Exhaustive_Baseline"] = {
                "feasible": ex["feasible"],
                "cost": round(float(ex["total_cost"]), 2),
                "runtime_ms": round(float(ex["computation_time_ms"]), 2),
                "distance_m": round(float(ex["total_distance"]), 2),
            }

        # Stochastic Metaheuristics (ALNS, HGS, QPSO)
        for algo in algo_names:
            if algo in solvers:
                runs = solvers[algo]
                costs = [float(r["cost"]) for r in runs if r["feasible"]]
                times = [float(r["runtime_ms"]) for r in runs]
                gaps = [float(r["optimality_gap_pct"]) for r in runs if r.get("optimality_gap_pct") is not None]
                feas_count = sum(1 for r in runs if r["feasible"])

                mean_c = float(np.mean(costs)) if costs else float("nan")
                std_c = float(np.std(costs, ddof=1)) if len(costs) > 1 else 0.0
                med_c = float(np.median(costs)) if costs else float("nan")
                q25, q75 = (float(np.percentile(costs, 25)), float(np.percentile(costs, 75))) if costs else (0.0, 0.0)
                iqr_c = q75 - q25

                ci_low, ci_high = compute_bootstrap_ci(costs, n_bootstraps=2000)

                inst_summary["algorithms"][algo] = {
                    "n_runs": len(runs),
                    "feasible_runs": feas_count,
                    "feasibility_rate_pct": round(feas_count / max(1, len(runs)) * 100.0, 1),
                    "mean_cost": round(mean_c, 2),
                    "std_cost": round(std_c, 2),
                    "median_cost": round(med_c, 2),
                    "iqr_cost": round(iqr_c, 2),
                    "ci_95_cost": [ci_low, ci_high],
                    "min_cost": round(float(min(costs)), 2) if costs else float("nan"),
                    "max_cost": round(float(max(costs)), 2) if costs else float("nan"),
                    "mean_runtime_ms": round(float(np.mean(times)), 2),
                    "std_runtime_ms": round(float(np.std(times, ddof=1)), 2) if len(times) > 1 else 0.0,
                    "median_runtime_ms": round(float(np.median(times)), 2),
                    "mean_gap_pct": round(float(np.mean(gaps)), 2) if gaps else None,
                }

                instance_means_for_friedman[algo].append(mean_c)

        instances_evaluated.append(inst_id)
        analyzed_data["instances"][inst_id] = inst_summary

    # -------------------------------------------------------------
    # 2. OMNIBUS FRIEDMAN TEST ACROSS INSTANCES
    # -------------------------------------------------------------
    friedman_matrix = np.array([instance_means_for_friedman[algo] for algo in algo_names])
    # matrix shape: (K, N_I) -> transpose to (N_I, K)
    friedman_matrix = friedman_matrix.T
    n_instances, k_algos = friedman_matrix.shape

    print(f"\nRunning Omnibus Friedman Test across {n_instances} instances for {k_algos} algorithms ({algo_names})...")
    # scipy.stats.friedmanchisquare takes *columns
    f_stat, p_val = stats.friedmanchisquare(*(friedman_matrix[:, i] for i in range(k_algos)))

    # Compute Iman-Davenport extension
    # F_F = ( (N - 1) * chi_F^2 ) / ( N * (k - 1) - chi_F^2 )
    denom = (n_instances * (k_algos - 1) - f_stat)
    if denom > 1e-6:
        f_iman_davenport = ((n_instances - 1) * f_stat) / denom
        p_iman_davenport = float(1.0 - stats.f.cdf(f_iman_davenport, k_algos - 1, (k_algos - 1) * (n_instances - 1)))
    else:
        f_iman_davenport = float("inf")
        p_iman_davenport = 0.0

    # Average ranks
    ranks = np.zeros_like(friedman_matrix)
    for i in range(n_instances):
        ranks[i] = stats.rankdata(friedman_matrix[i])
    avg_ranks = {algo: round(float(np.mean(ranks[:, idx])), 3) for idx, algo in enumerate(algo_names)}

    print(f"  Friedman Chi2: {f_stat:.4f}, p-value: {p_val:.5f}")
    print(f"  Iman-Davenport F: {f_iman_davenport:.4f}, p-value: {p_iman_davenport:.5f}")
    print(f"  Average Ranks: {avg_ranks}")

    analyzed_data["omnibus_tests"] = {
        "test_name": "Friedman Non-Parametric Rank Test",
        "num_instances": n_instances,
        "num_algorithms": k_algos,
        "algorithms": algo_names,
        "average_ranks": avg_ranks,
        "friedman_chi2": round(float(f_stat), 4),
        "friedman_p_value": float(p_val),
        "iman_davenport_f": round(float(f_iman_davenport), 4),
        "iman_davenport_p_value": float(p_iman_davenport),
        "reject_null_at_05": bool(p_val < 0.05),
    }

    # -------------------------------------------------------------
    # 3. PAIRWISE COMPARISONS: WILCOXON + HOLM POST-HOC + A12
    # -------------------------------------------------------------
    print("\nRunning Pairwise Statistical Tests & Vargha-Delaney Effect Sizes...")
    pairwise_results = {}
    for inst_id, inst_info in instances.items():
        solvers = inst_info.get("solvers", {})
        inst_pairwise = []

        pairs = [("HGS", "ALNS"), ("HGS", "QPSO"), ("ALNS", "QPSO")]
        raw_p_values = []
        pair_records = []

        for algo_a, algo_b in pairs:
            if algo_a in solvers and algo_b in solvers:
                costs_a = [float(r["cost"]) for r in solvers[algo_a] if r["feasible"]]
                costs_b = [float(r["cost"]) for r in solvers[algo_b] if r["feasible"]]

                # Ensure matching length for paired test
                min_len = min(len(costs_a), len(costs_b))
                sample_a = costs_a[:min_len]
                sample_b = costs_b[:min_len]

                diffs = [a - b for a, b in zip(sample_a, sample_b)]
                # Pratt method retains zeros in ranking
                if all(d == 0 for d in diffs):
                    w_stat = 0.0
                    p_val_pair = 1.0
                else:
                    try:
                        w_res = stats.wilcoxon(sample_a, sample_b, zero_method="pratt", alternative="two-sided")
                        w_stat = float(w_res.statistic)
                        p_val_pair = float(w_res.pvalue)
                    except Exception:
                        w_stat = 0.0
                        p_val_pair = 1.0

                a12, mag = compute_vargha_delaney_a12(sample_a, sample_b)

                rec = {
                    "pair": f"{algo_a}_vs_{algo_b}",
                    "algo_a": algo_a,
                    "algo_b": algo_b,
                    "n_pairs": min_len,
                    "mean_a": round(float(np.mean(sample_a)), 2),
                    "mean_b": round(float(np.mean(sample_b)), 2),
                    "wilcoxon_stat": round(w_stat, 2),
                    "raw_p_value": float(p_val_pair),
                    "a12_effect_size": a12,
                    "magnitude": mag,
                }
                pair_records.append(rec)
                raw_p_values.append(p_val_pair)

        # Apply Holm Step-Down Procedure to raw_p_values
        m = len(raw_p_values)
        sorted_indices = np.argsort(raw_p_values)
        holm_adjusted = [1.0] * m
        running_max = 0.0

        for rank_idx, orig_idx in enumerate(sorted_indices):
            multiplier = m - rank_idx
            adj_p = min(1.0, raw_p_values[orig_idx] * multiplier)
            running_max = max(running_max, adj_p)
            holm_adjusted[orig_idx] = round(float(running_max), 5)

        for idx, rec in enumerate(pair_records):
            rec["holm_adjusted_p_value"] = holm_adjusted[idx]
            rec["statistically_significant_at_05"] = bool(holm_adjusted[idx] < 0.05)
            inst_pairwise.append(rec)

        pairwise_results[inst_id] = inst_pairwise

    analyzed_data["pairwise_comparisons"] = pairwise_results

    os.makedirs("results/statistics", exist_ok=True)
    out_stat_path = "results/statistics/statistical_analysis.json"
    with open(out_stat_path, "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, indent=2)

    print(f"\n[OUTPUT] Statistical analysis results written to {out_stat_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_statistical_analysis()
