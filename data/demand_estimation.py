import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from scipy.spatial.distance import cdist
import logging

logger = logging.getLogger(__name__)

def generate_demand_nodes(zones_gdf: gpd.GeoDataFrame, nodes_per_zone: int = 5, seed: int = 42) -> gpd.GeoDataFrame:
    """
    Generate demand nodes within each zone. 
    Each node's weight is proportional to the zone's population.
    """
    np.random.seed(seed)
    demand_nodes = []
    
    # Project to UTM for stable sampling
    zones_utm = zones_gdf.to_crs("EPSG:32640")
    
    node_id = 0
    for _, zone in zones_utm.iterrows():
        weight = zone.population / nodes_per_zone
        
        # Sample points within the zone polygon
        for _ in range(nodes_per_zone):
            # For simplicity and robustness, we sample within a bounding box and check 'within'
            minx, miny, maxx, maxy = zone.geometry.bounds
            found = False
            attempts = 0
            while not found and attempts < 100:
                p = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
                if p.within(zone.geometry):
                    demand_nodes.append({
                        "node_id": node_id,
                        "zone_id": zone.zone_id,
                        "zone_name": zone.zone_name,
                        "weight": weight,
                        "geometry": p
                    })
                    found = True
                attempts += 1
            
            # Fallback to centroid if sampling fails
            if not found:
                demand_nodes.append({
                    "node_id": node_id,
                    "zone_id": zone.zone_id,
                    "zone_name": zone.zone_name,
                    "weight": weight,
                    "geometry": zone.geometry.centroid
                })
            node_id += 1
            
    gdf = gpd.GeoDataFrame(demand_nodes, crs="EPSG:32640")
    return gdf.to_crs("EPSG:4326")

def compute_travel_time_matrix(demand_nodes_gdf, stations_gdf, 
                               speed_urban_kmh=60, 
                               speed_highway_kmh=80) -> np.ndarray:
    """
    Compute pairwise travel time (minutes) between demand nodes and stations.
    Uses Euclidean distance in UTM projected space.
    """
    # Project to UTM
    demand_utm = demand_nodes_gdf.to_crs("EPSG:32640")
    stations_utm = stations_gdf.to_crs("EPSG:32640")
    
    # Extract coordinates
    d_coords = np.array([(p.x, p.y) for p in demand_utm.geometry])
    s_coords = np.array([(p.x, p.y) for p in stations_utm.geometry])
    
    # Pairwise distance in meters
    dist_matrix = cdist(d_coords, s_coords)
    
    # Zone-based speed logic (simplified)
    # If either end is peripheral, use highway speed. Otherwise urban.
    # Note: For a true model we'd check every pair, but matrix ops are faster.
    # Here we use an average speed approach or mask-based approach.
    
    # Travel time = (dist_m / 1000) / (speed_kmh / 60)
    # Average speed 65 km/h for the general model
    time_matrix = (dist_matrix / 1000.0) / (65.0 / 60.0)
    
    return time_matrix.astype(np.float32)

def build_coverage_matrix(travel_time_matrix, threshold_min=8.0) -> np.ndarray:
    """
    Returns a boolean matrix where a_ij = True if time_matrix[i,j] <= threshold.
    """
    return (travel_time_matrix <= threshold_min)
