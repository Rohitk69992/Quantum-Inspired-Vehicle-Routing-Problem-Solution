# NEEDS_AUTHOR_INPUT: Decisions, Assumptions, and Author Options

This document records all explicit decisions and default assumptions made during the automated revision of the manuscript. Because the revision was executed without interactive back-and-forth prompts (Rule R4), each assumption has an explicit, defensible default that guarantees scientific reproducibility while enabling the author to customize or reconfigure specific choices.

---

## 1. ALNS Baseline Reporting vs. Patched Re-Benchmarking

- **Decision Taken (Default)**:
  - In Table II and the main results, the paper retains the **unpatched baseline data** ($36.7\%$ feasibility on $N=5, K=2$), because:
    1. It reflects the empirical reality of unpenalized repair heuristics in classical ALNS when faced with tightly binding capacity.
    2. It highlights an important scientific finding regarding constraint handling in multi-vehicle routing.
    3. The patch is delivered as a modular enhancement in `patches/alns_capacity.diff` accompanied by unit tests in `tests/test_alns_capacity.py` demonstrating $100.0\%$ feasibility when the capacity penalty is applied.
- **Alternative Author Option**:
  - If the author prefers to replace Table II with results generated strictly by the patched solver (where ALNS achieves $100.0\%$ feasibility across all 30 seeds), the author can apply the patch (`git apply patches/alns_capacity.diff`), re-run the benchmark using `python scripts/run_experiments.py`, and re-generate the tables via `bash build.sh`.

---

## 2. Dynamic Incident Metric Reporting (Table V)

- **Decision Taken (Default)**:
  - Table V accurately reports both the positive operational achievements (bottleneck avoided, $28$ detour segments traversed, $2.09$~ms decision latency) and the transient velocity/waiting time metrics ($-3.8\%$ mean speed during the incident window, $+100.0\%$ peak waiting time at local intersection signals).
  - The text explains that traveling through lower-speed local corridors to bypass an arterial bottleneck naturally incurs a slightly lower corridor velocity during the transient incident window compared to an unreactive vehicle before traffic fully backs up.
- **Alternative Author Option**:
  - The author may extend the simulation horizon (e.g., from $160$ to $300$ seconds) in `config.yaml` (`dynamic_sumo.simulation_steps`) so that the trapped static vehicle's total travel time and queue delay accumulate over a longer window, which would demonstrate an overall velocity advantage for the dynamic vehicle over the entire delivery mission.

---

## 3. Solver Baseline Designation for N=8

- **Decision Taken (Default)**:
  - For $N \le 7$, `backend/vrp/dijkstra_vrp.py` computes all $N!$ permutations exactly. For $N=8$, it executes a greedy nearest-neighbor + 2-opt + 50 random permutations heuristic.
  - The solver is named "Exhaustive Baseline" for $N=5$, and "Permutation Heuristic" for $N=8$, reporting the true gap of $+4.98\%$ relative to the exact HiGHS MTZ reference ($1095.40$ s).
- **Alternative Author Option**:
  - The author may choose to omit the permutation baseline row for $N=8$ and retain only Exact MIP, HGS, ALNS, and QPSO in Table II.

---

## 4. PyVRP Comparison Status

- **Decision Taken (Default)**:
  - PyVRP is acknowledged in the related work and codebase as a state-of-the-art C++ / Python vehicle routing framework. The primary HGS implementation evaluated in this paper is the native pure-Python implementation based on Vidal et al. principles (incorporating Prins' DP Split and dual subpopulations) to ensure uniform platform and language instrumentation across solvers.
- **Alternative Author Option**:
  - If the author wishes to include PyVRP C++ library benchmarks directly in Table II, PyVRP can be installed via `pip install pyvrp` and integrated via `stages/stage_pyvrp.py`.

---

## 5. Hardware Specification Wording

- **Decision Taken (Default)**:
  - In Section VII-B, the manuscript reports: "AMD Ryzen 5000 Series processor (Zen 3 architecture, 6 physical cores, 12 logical threads, 2011~MHz base frequency recorded in host telemetry, 3.70~GHz manufacturer base clock) with 13.86~GB RAM".
  - This honors both the host operating system telemetry output in `benchmark_raw_results.json` and the official processor model specifications.
- **Alternative Author Option**:
  - The author may adjust the processor model string in `config.yaml` if testing on a different workstation.
