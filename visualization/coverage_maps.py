import matplotlib.pyplot as plt
import geopandas as gpd
import logging

logger = logging.getLogger(__name__)

def plot_coverage_choropleth(zones_gdf: gpd.GeoDataFrame, coverage_col: str, title: str, save_path: str = None) -> plt.Figure:
    """
    Plot a choropleth map of coverage percentage at the zone level.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Plot zones colored by coverage
    zones_gdf.plot(
        column=coverage_col,
        ax=ax,
        cmap="RdYlGn",
        legend=True,
        legend_kwds={'label': "Coverage %", 'orientation': "horizontal", 'shrink': 0.6},
        vmin=0,
        vmax=1,
        edgecolor='black',
        linewidth=0.5
    )
    
    # Add labels for major zones
    for x, y, label in zip(zones_gdf.geometry.centroid.x, zones_gdf.geometry.centroid.y, zones_gdf.zone_name):
        if zones_gdf.geometry.area.loc[zones_gdf.zone_name == label].values[0] > 0.005:  # Simple filter for large zones
            ax.text(x, y, label, fontsize=6, ha='center', alpha=0.7)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        logger.info(f"Saved coverage choropleth to {save_path}")
        
    return fig

def plot_station_locations(zones_gdf: gpd.GeoDataFrame, stations_gdf: gpd.GeoDataFrame, 
                             highlight_idx=None, title="Station Locations", save_path=None) -> plt.Figure:
    """
    Plot station locations overlaid on zone polygons.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Background: zones
    zones_gdf.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)
    
    # Points: stations
    stations_gdf.plot(ax=ax, marker='o', color='blue', markersize=20, label="Potential Stations", alpha=0.5)
    
    # Highlight specific indices (e.g., optimized selection)
    if highlight_idx is not None:
        selected = stations_gdf[stations_gdf.index.isin(highlight_idx)]
        selected.plot(ax=ax, marker='^', color='orange', markersize=60, label="Selected/Existing", edgecolor='black')

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.axis('off')
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig
