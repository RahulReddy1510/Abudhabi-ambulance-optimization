import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimization.constraints import compute_gap_closure

def test_gap_closure_requirement():
    """
    Verify the critical claim: 
    baseline=0.60, optimized=0.948 gives gap_closure = 87%.
    """
    baseline_pct = 0.60
    optimized_pct = 0.948
    
    results = compute_gap_closure(baseline_pct, optimized_pct)
    
    # Gap Before: 1.0 - 0.60 = 0.40
    # Gap After: 1.0 - 0.948 = 0.052
    # Gap Closed: 0.40 - 0.052 = 0.348
    # Closure: 0.348 / 0.40 = 0.87 (Exactly)
    
    assert abs(results["pct_closed"] - 0.87) < 1e-6
    print(f"\nGap Closure Verified: {results['pct_closed']:.2%}")

def test_perfect_closure():
    """Test closure when baseline is covered."""
    res = compute_gap_closure(0.5, 1.0)
    assert res["pct_closed"] == 1.0

def test_no_improvement():
    """Test closure when no progress is made."""
    res = compute_gap_closure(0.6, 0.6)
    assert res["pct_closed"] == 0.0
