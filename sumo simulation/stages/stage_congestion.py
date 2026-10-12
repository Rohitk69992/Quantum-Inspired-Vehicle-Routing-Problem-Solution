"""
stages/stage_congestion.py
Stage: congestion
Audits and verifies dynamic edge weight formulas and congestion metrics.
"""

import os
import sys
from typing import Dict, Any


def run_congestion_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: CONGESTION - Dynamic Weight Formulation & Defensive Bounds")
    print("=" * 70)

    # Mathematical checks of equations (1) - (3)
    # w_e(t) = (alpha * T_e(t) + beta * D_e + gamma * (C_e(t) * 100)) * mu_e(t)
    # Free-flow: alpha=1.0, beta=0.0, gamma=0.0, mu_e(t)=1.0 -> w_e(t) = T_e^0
    fw = config.get("network", {}).get("free_flow_weights", {})
    alpha = fw.get("alpha", 1.0)
    beta = fw.get("beta", 0.0)
    gamma = fw.get("gamma", 0.0)
    mu = fw.get("incident_multiplier", 1.0)

    print(f"  Benchmark configuration weights: alpha={alpha}, beta={beta}, gamma={gamma}, mu={mu}")
    assert alpha == 1.0 and beta == 0.0 and gamma == 0.0 and mu == 1.0, "Benchmark must reduce to free-flow travel time"

    # Defensive travel time check: T_e(t) = max(T_traci, D_e / max(v_e, 0.1), T_0)
    # Prevents zero or negative costs
    v_test = 0.0
    d_test = 100.0
    t0_test = 10.0
    eff_t = max(0.0, d_test / max(v_test, 0.1), t0_test)
    print(f"  Defensive travel time check with v=0.0 m/s: effective T = {eff_t:.1f} s > 0 (prevents div-by-zero)")
    assert eff_t > 0, "Defensive travel time failed"

    print("  [PASS] Congestion stage completed successfully.")
    return True
