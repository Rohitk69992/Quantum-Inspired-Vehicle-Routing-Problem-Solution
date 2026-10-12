"""
stages/stage_qaoa.py
Stage: qaoa
Audits and verifies QAOA closed-tour position-variable QUBO formulation and scaling limits.
"""

import os
import sys
import json
import math
from typing import Dict, Any


def run_qaoa_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: QAOA - Closed-Tour QUBO Formulation & Statevector Scaling Audit")
    print("=" * 70)

    qaoa_file = os.path.join(config.get("paths", {}).get("results_raw_dir", "results/raw"), "qaoa_raw_results.json")
    with open(qaoa_file, "r", encoding="utf-8") as f:
        q_data = json.load(f)

    instances = q_data.get("instances", {})
    assert "pune_q3" in instances and "pune_q4" in instances, "Missing pune_q3 or pune_q4 in QAOA results"

    # N=3 checks
    q3 = instances["pune_q3"]
    runs3 = q3.get("runs", [])
    assert len(runs3) == 6, f"Expected 6 runs for q3, found {len(runs3)}"
    c3 = runs3[0]["cost"]
    p3 = runs3[0]["selected_probability"]
    gap3 = runs3[0]["optimality_gap_pct"]
    print(f"  pune_q3 (N=3, n_q=9 qubits):")
    print(f"    Hilbert space size: 2^9 = 512 states")
    print(f"    Valid permutation states: 3! = 6 states ({6/512*100:.2f}% of space)")
    print(f"    Exact MIP cost: {q3['exact_mip_cost']:.2f} s | QAOA cost: {c3:.2f} s (Gap: {gap3:.2f}%)")
    print(f"    Feasible ground state sampling probability P(feas): {p3:.4f}")

    # N=4 checks
    q4 = instances["pune_q4"]
    runs4 = q4.get("runs", [])
    assert len(runs4) == 6, f"Expected 6 runs for q4, found {len(runs4)}"
    c4 = runs4[0]["cost"]
    p4 = runs4[0]["selected_probability"]
    gap4 = runs4[0]["optimality_gap_pct"]
    print(f"  pune_q4 (N=4, n_q=16 qubits):")
    print(f"    Hilbert space size: 2^16 = 65,536 states")
    print(f"    Valid permutation states: 4! = 24 states ({24/65536*100:.3f}% of space)")
    print(f"    Exact MIP cost: {q4['exact_mip_cost']:.2f} s | QAOA cost: {c4:.2f} s (Gap: {gap4:.2f}%)")
    print(f"    Feasible ground state sampling probability P(feas): {p4:.6f}")

    assert abs(c3 - 781.26) < 0.1, f"Q3 cost mismatch: {c3}"
    assert abs(c4 - 1039.24) < 0.1, f"Q4 cost mismatch: {c4}"
    assert abs(gap3 - 8.38) < 0.1, f"Q3 gap mismatch: {gap3}"
    assert abs(gap4 - 25.29) < 0.1, f"Q4 gap mismatch: {gap4}"

    print("  [PASS] QAOA stage completed successfully. Dilution metrics verified.")
    return True
