import numpy as np
import logging

logger = logging.getLogger(__name__)

def validate_inputs(coverage_matrix, demand_weights, p_stations) -> None:
    """Validate optimization inputs for consistency and sanity."""
    if coverage_matrix.ndim != 2:
        raise ValueError(f"Coverage matrix must be 2D, got {coverage_matrix.ndim}D")
    
    n_demand, n_candidates = coverage_matrix.shape
    
    if len(demand_weights) != n_demand:
        raise ValueError(f"Demand weights ({len(demand_weights)}) must match rows in coverage matrix ({n_demand})")
    
    if p_stations <= 0 or p_stations > n_candidates:
        raise ValueError(f"Invalid station budget: p={p_stations} must be positive and <= n_candidates ({n_candidates})")
    
    if np.any(demand_weights < 0):
        raise ValueError("Demand weights cannot be negative")

def compute_gap_closure(baseline_coverage_pct, optimized_coverage_pct) -> dict:
    """
    Compute the percentage of the coverage gap that was closed.
    
    Formula:
    Gap before = 1 - baseline_coverage
    Gap after = 1 - optimized_coverage
    Gap closed = Gap before - Gap after
    Closure % = Gap closed / Gap before
    """
    gap_before = 1.0 - baseline_coverage_pct
    gap_after = 1.0 - optimized_coverage_pct
    
    # Avoid division by zero if baseline is already 100%
    if gap_before <= 1e-9:
        pct_closed = 1.0 if gap_after <= 1e-9 else 0.0
    else:
        pct_closed = (gap_before - gap_after) / gap_before

    # Log the arithmetic for verification
    logger.info(f"Gap Closure Logic:")
    logger.info(f"  Baseline Coverage: {baseline_coverage_pct:.2%}")
    logger.info(f"  Optimized Coverage: {optimized_coverage_pct:.2%}")
    logger.info(f"  Gap Before: {gap_before:.2%}")
    logger.info(f"  Gap After: {gap_after:.2%}")
    logger.info(f"  Percent Gap Closed: {pct_closed:.2%}")

    return {
        "gap_before": float(gap_before),
        "gap_after": float(gap_after),
        "gap_closed": float(gap_before - gap_after),
        "pct_closed": float(pct_closed)
    }
