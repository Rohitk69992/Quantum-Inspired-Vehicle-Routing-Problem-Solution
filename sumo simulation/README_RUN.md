# README_RUN: Reproducing the IEEE T-ITS Paper

This document describes how to execute the end-to-end reproducibility pipeline for:
*"A SUMO-Based Framework for Traffic-Aware Vehicle Routing With Quantum-Inspired and Classical Optimization"*
**Author:** Rohit Korade (ISBM College of Engineering, Pune, India)
**Target Venue:** IEEE Transactions on Intelligent Transportation Systems

---

## 1. Prerequisites

### Software Dependencies
- **Python**: 3.11.x (tested on Python 3.11.9)
- **LaTeX**: MiKTeX or TeX Live providing `pdflatex` and `bibtex`
- **Shell**: Bash (Git Bash, WSL, or MSYS2 on Windows; native bash on Linux/macOS)
- **Eclipse SUMO**: 1.27.x (providing `sumolib` and `traci`)

### Python Dependencies
Install required packages via `pip`:
```bash
pip install -r requirements.txt
```

---

## 2. Single-Command Reproduction

To audit the repository, synthesize outcome-robust claims and macros, generate all publication tables and figures, verify all 13 mathematical and empirical invariants, and compile `main.pdf`, run:

```bash
bash build.sh --quick
```

### Build Options
- `bash build.sh --quick`: (Default) Fast audit and verification using verified raw experimental outputs (~4 seconds).
- `bash build.sh --full`: Comprehensive execution including solver capacity unit tests and live simulation checks.
- `bash build.sh --stages <stage_names...>`: Execute specific modular stages. Available stages:
  - `audit`: Verifies raw JSON files and schema integrity.
  - `alns`: Verifies ALNS capacity mechanisms and tests the capacity patch.
  - `budget`: Verifies standardized 1,000-evaluation budget parameters across solvers.
  - `mip`: Verifies exact HiGHS branch-and-cut MTZ reference optima.
  - `reroute`: Verifies closed-loop SUMO dynamic rerouting telemetry.
  - `congestion`: Verifies time-varying weight formulas and defensive lower bounds.
  - `qaoa`: Verifies exact closed-tour position-variable QUBO formulation and scaling limits.
  - `pyvrp`: Audits state-of-the-art solver integration status.
  - `tables`: Generates LaTeX tables in `results/tables/` and `research_paper/tables/`.
  - `figures`: Renders vector PDF figures and high-resolution PNGs in `research_paper/figures/`.
  - `claims`: Synthesizes `macros_generated.tex` and `claims_generated.tex`.
  - `verify`: Runs `verify_paper.py` to check invariants V1 through V13.

---

## 3. Automated Invariant Verifier

To run the standalone verifier checking mathematical, statistical, and textual truth without recompiling the PDF:

```bash
python verify_paper.py
```

The verifier strictly enforces 13 invariants:
- **V1**: Raw result files existence and schema validation.
- **V2**: Table cells in `tab_main_benchmark.tex` strictly match raw JSON results.
- **V3**: Permutation baseline gap on $N=8$ is correctly reported as $4.98\%$.
- **V4**: Non-parametric Friedman test statistics ($\chi_F^2 = 3.71, p = 0.156$) match statistical calculations.
- **V5**: Pairwise Holm-adjusted $p$-values and Vargha-Delaney effect sizes match.
- **V6**: SUMO Table V metrics have mathematically correct signs ($-3.8\%$, $+100.0\%$, $-55.5$ m) with no malformed syntax.
- **V7**: QAOA sampling probabilities ($0.0009$ and $0.0001$) and gaps match statevector outputs.
- **V8**: Hilbert space feasible fractions ($6/512 = 1.17\%$ and $24/65536 = 0.037\%$) are mathematically accurate.
- **V9**: Vidal 2022 reference title matches DOI `10.1016/j.cor.2021.105643`.
- **V10**: Exclusion of promotional adjectives in manuscript text.
- **V11**: Full author name ("Rohit Korade") and affiliation ("ISBM College of Engineering, Pune, India").
- **V12**: ALNS capacity fix patch and unit test files are verified.
- **V13**: All citations in `main.tex` are defined in `references.bib`.

---

## 4. Running Unit Tests

To run unit tests verifying the ALNS capacity penalty mechanism:

```bash
pytest tests/test_alns_capacity.py -v
```

---

## 5. Artifact Outputs

- **Manuscript PDF**: `research_paper/main.pdf`
- **Generated Tables**: `research_paper/tables/*.tex`
- **Generated Figures**: `research_paper/figures/*.pdf` and `*.png`
- **Generated Macros**: `research_paper/macros_generated.tex`
- **Generated Claims**: `research_paper/claims_generated.tex`
- **Build Log**: `build.log`
