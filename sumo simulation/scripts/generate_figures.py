#!/usr/bin/env python3
"""
scripts/generate_figures.py

Generates publication-quality figures (both PDF vector and high-resolution PNG)
for the upgraded IEEE T-ITS manuscript.
All plots are rendered strictly from raw experimental results.
"""

import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

# Use clean IEEE style formatting
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 12,
    "figure.autolayout": True,
    "lines.linewidth": 1.5,
    "grid.alpha": 0.4,
})

def generate_publication_figures():
    print("=" * 70)
    print("GENERATING PUBLICATION FIGURES FROM EXPERIMENTAL RESULTS")
    print("=" * 70)

    raw_file = "results/raw/benchmark_raw_results.json"
    dynamic_file = "results/raw/dynamic_sumo_results.json"
    qaoa_file = "results/raw/qaoa_raw_results.json"

    os.makedirs("results/figures", exist_ok=True)
    os.makedirs("research_paper/figures", exist_ok=True)

    # -------------------------------------------------------------
    # FIGURE 1: MULTI-INSTANCE COST COMPARISON & GAP
    # -------------------------------------------------------------
    if os.path.exists(raw_file):
        with open(raw_file, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        instances = bench_data.get("instances", {})
        inst_ids = list(instances.keys())
        algos = ["HGS", "ALNS", "QPSO"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))

        # Panel 1: Mean Costs by Instance
        x = np.arange(len(inst_ids))
        width = 0.25

        for idx, algo in enumerate(algos):
            means = []
            for i_id in inst_ids:
                runs = instances[i_id].get("solvers", {}).get(algo, [])
                costs = [r["cost"] for r in runs if r["feasible"]]
                means.append(np.mean(costs) if costs else 0.0)
            ax1.bar(x + idx * width - width, means, width, label=algo, alpha=0.85)

        # Plot Exact MIP points if present
        mip_points = []
        for i_id in inst_ids:
            mip_sol = instances[i_id].get("solvers", {}).get("Exact_MIP")
            mip_points.append(mip_sol["total_cost"] if mip_sol and mip_sol["feasible"] else np.nan)
        ax1.plot(x, mip_points, "k*--", markersize=8, label="Exact MIP (Reference)")

        ax1.set_ylabel("Routing Objective Cost (s)")
        ax1.set_xlabel("Benchmark Instance")
        ax1.set_title("(a) Objective Cost Across Instances")
        ax1.set_xticks(x)
        clean_labels = [i_id.replace("pune_", "").replace("_unconstrained", " (U)").replace("_binding", " (B)") for i_id in inst_ids]
        ax1.set_xticklabels(clean_labels, rotation=35, ha="right")
        ax1.grid(True, linestyle="--")
        ax1.legend(loc="upper left")

        # Panel 2: Mean Optimality Gap (%)
        for idx, algo in enumerate(algos):
            gaps = []
            for i_id in inst_ids:
                runs = instances[i_id].get("solvers", {}).get(algo, [])
                g_vals = [r["optimality_gap_pct"] for r in runs if r.get("optimality_gap_pct") is not None]
                gaps.append(np.mean(g_vals) if g_vals else 0.0)
            ax2.bar(x + idx * width - width, gaps, width, label=algo, alpha=0.85)

        ax2.set_ylabel("Optimality Gap relative to MIP (%)")
        ax2.set_xlabel("Benchmark Instance")
        ax2.set_title("(b) Optimality Gap (%)")
        ax2.set_xticks(x)
        ax2.set_xticklabels(clean_labels, rotation=35, ha="right")
        ax2.grid(True, linestyle="--")
        ax2.legend(loc="upper left")

        fig.tight_layout()
        fig.savefig("results/figures/fig1_cost_and_gap.pdf")
        fig.savefig("results/figures/fig1_cost_and_gap.png", dpi=300)
        fig.savefig("research_paper/figures/fig1_per_seed_cost.pdf") # Mirror to paper
        fig.savefig("research_paper/figures/fig1_per_seed_cost.png", dpi=300)
        plt.close(fig)
        print("  [SAVED] fig1_cost_and_gap (PDF & PNG)")

        # -------------------------------------------------------------
        # FIGURE 2: COMPUTATION RUNTIME SCALING
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(6, 4))
        for algo in ["HGS", "ALNS", "QPSO"]:
            runtimes = []
            cust_counts = []
            for i_id in inst_ids:
                runs = instances[i_id].get("solvers", {}).get(algo, [])
                t_vals = [r["runtime_ms"] for r in runs]
                runtimes.append(np.mean(t_vals) if t_vals else 0.0)
                cust_counts.append(instances[i_id]["num_customers"])
            ax.plot(cust_counts, runtimes, marker="o", label=algo)

        # MIP runtimes
        mip_times = []
        mip_custs = []
        for i_id in inst_ids:
            mip_sol = instances[i_id].get("solvers", {}).get("Exact_MIP")
            if mip_sol and mip_sol["feasible"]:
                mip_times.append(mip_sol["computation_time_ms"])
                mip_custs.append(instances[i_id]["num_customers"])
        ax.plot(mip_custs, mip_times, "k*--", markersize=8, label="Exact MIP (HiGHS)")

        ax.set_yscale("log")
        ax.set_xlabel("Problem Scale (Number of Customers $N$)")
        ax.set_ylabel("Mean Computation Time (ms, log scale)")
        ax.set_title("Algorithmic Runtime Scaling Under Equal Evaluation Budget")
        ax.grid(True, which="both", linestyle="--")
        ax.legend()
        fig.tight_layout()
        fig.savefig("results/figures/fig2_runtime_scaling.pdf")
        fig.savefig("results/figures/fig2_runtime_scaling.png", dpi=300)
        fig.savefig("research_paper/figures/fig2_runtime_comparison.pdf") # Mirror to paper
        fig.savefig("research_paper/figures/fig2_runtime_comparison.png", dpi=300)
        plt.close(fig)
        print("  [SAVED] fig2_runtime_scaling (PDF & PNG)")

    # -------------------------------------------------------------
    # FIGURE 3: CLOSED-LOOP DYNAMIC SUMO INCIDENT TRAFFIC PROFILE
    # -------------------------------------------------------------
    if os.path.exists(dynamic_file):
        with open(dynamic_file, "r", encoding="utf-8") as f:
            dyn_data = json.load(f)

        st_tele = dyn_data.get("static_regime", {}).get("telemetry", [])
        dy_tele = dyn_data.get("dynamic_regime", {}).get("telemetry", [])

        st_times = [r["sim_time"] for r in st_tele]
        st_speeds = [r["speed_ms"] for r in st_tele]
        st_waits = [r["waiting_time_s"] for r in st_tele]

        dy_times = [r["sim_time"] for r in dy_tele]
        dy_speeds = [r["speed_ms"] for r in dy_tele]
        dy_waits = [r["waiting_time_s"] for r in dy_tele]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.5, 5.5), sharex=True)

        # Panel 1: Speed Profile
        ax1.plot(st_times, st_speeds, "r-", label="Static Unreactive Route (Bottleneck Trap)")
        ax1.plot(dy_times, dy_speeds, "b-", label="Dynamic Closed-Loop Reroute (Adaptive Detour)")
        ax1.axvline(30, color="k", linestyle=":", label="Arterial Incident Injection ($t=30\\,$s)")
        ax1.set_ylabel("Vehicle Speed (m/s)")
        ax1.set_title("(a) Real-Time Vehicle Speed Profile in SUMO Simulation")
        ax1.grid(True, linestyle="--")
        ax1.legend(loc="upper right")

        # Panel 2: Bottleneck Waiting Time
        ax2.plot(st_times, st_waits, "r-", label="Static Unreactive Route")
        ax2.plot(dy_times, dy_waits, "b-", label="Dynamic Closed-Loop Reroute")
        ax2.axvline(30, color="k", linestyle=":", label="Incident Injection ($t=30\\,$s)")
        ax2.set_xlabel("Simulation Time (s)")
        ax2.set_ylabel("Accumulated Waiting Time (s)")
        ax2.set_title("(b) Queue Waiting Time Delay Behind Bottleneck")
        ax2.grid(True, linestyle="--")
        ax2.legend(loc="upper left")

        fig.tight_layout()
        fig.savefig("results/figures/fig3_dynamic_sumo_incident.pdf")
        fig.savefig("results/figures/fig3_dynamic_sumo_incident.png", dpi=300)
        fig.savefig("research_paper/figures/fig3_dynamic_sumo_incident.pdf")
        fig.savefig("research_paper/figures/fig3_dynamic_sumo_incident.png", dpi=300)
        plt.close(fig)
        print("  [SAVED] fig3_dynamic_sumo_incident (PDF & PNG)")

    # -------------------------------------------------------------
    # FIGURE 4: QAOA PROBABILITY DISTRIBUTION & CONVERGENCE
    # -------------------------------------------------------------
    if os.path.exists(qaoa_file):
        with open(qaoa_file, "r", encoding="utf-8") as f:
            q_data = json.load(f)

        fig, ax = plt.subplots(figsize=(6, 4))
        inst_keys = list(q_data.get("instances", {}).keys())
        probs_all = []
        labels = []

        for k in inst_keys:
            runs = q_data["instances"][k].get("runs", [])
            p_vals = [r["selected_probability"] for r in runs]
            probs_all.append(p_vals)
            labels.append(f"{k} (N={q_data['instances'][k]['num_customers']})")

        ax.boxplot(probs_all, labels=labels)
        ax.set_ylabel("Feasible Ground State Probability $P(\\text{feas})$")
        ax.set_title("QAOA Ground State Sampling Probability (Corrected Closed-Tour QUBO)")
        ax.grid(True, linestyle="--")
        fig.tight_layout()
        fig.savefig("results/figures/fig4_qaoa_probabilities.pdf")
        fig.savefig("results/figures/fig4_qaoa_probabilities.png", dpi=300)
        fig.savefig("research_paper/figures/fig4_qaoa_probabilities.pdf")
        fig.savefig("research_paper/figures/fig4_qaoa_probabilities.png", dpi=300)
        plt.close(fig)
        print("  [SAVED] fig4_qaoa_probabilities (PDF & PNG)")

    print("=" * 70)
    print("ALL PUBLICATION FIGURES SUCCESSFULLY GENERATED")
    print("=" * 70)


if __name__ == "__main__":
    generate_publication_figures()
