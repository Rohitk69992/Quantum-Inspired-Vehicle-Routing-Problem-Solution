"""
stages/stage_claims.py
Stage: claims
Generates outcome-robust claims and macros directly from raw experimental data.
"""

import os
import sys
from typing import Dict, Any
from claims_engine import generate_claims_and_macros


def run_claims_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: CLAIMS - Synthesizing Outcome-Robust Macros & Claims")
    print("=" * 70)

    generate_claims_and_macros()
    print("  [PASS] Claims stage completed successfully.")
    return True
