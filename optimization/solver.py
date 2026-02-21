import os
import argparse
import json
import logging
import yaml
import geopandas as gpd
import numpy as np

from mclp_model import MCLPModel
from coverage_matrix import compute_travel_time_matrix, build_coverage_matrix, baseline_coverage_stats
from constraints import validate_inputs, compute_gap_closure

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    """Load optimization parameters from YAML."""
    if not os.path.exists(config_path):
        logger.warning(f"Config {config_path} not found. Using defaults.")
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_full_optimization(config_path=None, verbose=False):
    """
    Orchestrate the full optimization workflow:
    1. Load data
    2. Compute travel times and coverage
    3. Run MCLP model (Gurobi or PuLP)
    4. Compute gap closure
    5. Save results
    """
    # Load parameters
    params = {}
    if config_path:
        params = load_config(config_path)
    
    # Defaults
    opt_params = params.get("optimization", {})
    p_stations = opt_params.get("p_stations", 12)
    p_vehicles = opt_params.get("p_vehicles", 24)
    threshold = opt_params.get("response_threshold_min", 8.0)
    
    # Paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "synthetic")
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # 1. Load Synthetic Data
    logger.info("Loading synthetic data...")
    try:
        zones_gdf = gpd.read_file(os.path.join(data_dir, "zones.geojson"))
        demand_gdf = gpd.read_file(os.path.join(data_dir, "demand_nodes.geojson"))
        candidates_gdf = gpd.read_file(os.path.join(data_dir, "candidate_stations.geojson"))
        existing_gdf = gpd.read_file(os.path.join(data_dir, "existing_stations.geojson"))
    except Exception as e:
        logger.error(f"Failed to load data from {data_dir}. Run generate_synthetic_data.py first.")
        raise e
        
    # 2. Compute Coverage Matrix
    logger.info(f"Computing travel time matrix (threshold: {threshold} min)...")
    time_matrix = compute_travel_time_matrix(demand_gdf, candidates_gdf)
    cov_matrix = build_coverage_matrix(time_matrix, threshold)
    
    weights = demand_gdf.weight.values
    
    # 3. Compute Baseline Coverage
    # Identify indices of existing stations in the candidate set
    # In our synthetic generator, existing stations are often a subset or close to candidates
    # For baseline, we just use the existing_gdf directly against demand
    logger.info("Computing baseline coverage...")
    base_time_matrix = compute_travel_time_matrix(demand_gdf, existing_gdf)
    base_cov_matrix = build_coverage_matrix(base_time_matrix, threshold)
    
    # Baseline stats
    is_covered_base = np.any(base_cov_matrix, axis=1)
    base_pop = np.sum(weights[is_covered_base])
    total_pop = np.sum(weights)
    base_pct = base_pop / total_pop
    
    logger.info(f"Baseline Coverage: {base_pct:.2%}")
    
    # 4. Run Optimization
    logger.info(f"Running MCLP optimization (p={p_stations})...")
    validate_inputs(cov_matrix, weights, p_stations)
    
    model = MCLPModel(cov_matrix, weights, p_stations, p_vehicles, verbose=verbose)
    results = model.solve()
    
    # 5. Post-process and Calculate Gap Closure
    gap_results = compute_gap_closure(base_pct, results["coverage_pct"])
    
    # Merge results
    final_output = {
        **results,
        "baseline_coverage_pct": float(base_pct),
        "gap_closure_pct": float(gap_results["pct_closed"]),
        "total_population": int(total_pop),
        "params": {
            "p_stations": p_stations,
            "p_vehicles": p_vehicles,
            "threshold_min": threshold
        }
    }
    
    # 6. Save results
    output_path = os.path.join(results_dir, "optimization_results.json")
    with open(output_path, "w") as f:
        json.dump(final_output, f, indent=4)
        
    logger.info(f"Optimization complete. Results saved to {output_path}")
    logger.info(model.summary())
    logger.info(f"Gap Closure: {final_output['gap_closure_pct']:.2%}")
    
    return final_output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abu Dhabi Ambulance Optimization Solver")
    parser.add_argument("--config", type=str, help="Path to config YAML")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    run_full_optimization(args.config, args.verbose)
