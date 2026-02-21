import numpy as np
import geopandas as gpd
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def aggregate_coverage_to_zones(zones_gdf: gpd.GeoDataFrame, demand_gdf: gpd.GeoDataFrame, y_binary: np.ndarray) -> gpd.GeoDataFrame:
    """
    Map binary coverage results from demand nodes back to the zone level.
    y_binary: (n_demand,) binary array from optimization results.
    """
    gdf = zones_gdf.copy()
    demand = demand_gdf.copy()
    demand["is_covered"] = y_binary
    
    # Calculate coverage pct per zone: sum(covered_weight) / sum(total_weight)
    zone_stats = demand.groupby("zone_id").apply(
        lambda x: (x.is_covered * x.weight).sum() / x.weight.sum()
    )
    
    gdf["coverage_pct"] = gdf.zone_id.map(zone_stats).fillna(0)
    return gdf

def compute_baseline_coverage(zones_gdf: gpd.GeoDataFrame, demand_gdf: gpd.GeoDataFrame, base_coverage_matrix: np.ndarray) -> gpd.GeoDataFrame:
    """
    Compute zone-level coverage based on the baseline (existing) station matrix.
    base_coverage_matrix: (n_demand, n_existing_stations) boolean matrix.
    """
    # Demand node is baseline-covered if ANY existing station covers it
    is_covered_base = np.any(base_coverage_matrix, axis=1).astype(int)
    return aggregate_coverage_to_zones(zones_gdf, demand_gdf, is_covered_base)

def compute_optimized_coverage(zones_gdf: gpd.GeoDataFrame, demand_gdf: gpd.GeoDataFrame, y_optimized: np.ndarray) -> gpd.GeoDataFrame:
    """
    Compute zone-level coverage based on the optimized model output.
    y_optimized: (n_demand,) binary array.
    """
    return aggregate_coverage_to_zones(zones_gdf, demand_gdf, y_optimized)

def summarize_by_type(zones_gdf: gpd.GeoDataFrame, col: str) -> pd.DataFrame:
    """
    Group coverage statistics by zone type (Urban, Suburban, etc.).
    """
    return zones_gdf.groupby("zone_type")[col].agg(['mean', 'min', 'max']).round(4)
