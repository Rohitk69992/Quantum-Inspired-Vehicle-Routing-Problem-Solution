"""
stages/stage_tables.py
Stage: tables
Generates all publication-ready LaTeX tables from experimental and statistical data.
"""

import os
import sys
from typing import Dict, Any
from scripts.make_tables import generate_all_tables


def run_tables_stage(config: Dict[str, Any], quick_mode: bool = True) -> bool:
    print("\n" + "=" * 70)
    print("STAGE: TABLES - Generating LaTeX Tables")
    print("=" * 70)

    generate_all_tables()
    print("  [PASS] Tables stage completed successfully.")
    return True
