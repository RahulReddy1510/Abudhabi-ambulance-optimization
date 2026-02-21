import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)

def plot_mip_solution(zones_gdf: gpd.GeoDataFrame, candidates_gdf: gpd.GeoDataFrame, 
                      open_stations_idx: list, coverage_radius_m: float = 8000, 
                      demand_gdf: gpd.GeoDataFrame = None, save_path: str = None) -> plt.Figure:
    """
    Comprehensive map showing the optimization solution.
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 12))
    
    # Base: Zones
    zones_gdf.plot(ax=ax, color='#f0f0f0', edgecolor='white', linewidth=0.5)
    
    # Candidate Stations (all)
    candidates_gdf.plot(ax=ax, marker='o', color='gray', markersize=5, alpha=0.3, label="Potential Sites")
    
    # Selected Stations
    selected = candidates_gdf.iloc[open_stations_idx]
    
    # Coverage Radii (approx circle in meters - requires UTM projection)
    selected_utm = selected.to_crs("EPSG:32640")
    buffers_utm = selected_utm.geometry.buffer(coverage_radius_m)
    buffers = gpd.GeoSeries(buffers_utm, crs="EPSG:32640").to_crs("EPSG:4326")
    
    buffers.plot(ax=ax, color='green', alpha=0.1, edgecolor='green', linewidth=1, label="8-min Service Range")
    selected.plot(ax=ax, marker='^', color='orange', markersize=100, edgecolor='black', label="Optimized Station Sites", zorder=5)
    
    # Optional: Demand nodes (if provided)
    if demand_gdf is not None:
        demand_gdf.plot(ax=ax, color='red', markersize=1, alpha=0.2, label="Demand Centers")

    ax.set_title("Optimized Ambulance Infrastructure Network", fontsize=16, fontweight='bold')
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc='lower right')
    ax.grid(alpha=0.2)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig
