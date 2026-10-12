"""
stages/stage_figures.py
Stage: figures
Generates all publication-ready vector PDF and PNG figures.
"""

import os
import sys
from typing import Dict, Any
from scripts.make_figures import generate_all_figures


def run_figures_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: FIGURES - Generating Figures")
    print("=" * 70)

    generate_all_figures()
    print("  [PASS] Figures stage completed successfully.")
    return True
