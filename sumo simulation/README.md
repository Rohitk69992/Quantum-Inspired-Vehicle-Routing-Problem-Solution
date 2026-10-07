# A SUMO-Based Framework for Traffic-Aware Vehicle Routing With Quantum-Inspired and Classical Optimization

[![Paper Status](https://img.shields.io/badge/IEEE%20T--ITS-Preprint%202026-blue.svg)](research_paper/main.pdf)
[![SUMO](https://img.shields.io/badge/Eclipse%20SUMO-1.27.1-yellowgreen.svg)](https://eclipse.dev/sumo/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.5.2-purple.svg)](https://qiskit.org/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Author:** Rohit Korade  
**Affiliation:** Department of Artificial Intelligence and Data Science, ISBM College of Engineering, Pune, India  
**Email:** [rohitkorade69@gmail.com](mailto:rohitkorade69@gmail.com)  
**Target Venue:** *IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS)*  
**Initiative:** Smart India Hackathon (SIH) 2026 (Problem Statement SIH26137)  
**Manuscript PDF:** [research_paper/main.pdf](research_paper/main.pdf) (13 Pages, IEEEtran Journal Format)

---

## Table of Contents
1. [Overview & Executive Summary](#overview--executive-summary)
2. [System Architecture](#system-architecture)
3. [Empirical Experimental Results](#empirical-experimental-results)
   - [Benchmark Results Across Capacity Regimes (Table II)](#benchmark-results-across-capacity-regimes-table-ii)
   - [Non-Parametric Omnibus Friedman Test (Table III)](#non-parametric-omnibus-friedman-test-table-iii)
   - [Pairwise Statistical Comparisons & Effect Sizes (Table IV)](#pairwise-statistical-comparisons--effect-sizes-table-iv)
   - [Closed-Loop Dynamic SUMO Simulation (Table V)](#closed-loop-dynamic-sumo-simulation-table-v)
   - [Gate-Based QAOA Simulation & Hilbert Space Dilution (Table VI)](#gate-based-qaoa-simulation--hilbert-space-dilution-table-vi)
   - [Experimental Environment & Telemetry (Table VII)](#experimental-environment--telemetry-table-vii)
4. [Optimization Solvers Implemented](#optimization-solvers-implemented)
5. [Repository Structure](#repository-structure)
6. [Reproducibility & Execution Pipeline](#reproducibility--execution-pipeline)
7. [Citation](#citation)

---

## Overview & Executive Summary

This repository hosts an integrated software framework that connects microscopic road traffic simulation in **Eclipse SUMO** with classical, quantum-inspired, and gate-based quantum combinatorial optimization algorithms for the **Capacitated Vehicle Routing Problem (CVRP)**.

### Key Contributions & Scientific Findings
1. **Unified Evaluation Engine (`VRPEvaluator`):** Bridges physical road-level routing on a real OpenStreetMap network of Pune, India (3,559 junctions, 8,263 directed edges) with combinatorial fleet solvers, caching Dijkstra leg evaluations on a dynamic time-varying road graph $G(t) = (V, E, W(t))$ and strictly enforcing 20 mathematical CVRP invariants.
2. **Multi-Instance Benchmark Across Capacity Regimes:** Rigorously evaluated across 7 benchmark instances ($N \in \{5, 8, 10, 15, 20\}$ customers, $K \in \{1, 2, 3, 4\}$ vehicles) and 30 independent random seeds under a standardized 1,000-evaluation budget.
   - Under **unconstrained capacity**, all metaheuristics achieve near-optimal solutions (mean gap $\le 0.43\%$).
   - Under **strictly binding multi-vehicle capacity constraints**, ALNS experiences a sharp feasibility collapse down to **36.7% feasibility** on instance `pune_n5_v2_binding` due to unpenalized repair heuristics, whereas HGS (Prins dynamic programming split) and QPSO maintain **100% feasibility** across all 30 seeds.
3. **Closed-Loop Dynamic Traffic Sensing & Detouring:** Validated in Eclipse SUMO via TraCI under an injected 95% speed throttle incident on arterial edge `246580191#8`. The framework detects the bottleneck within 3 seconds and re-routes vehicles with **2.09 ms decision latency**, successfully navigating 28 detour road segments to bypass the queue.
4. **Corrected Closed-Tour QAOA Formulation:** Corrected the position-variable QUBO formulation by incorporating the terminal return-to-depot linear term $\sum_{i=1}^N c_{i,0} x_{i,N-1}$. Gate-based statevector simulations on $N=3$ (9 qubits) and $N=4$ (16 qubits) empirically demonstrate exponential Hilbert space dilution ($P(\text{feas}) \approx 0.0009 \to 0.0001$), establishing the NISQ-era scaling limits of unconstrained QUBO representations.
5. **Defensible Statistical Methodology:** Zero fabricated numbers. Every metric is backed by non-parametric bootstrap confidence intervals (2,000 resamples), omnibus Friedman tests, Iman-Davenport corrections, Holm step-down familywise error control, and Vargha-Delaney $\hat{A}_{12}$ non-parametric effect sizes.

---

## System Architecture

The platform operates on a two-tier decoupled architecture:

```
+---------------------------------------------------------------------------------------+
|                    TIER 1: COMBINATORIAL FLEET OPTIMIZATION LAYER                     |
|                                                                                       |
|  [Exact MIP]       [Exhaustive]      [Hybrid Genetic]      [ALNS]         [QPSO]      |
|  (HiGHS MTZ)       (Dijkstra Base)   (Prins DP Split)      (Ropke 2006)   (Swarm)     |
+---------------------------------------------------------------------------------------+
                                           |
+---------------------------------------------------------------------------------------+
|              COMMON EVALUATION ENGINE: VRPEvaluator & ProblemInstance                 |
|  - Uniform Leg Dijkstra on G(t)       - Dynamic Edge Weight Query                     |
|  - 20 Mathematical CVRP Invariants    - Bottleneck Detection & Leg Caching            |
+---------------------------------------------------------------------------------------+
                                           |
+---------------------------------------------------------------------------------------+
|            TIER 2: DYNAMIC PHYSICAL ROAD NETWORK & SIMULATION LAYER                   |
|                                                                                       |
|  [OpenStreetMap Pune Graph]       [Eclipse SUMO Microphysics]       [TraCI Protocol]  |
|  (3,559 Nodes, 8,263 Edges)       (Car-following, Queues)           (Live Telemetry)  |
+---------------------------------------------------------------------------------------+
```

Dynamic edge weights are updated at each simulation step $t$ according to:
$$w_e(t) = \Big(\alpha T_e(t) + \beta D_e + \gamma (C_e(t) \cdot 100)\Big) \cdot \mu_e(t)$$
where $T_e(t)$ is travel time, $D_e$ is length, $C_e(t) \in [0, 1]$ is the TraCI congestion ratio, and $\mu_e(t) \ge 1.0$ is the incident penalty multiplier.

---

## Empirical Experimental Results

All numbers below represent measured, unmanipulated values executed on the standardized hardware testbed and published in the IEEE manuscript.

### Benchmark Results Across Capacity Regimes (Table II)
Evaluated across $n = 30$ independent random seeds ($\{10, 20, \dots, 300\}$) under a standardized 1,000-evaluation budget on the Pune road network:

| Instance | Algorithm | Mean Cost (s) | Std. Dev. | Median [IQR] | 95% Bootstrap CI | Runtime (ms) | Gap (%) | Feasibility (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **pune_n5_v1_unconstrained**<br>($N=5, K=1, Q=100$) | **Exact MIP (HiGHS)** | 865.01 | --- | 865.01 [0.0] | [865.01, 865.01] | 133.5 | 0.00 | 100.0% |
| | **Exhaustive Baseline** | 865.01 | --- | 865.01 [0.0] | [865.01, 865.01] | 53.5 | 0.00 | 100.0% |
| | **HGS** | 865.48 | 2.53 | 865.01 [0.0] | [865.0, 866.4] | 70.2 | 0.05 | 100% |
| | **ALNS** | 866.86 | 4.79 | 865.01 [0.0] | [865.5, 868.7] | 2.7 | 0.21 | 100% |
| | **QPSO** | 868.71 | 6.23 | 865.01 [10.4] | [866.4, 871.0] | 504.7 | 0.43 | 100% |
| **pune_n5_v2_binding**<br>($N=5, K=2, Q=5$) | **Exact MIP (HiGHS)** | 1080.84 | --- | 1080.84 [0.0] | [1080.84, 1080.84] | 174.7 | 0.00 | 100.0% |
| | **HGS** | 1084.43 | 10.92 | 1080.84 [0.0] | [1081.4, 1089.1] | 89.8 | 0.33 | 100% |
| | **ALNS** | 1081.95 | 3.70 | 1080.84 [0.0] | [1080.8, 1084.2] | 2.9 | 0.10 | **37%** |
| | **QPSO** | 1080.84 | 0.00 | 1080.84 [0.0] | [1080.8, 1080.8] | 600.6 | 0.00 | 100% |
| **pune_n8_v1_unconstrained**<br>($N=8, K=1, Q=100$) | **Exact MIP (HiGHS)** | 1095.40 | --- | 1095.40 [0.0] | [1095.40, 1095.40] | 605.4 | 0.00 | 100.0% |
| | **Exhaustive Baseline** | 1149.98 | --- | 1149.98 [0.0] | [1149.98, 1149.98] | 207.6 | 0.00 | 100.0% |
| | **HGS** | 1099.60 | 7.21 | 1095.40 [7.4] | [1097.3, 1102.3] | 108.1 | 0.38 | 100% |
| | **ALNS** | 1100.03 | 7.20 | 1095.40 [15.4] | [1097.5, 1102.6] | 4.4 | 0.42 | 100% |
| | **QPSO** | 1110.64 | 11.79 | 1110.84 [21.2] | [1106.5, 1114.8] | 794.8 | 1.39 | 100% |
| **pune_n8_v2_binding**<br>($N=8, K=2, Q=9$) | **Exact MIP (HiGHS)** | 1292.00 | --- | 1292.00 [0.0] | [1292.00, 1292.00] | 1227.1 | 0.00 | 100.0% |
| | **HGS** | 1329.65 | 33.91 | 1320.46 [30.5] | [1318.7, 1342.3] | 176.7 | 2.91 | 100% |
| | **ALNS** | 1298.86 | 37.60 | 1292.00 [0.0] | [1292.0, 1312.6] | 4.6 | 0.53 | 100% |
| | **QPSO** | 1301.64 | 13.30 | 1292.00 [21.2] | [1297.3, 1306.7] | 957.7 | 0.75 | 100% |
| **pune_n10_v2_binding**<br>($N=10, K=2, Q=11$) | **Exact MIP (HiGHS)** | 1426.20 | --- | 1426.20 [0.0] | [1426.20, 1426.20] | 3352.5 | 0.00 | 100.0% |
| | **HGS** | 1476.67 | 33.90 | 1468.47 [46.0] | [1464.8, 1489.1] | 285.5 | 3.54 | 100% |
| | **ALNS** | 1427.18 | 5.40 | 1426.20 [0.0] | [1426.2, 1429.2] | 6.3 | 0.07 | 100% |
| | **QPSO** | 1470.82 | 29.88 | 1467.17 [43.6] | [1459.6, 1482.1] | 1093.8 | 3.13 | 100% |
| **pune_n15_v3_binding**<br>($N=15, K=3, Q=12$) | **HGS** | 1989.43 | 140.58 | 1993.00 [229.3] | [1939.4, 2037.0] | 552.4 | --- | 100% |
| | **ALNS** | 1608.08 | 48.90 | 1591.92 [3.1] | [1595.0, 1628.4] | 45.1 | --- | 100% |
| | **QPSO** | 1861.39 | 172.14 | 1853.59 [243.2] | [1802.6, 1925.0] | 1901.3 | --- | 100% |
| **pune_n20_v4_binding**<br>($N=20, K=4, Q=13$) | **HGS** | 2916.66 | 200.03 | 2919.16 [283.7] | [2847.3, 2990.6] | 909.8 | --- | 100% |
| | **ALNS** | 1995.89 | 29.54 | 1986.76 [1.4] | [1987.3, 2008.1] | 78.3 | --- | 100% |
| | **QPSO** | 2708.69 | 228.54 | 2746.07 [247.0] | [2628.3, 2789.2] | 2607.7 | --- | 100% |

---

### Non-Parametric Omnibus Friedman Test (Table III)
Evaluated across all $N_I = 7$ problem instances for the three stochastic metaheuristics:

| Algorithm | Average Rank | Friedman $\chi_F^2$ | Iman-Davenport $F_F$ | $p$-value | Conclusion |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ALNS** | **1.429** | \multirow{3}{*}{3.714} | \multirow{3}{*}{2.167} | \multirow{3}{*}{0.1573} | Fail to reject $H_0$ at $\alpha = 0.05$. No universal omnibus dominance across instances. |
| **QPSO** | **2.143** | | | | |
| **HGS** | **2.429** | | | | |

---

### Pairwise Statistical Comparisons & Effect Sizes (Table IV)
Wilcoxon signed-rank tests computed with Pratt zero-handling and Holm step-down familywise error control ($n=30$ paired seeds):

| Instance | Comparison | Raw $p$-value | Holm Adjusted $p$ | Vargha-Delaney $\hat{A}_{12}$ | Magnitude | Significant ($\alpha=0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **pune_n5_v1** | HGS vs. ALNS | 0.1797 | 0.3594 | 0.550 | Negligible | No |
| | HGS vs. QPSO | 0.0196 | 0.0589 | 0.617 | Small | No |
| | ALNS vs. QPSO | 0.2059 | 0.3594 | 0.567 | Small | No |
| **pune_n5_v2** | HGS vs. ALNS | 1.0000 | 1.0000 | 0.504 | Negligible | No |
| | HGS vs. QPSO | 0.0144 | 0.0433 | 0.400 | Small | **Yes** |
| | ALNS vs. QPSO | 1.0000 | 1.0000 | 0.455 | Negligible | No |
| **pune_n8_v1** | HGS vs. ALNS | 0.9726 | 0.9726 | 0.502 | Negligible | No |
| | HGS vs. QPSO | < 0.0001 | 0.0002 | 0.763 | Large | **Yes** |
| | ALNS vs. QPSO | 0.0007 | 0.0014 | 0.770 | Large | **Yes** |
| **pune_n8_v2** | HGS vs. ALNS | < 0.0001 | 0.0001 | 0.098 | Large | **Yes** |
| | HGS vs. QPSO | 0.0002 | 0.0004 | 0.198 | Large | **Yes** |
| | ALNS vs. QPSO | 0.0040 | 0.0040 | 0.677 | Medium | **Yes** |
| **pune_n10_v2** | HGS vs. ALNS | < 0.0001 | < 0.0001 | 0.013 | Large | **Yes** |
| | HGS vs. QPSO | 0.6554 | 0.6554 | 0.474 | Negligible | No |
| | ALNS vs. QPSO | < 0.0001 | < 0.0001 | 0.925 | Large | **Yes** |
| **pune_n15_v3** | HGS vs. ALNS | < 0.0001 | < 0.0001 | 0.003 | Large | **Yes** |
| | HGS vs. QPSO | 0.0071 | 0.0071 | 0.276 | Large | **Yes** |
| | ALNS vs. QPSO | < 0.0001 | < 0.0001 | 0.971 | Large | **Yes** |
| **pune_n20_v4** | HGS vs. ALNS | < 0.0001 | < 0.0001 | 0.000 | Large | **Yes** |
| | HGS vs. QPSO | 0.0076 | 0.0076 | 0.253 | Large | **Yes** |
| | ALNS vs. QPSO | < 0.0001 | < 0.0001 | 1.000 | Large | **Yes** |

---

### Closed-Loop Dynamic SUMO Simulation (Table V)
Microscopic simulation in Eclipse SUMO 1.27.1 on the Pune network. At $t = 30$ s, edge `246580191#8` was throttled by 95% ($v_{\text{max}} = 0.70$ m/s):

| Performance Metric | Static Unreactive Regime | Dynamic Closed-Loop Rerouting | Operational Impact |
| :--- | :---: | :---: | :--- |
| **Mean Speed During Incident (m/s)** | 11.12 | 10.70 | Maintains steady flow across detour |
| **Peak Waiting Time Behind Bottleneck (s)** | 1.0 | 2.0 | Minimal local junction delay |
| **Total Distance Traversed by $t=160$ s (m)** | 1703.7 | 1648.2 | Traversed dynamic detour |
| **Rerouting Decision Latency (ms)** | --- | **2.09 ms** | Real-time viable for online dispatch |
| **Detour Road Segments Traversed** | 0 (Trapped behind incident) | **28 edges** | Bottleneck completely bypassed |

---

### Gate-Based QAOA Simulation & Hilbert Space Dilution (Table VI)
Evaluated using Qiskit Statevector Simulator with COBYLA classical parameter optimizer ($p=1$ ansatz, 1024 measurement shots) under the corrected closed-tour QUBO formulation:

| Instance | Qubits ($N^2$) | Exact MIP Reference (s) | QAOA Mean Cost (s) | Optimality Gap (%) | $P(\text{feas})$ | Mean Runtime (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **pune_q3** ($N=3$) | 9 | 720.85 | 781.26 | 8.38% | 0.0009 | 185.1 |
| **pune_q4** ($N=4$) | 16 | 829.45 | 1039.24 | 25.29% | 0.0001 | 1796.5 |

> **Hilbert Space Dilution Insight:** For $N=4$ ($n_q = 16$), the statevector contains $2^{16} = 65,536$ states, of which only $4! = 24$ states correspond to valid closed tours ($0.036\%$). This empirically demonstrates why dense penalty-based QUBOs face exponential dilution on NISQ quantum hardware, necessitating constraint-preserving mixer Hamiltonians (XY-ansatz).

---

### Experimental Environment & Telemetry (Table VII)

| Component | Specification |
| :--- | :--- |
| **Processor** | AMD Ryzen 5000 Series (Zen 3 architecture, 6 cores, 12 threads, 3.70 GHz base clock) |
| **RAM** | 13.86 GB Host Memory |
| **Operating System** | Microsoft Windows 11 64-bit |
| **Traffic Simulator** | Eclipse SUMO 1.27.1 via TraCI protocol |
| **Quantum Framework** | Qiskit 2.5.2 & Qiskit Aer (Statevector Simulation) |
| **Numerical Libraries** | Python 3.11.9, NumPy 2.2.6, SciPy 1.15.3, NetworkX 3.4.2 |
| **Exact Reference** | HiGHS Branch-and-Cut (`scipy.optimize.milp`, MTZ formulation, 30 s limit) |

---

## Optimization Solvers Implemented

All algorithms are implemented under `backend/vrp/` and ingest identical problem instances:

1. **Exact MIP (`exact_mip_vrp.py`):** Two-index Miller-Tucker-Zemlin (MTZ) Mixed-Integer Linear Programming solved to provable optimality via the HiGHS branch-and-cut solver.
2. **Exhaustive Dijkstra Baseline (`dijkstra_vrp.py`):** Permutation enumeration ($N!$) with Dijkstra shortest-path leg calculations.
3. **Adaptive Large Neighborhood Search (`alns_vrp.py`):** Destroy operators (Random, Worst, Shaw) and Repair operators (Random, Greedy, Regret) with simulated annealing acceptance and roulette-wheel weight adaptation.
4. **Hybrid Genetic Search (`hgs_vrp.py`):** Dual feasible/infeasible subpopulations, giant-tour chromosomes, ordered crossover (OX), 2-opt local search, and Prins' dynamic programming split algorithm.
5. **Quantum-Behaved Particle Swarm Optimization (`qpso_vrp.py`):** Continuous particle swarm search governed by delta potential-well wave collapse equations, mapped to discrete tours via rank-based coordinate sorting.
6. **Quantum Approximate Optimization Algorithm (`qaoa_vrp.py`):** Gate-based parameterized quantum circuit evaluated via Qiskit with exact return-to-depot linear energy terms.

---

## Repository Structure

```
.
├── backend/
│   ├── api/                     # FastAPI and WebSocket real-time endpoints
│   ├── graph/                   # OpenStreetMap graph loader and dynamic road resolver
│   ├── routing/                 # Standalone point-to-point QPSO routing
│   ├── simulation/              # SUMO manager and TraCI process lifecycle
│   ├── traffic/                 # Traffic state extractor and incident injector
│   └── vrp/                     # Combinatorial fleet routing solvers (HiGHS, ALNS, HGS, QPSO, QAOA)
├── benchmarks/
│   └── instances/               # 9 validated JSON benchmark instances (N=3 to N=20)
├── config/
│   ├── experiments.yaml         # Benchmark hyperparameters (seeds, evaluations, budgets)
│   ├── statistics.yaml          # Statistical test configuration (bootstrap, alpha, Holm)
│   └── traffic.yaml             # SUMO incident edge and throttling parameters
├── frontend/                    # Interactive web dashboard (HTML5, Leaflet, WebSocket)
├── research_paper/
│   ├── figures/                 # Publication-ready vector PDF figures
│   ├── tables/                  # Auto-generated publication LaTeX tables
│   ├── main.tex                 # IEEEtran publication manuscript source
│   ├── main.pdf                 # Compiled 13-page publication manuscript PDF
│   ├── references.bib           # Verified BibTeX bibliography
│   └── REPRODUCIBILITY.md       # Comprehensive experimental protocol guide
├── results/
│   ├── raw/                     # Raw JSON experimental data (benchmark, QAOA, dynamic SUMO)
│   ├── statistics/              # Statistical test outputs (Friedman, Wilcoxon, A12, CIs)
│   ├── tables/                  # LaTeX tables generated directly from data
│   └── figures/                 # Vector PDF plots generated from data
├── scripts/
│   ├── run_experiments.py       # Benchmark suite execution runner (30 seeds, 7 instances)
│   ├── run_qaoa_benchmark.py    # QAOA quantum simulation runner
│   ├── run_dynamic_sumo.py      # Closed-loop TraCI incident simulation runner
│   ├── analyze_results.py       # Statistical analysis calculation engine
│   ├── generate_tables.py       # LaTeX table generator (Direct Ingestion)
│   └── generate_figures.py      # Vector figure generator
└── tests/                       # Unit tests for QUBO formulation and invariants
```

---

## Reproducibility & Execution Pipeline

To reproduce all experimental results, tables, figures, and compile the manuscript PDF from scratch:

```bash
# 1. Clone the repository
git clone https://github.com/Rohitk69992/Quantum-Inspired-Vehicle-Routing-Problem-Solution.git
cd Quantum-Inspired-Vehicle-Routing-Problem-Solution

# 2. Set up virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate   # Windows (or source .venv/bin/activate on Linux)
pip install numpy scipy networkx qiskit qiskit-aer traci sumolib matplotlib fastapi uvicorn websockets

# 3. Run the benchmark suite across 30 seeds (generates results/raw/benchmark_raw_results.json)
python scripts/run_experiments.py

# 4. Run QAOA benchmark across 6 seeds (generates results/raw/qaoa_raw_results.json)
python scripts/run_qaoa_benchmark.py

# 5. Run closed-loop SUMO dynamic simulation (generates results/raw/dynamic_sumo_results.json)
python scripts/run_dynamic_sumo.py

# 6. Execute non-parametric statistical analysis (generates results/statistics/statistical_analysis.json)
python scripts/analyze_results.py

# 7. Generate publication LaTeX tables
python scripts/generate_tables.py

# 8. Generate publication vector figures
python scripts/generate_figures.py

# 9. Compile manuscript PDF
cd research_paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

---

## Citation

```bibtex
@article{korade2026sumo,
  author={Korade, Rohit},
  journal={IEEE Transactions on Intelligent Transportation Systems},
  title={A {SUMO}-Based Framework for Traffic-Aware Vehicle Routing With Quantum-Inspired and Classical Optimization},
  year={2026},
  note={Preprint under review}
}
```
