import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import logging

logger = logging.getLogger(__name__)

def project_to_utm(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Project GeoDataFrame to UTM Zone 40N (Abu Dhabi)."""
    return gdf.to_crs("EPSG:32640")

def compute_distance_matrix(points_a, points_b) -> np.ndarray:
    """Compute pairwise Euclidean distance in meters."""
    coords_a = np.array([(p.x, p.y) for p in points_a.geometry])
    coords_b = np.array([(p.x, p.y) for p in points_b.geometry])
    return cdist(coords_a, coords_b)

def compute_travel_time_matrix(demand_gdf, stations_gdf) -> np.ndarray:
    """
    Compute travel time in minutes.
    Assumes average speed of 65 km/h for the general model.
    """
    demand_utm = project_to_utm(demand_gdf)
    stations_utm = project_to_utm(stations_gdf)
    
    dist_m = compute_distance_matrix(demand_utm, stations_utm)
    dist_km = dist_m / 1000.0
    
    # Time in minutes = (distance in km / speed in km/h) * 60
    # Average speed 65 km/h
    time_min = (dist_km / 65.0) * 60.0
    
    return time_min.astype(np.float32)

def build_coverage_matrix(travel_time_matrix, threshold_min=8.0) -> np.ndarray:
    """Generate boolean matrix for coverage within threshold."""
    return (travel_time_matrix <= threshold_min)

def baseline_coverage_stats(existing_station_idx, coverage_matrix, demand_weights) -> dict:
    """Compute coverage statistics for a subset of stations."""
    # coverage_matrix is (n_demand, n_candidates)
    # subset coverage is True if any existing station covers the node
    subset_matrix = coverage_matrix[:, existing_station_idx]
    is_covered = np.any(subset_matrix, axis=1)
    
    covered_population = np.sum(demand_weights[is_covered])
    total_population = np.sum(demand_weights)
    coverage_pct = covered_population / total_population
    
    return {
        "coverage_pct": float(coverage_pct),
        "covered_population": float(covered_population),
        "total_population": float(total_population)
    }
