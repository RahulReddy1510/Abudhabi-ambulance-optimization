import numpy as np
import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimization.mclp_model import MCLPModel

def test_mclp_formulation_small():
    """Test MCLP on a simple 2x2 instance."""
    # 2 demand nodes, 2 candidates
    # Node 0 covered by 0
    # Node 1 covered by 1
    cov = np.array([[1, 0], [0, 1]])
    weights = np.array([100, 50])
    
    # Budget of 1 station -> should pick station 0 because weight 100 > 50
    model = MCLPModel(cov, weights, p_stations=1, p_vehicles=1)
    results = model.solve()
    
    assert results["n_stations_used"] == 1
    assert 0 in results["open_stations"]
    assert results["coverage_pct"] == 100 / 150

def test_mclp_budget_constraint():
    """Test that station budget is strictly respected."""
    np.random.seed(42)
    cov = np.ones((10, 10)) # Everyone covers everyone
    weights = np.ones(10)
    
    p = 3
    model = MCLPModel(cov, weights, p_stations=p)
    results = model.solve()
    
    assert results["n_stations_used"] <= p
    assert results["coverage_pct"] == 1.0

def test_mclp_solver_consistency():
    """Ensures solver type is correctly detected (PuLP in CI)."""
    model = MCLPModel(np.ones((2, 2)), np.ones(2), p_stations=1)
    assert model.solver_type in ["gurobi", "pulp"]
    
    if os.environ.get("USE_PULP") == "1":
        assert model.solver_type == "pulp"
