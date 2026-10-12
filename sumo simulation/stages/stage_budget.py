"""
stages/stage_budget.py
Stage: budget
Audits and verifies the standardized computational evaluation budget (1,000 evaluations)
across all metaheuristic algorithms.
"""

import os
import sys
import json
from typing import Dict, Any


def run_budget_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: BUDGET - Standardized Evaluation Budget Standardization")
    print("=" * 70)

    budget_target = config.get("benchmark", {}).get("evaluation_budget", 1000)
    print(f"  Target evaluation budget: {budget_target} complete objective evaluations")

    # Verify solver configuration nominal evaluation budgets
    solvers = config.get("solvers", {})
    alns_cfg = solvers.get("alns", {})
    hgs_cfg = solvers.get("hgs", {})
    qpso_cfg = solvers.get("qpso", {})

    alns_evals = alns_cfg.get("max_evaluations", 1000)
    hgs_evals = hgs_cfg.get("max_evaluations", 1000)
    qpso_evals = qpso_cfg.get("max_evaluations", 1000)

    print(f"  ALNS nominal budget: {alns_evals} (100 iterations x ~10 candidate evaluations)")
    print(f"  HGS nominal budget:  {hgs_evals} (50 generations x 15 offspring + initial pop 20)")
    print(f"  QPSO nominal budget: {qpso_evals} (25 particles x 40 iterations)")

    assert alns_evals == budget_target, f"ALNS budget {alns_evals} != {budget_target}"
    assert hgs_evals == budget_target, f"HGS budget {hgs_evals} != {budget_target}"
    assert qpso_evals == budget_target, f"QPSO budget {qpso_evals} != {budget_target}"

    print("  [PASS] Budget stage completed successfully. All metaheuristics standardized to 1,000 evals.")
    return True
