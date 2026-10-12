#!/usr/bin/env python3
"""
run_all.py - Complete Pipeline Orchestrator for IEEE T-ITS Reproducibility

Usage:
    python run_all.py --quick
    python run_all.py --full
    python run_all.py --stages audit alns budget mip reroute congestion qaoa pyvrp tables figures claims verify
"""

import os
import sys
import argparse
import yaml
import time
from typing import List, Dict, Any

from stages.stage_audit import run_audit_stage
from stages.stage_alns import run_alns_stage
from stages.stage_budget import run_budget_stage
from stages.stage_mip import run_mip_stage
from stages.stage_reroute import run_reroute_stage
from stages.stage_congestion import run_congestion_stage
from stages.stage_qaoa import run_qaoa_stage
from stages.stage_pyvrp import run_pyvrp_stage
from stages.stage_tables import run_tables_stage
from stages.stage_figures import run_figures_stage
from stages.stage_claims import run_claims_stage
from stages.stage_verify import run_verify_stage


ALL_STAGES = [
    ("audit", run_audit_stage),
    ("alns", run_alns_stage),
    ("budget", run_budget_stage),
    ("mip", run_mip_stage),
    ("reroute", run_reroute_stage),
    ("congestion", run_congestion_stage),
    ("qaoa", run_qaoa_stage),
    ("pyvrp", run_pyvrp_stage),
    ("tables", run_tables_stage),
    ("figures", run_figures_stage),
    ("claims", run_claims_stage),
    ("verify", run_verify_stage),
]


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="IEEE T-ITS Reproducibility Pipeline Orchestrator")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--quick", action="store_true", default=False, help="Fast execution using verified raw data")
    parser.add_argument("--full", action="store_true", default=False, help="Full end-to-end execution")
    parser.add_argument("--stages", nargs="+", choices=[s[0] for s in ALL_STAGES], help="Execute specific stages")

    args = parser.parse_args()

    # Default to quick mode if neither quick nor full is explicitly given
    quick_mode = not args.full

    config = load_config(args.config)
    stages_to_run = ALL_STAGES

    if args.stages:
        stage_names = set(args.stages)
        stages_to_run = [s for s in ALL_STAGES if s[0] in stage_names]

    print("=" * 80)
    print("IEEE T-ITS REPRODUCIBILITY PIPELINE: STARTING EXECUTION")
    print(f"Mode: {'QUICK' if quick_mode else 'FULL'}")
    print(f"Stages to execute: {[s[0] for s in stages_to_run]}")
    print("=" * 80)

    start_total = time.perf_counter()
    executed_count = 0

    for name, stage_fn in stages_to_run:
        stage_start = time.perf_counter()
        try:
            success = stage_fn(config=config, quick_mode=quick_mode)
            if not success:
                print(f"\n[ERROR] Pipeline aborted: Stage '{name}' returned failure.")
                sys.exit(1)
            stage_elapsed = time.perf_counter() - stage_start
            print(f"--> Stage '{name}' completed in {stage_elapsed:.2f} s")
            executed_count += 1
        except Exception as e:
            print(f"\n[ERROR] Exception in stage '{name}': {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    total_elapsed = time.perf_counter() - start_total
    print("\n" + "=" * 80)
    print(f"PIPELINE COMPLETED SUCCESSFULLY: {executed_count} stages executed in {total_elapsed:.2f} s")
    print("=" * 80)


if __name__ == "__main__":
    main()
