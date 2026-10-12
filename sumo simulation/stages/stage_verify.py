"""
stages/stage_verify.py
Stage: verify
Automated verifier checking invariants V1 through V13.
"""

import os
import sys
from typing import Dict, Any
from verify_paper import verify_all


def run_verify_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: VERIFY - Automated Manuscript Verification")
    print("=" * 70)

    success = verify_all()
    if not success:
        raise RuntimeError("Verification failed. See log output for failed invariants.")
    print("  [PASS] Verify stage completed successfully.")
    return True
