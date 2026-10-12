"""
stages package for IEEE T-ITS Reproducibility Pipeline.
Provides modular, callable stages for benchmark verification, execution,
table generation, claims synthesis, and paper verification.
"""

from .stage_audit import run_audit_stage
from .stage_alns import run_alns_stage
from .stage_budget import run_budget_stage
from .stage_mip import run_mip_stage
from .stage_reroute import run_reroute_stage
from .stage_congestion import run_congestion_stage
from .stage_qaoa import run_qaoa_stage
from .stage_pyvrp import run_pyvrp_stage
from .stage_tables import run_tables_stage
from .stage_figures import run_figures_stage
from .stage_claims import run_claims_stage
from .stage_verify import run_verify_stage
