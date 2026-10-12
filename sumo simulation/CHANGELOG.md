# CHANGELOG: IEEE T-ITS Revision Audit Trail

This changelog records all modifications made to the manuscript, codebase, statistical pipeline, and configuration in accordance with Rule R1 (Truth hierarchy: raw results > code > manuscript).

---

## 1. Data Integrity and Reporting Corrections ([A1]–[A11])

- **[A1] N=8 Permutation Baseline Gap**:
  - *Previous*: Table II printed cost as 1149.98 with an optimality gap of `0.00%`.
  - *Correction*: The true gap relative to exact HiGHS reference ($1095.40$) is $+4.98\%$. The gap calculation in `scripts/make_tables.py` now computes $((1149.98 - 1095.40) / 1095.40) \times 100 = 4.98\%$. Furthermore, because $N > 7$ is evaluated by 2-opt + 50 random permutations in `backend/vrp/dijkstra_vrp.py`, the solver label on $N=8$ is corrected to "Permutation Heuristic".
- **[A2] Graph Weight Footnote**:
  - *Previous*: Table II footnote claimed costs were evaluated on dynamic graph $G(t)$.
  - *Correction*: Clarified that quantitative multi-instance benchmarks used static free-flow travel times on $G_0$ ($\alpha=1.0, \beta=0.0, \gamma=0.0, \mu=1.0$).
- **[A3] Overstated Optimality Gap Claims**:
  - *Previous*: Abstract and discussion claimed all metaheuristics achieve mean gaps $\le 0.43\%$ or $\le 0.5\%$.
  - *Correction*: Updated claims to reflect instance-specific reality: mean gap $\le 0.43\%$ on $N=5$, but $1.39\%$ for QPSO on $N=8$, and up to $3.54\%$ on binding instances.
- **[A4] Statistical Text vs. Table IV Numbers**:
  - *Previous*: Section VIII-C quoted $p_{\text{adj}} = 0.0003, \hat{A}_{12} = 0.88$ for ALNS vs HGS on $N=10$, while Table IV listed $p < 0.0001, \hat{A}_{12} = 0.013$.
  - *Correction*: Synchronized text with Table IV values: $p_{\text{adj}} < 0.0001$, $\hat{A}_{12} = 0.013$ for HGS vs. ALNS (indicating ALNS superiority under lower-cost ranking convention).
- **[A5] Dynamic SUMO Table Signs & LaTeX Math Symbols**:
  - *Previous*: Table V displayed malformed symbols `+-3.8%`, `--100.0%`, and `+-55.5 m`.
  - *Correction*: Corrected signs to $-3.8\%$ for mean speed, $+100.0\%$ for peak waiting time increase, and $-55.5$ m for distance delta. Header updated to "Delta ($\Delta$)".
- **[A6] QAOA Feasible State Space Fractions**:
  - *Previous*: Claimed $4! = 24$ states is $0.036\%$ of the $2^{16}$ space.
  - *Correction*: Corrected to $24 / 65536 = 0.037\%$ ($0.0366\%$), and documented $N=3$ space as $6 / 512 = 1.17\%$.
- **[A7] Feasibility Formatting Inconsistencies**:
  - *Previous*: Table II mixed `100`, `100.0`, and `37`.
  - *Correction*: Standardized to one decimal place across all rows (`100.0` and `36.7`).
- **[A8] Exact Solver Transparency**:
  - *Correction*: Documented HiGHS branch-and-cut MTZ implementation via `scipy.optimize.milp` with formal citations.
- **[A9] Multi-Vehicle Formulation**:
  - *Correction*: Explicitly formalized vehicle capacities $C_k$, cumulative load constraints, and flow conservation.
- **[A10] Hardware Telemetry Transparency**:
  - *Correction*: Documented 2011 MHz base telemetry frequency measured on AMD Ryzen Zen 3 system alongside manufacturer specifications.
- **[A11] Vidal 2022 Reference Title**:
  - *Previous*: Cited as *"Hybrid genetic search for the CVRP: 22 years later"*.
  - *Correction*: Corrected title to *"Hybrid Genetic Search for the CVRP: Open-Source Implementation and SWAP\* Neighborhood"* (DOI: 10.1016/j.cor.2021.105643). Added missing citations for HiGHS, SciPy, NetworkX, Qiskit, and SUMO.

---

## 2. Algorithmic and Methodological Audits ([B1]–[B9])

- **[B1] Permutation Heuristic Baseline Renaming**: Renamed solver on $N=8$ from "Exhaustive Baseline" to "Permutation Heuristic".
- **[B2] Evaluation Budget Standardization**: Verified 1,000-evaluation budget across ALNS, HGS, and QPSO.
- **[B3] ALNS Feasibility Drop Fix**:
  - Diagnosed cause: lack of capacity penalty in `solution_cost` and unpenalized append fallback in repair heuristics.
  - Created `patches/alns_capacity.diff` and verified with `tests/test_alns_capacity.py` that patched ALNS restores 100% feasibility.
- **[B4] HGS Configuration Audit**: Aligned manuscript parameter reporting ($\mu=20, \lambda=15, T_{\max}=50$).
- **[B5] QPSO Rank-Discretization Ties**: Verified argsort discretization with deterministic index preservation.
- **[B6] QAOA Return-to-Depot Term**: Formulated exact closed-tour return leg $\sum_{i=1}^N c_{i,0} x_{i, N-1}$.
- **[B7] QAOA Classical Simulation Transparency**: Explicitly stated statevector simulation is a classical test harness without quantum advantage.
- **[B8] Dynamic Rerouting Scope**: Accurately reported single-vehicle incident demonstration with 2.09 ms algorithmic latency and 28 detour segments.
- **[B9] Friedman Test Algorithm Cohort**: Confirmed omnibus test evaluates $\{ \text{HGS}, \text{ALNS}, \text{QPSO} \}$ across all 7 benchmark instances.

---

## 3. Pipeline Automation and Code Quality ([C1]–[C11])

- **[C1] Centralized Configuration**: Created `config.yaml`.
- **[C2] Evaluation Tracking**: Standardized objective evaluation accounting.
- **[C3] Reproducibility Pipeline**: Created `stages/` modular pipeline.
- **[C4] Automated Table Generation**: Created `scripts/make_tables.py`.
- **[C5] Automated Figure Generation**: Created `scripts/make_figures.py`.
- **[C6] Notation Disambiguation**: Resolved symbol collisions between $\mu_e(t)$ (incident multiplier), $\mu$ (HGS population size), and $n_{\text{elite}}$.
- **[C7] Clean Figure Regeneration**: Rendered vector PDF figures and high-resolution PNGs.
- **[C8] Empty Subsection Elimination**: Removed empty subsection `\subsection{Solution Quality and Algorithm Convergence}`.
- **[C9] Codebase Hygiene**: Clean imports, strict type annotations, defensive checks.
- **[C10] Single Build Entrypoint**: Created `build.sh` supporting `--quick` and `--full`.
- **[C11] Automated Verifier**: Created `verify_paper.py` enforcing invariants V1–V13.

---

## 4. Tone and Manuscript Presentation ([D1]–[D7], [E1]–[E4])

- **[D1]–[D7] Evidence-Linked Claims**: Replaced hardcoded prose claims with outcome-robust macros linked to raw JSON results.
- **Tone Scrub**: Removed promotional phrasing ("unbroken evidence chain", "verified hardware telemetry", "rigorous", "defensible").
- **Author Identity**: Preserved author name "Rohit Korade" and affiliation "Department of Artificial Intelligence and Data Science, ISBM College of Engineering, Pune, India".
