"""
stages/stage_pyvrp.py
Stage: pyvrp
Audits PyVRP baseline integration, checking availability and documenting baseline status.
"""

import os
import sys
from typing import Dict, Any


def run_pyvrp_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: PYVRP - SOTA Open-Source Solver Audit")
    print("=" * 70)

    try:
        import pyvrp
        print(f"  [FOUND] PyVRP version {getattr(pyvrp, '__version__', 'unknown')} is installed.")
        pyvrp_available = True
    except ImportError:
        print("  [INFO] PyVRP not installed in current Python environment.")
        print("  [NOTE] HGS implementation in repository operates as the native pure-Python")
        print("         algorithmic reference using Vidal et al. principles (Prins DP Split).")
        pyvrp_available = False

    print("  [PASS] PyVRP stage completed.")
    return True
