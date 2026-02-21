import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import logging

logger = logging.getLogger(__name__)

def plot_lorenz_curve(baseline_coords, optimized_coords, baseline_gini, optimized_gini, save_path=None) -> plt.Figure:
    """
    Plot Lorenz curves comparing baseline and optimized coverage distributions.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Diagonal line (perfect equality)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label="Perfect Equality")
    
    # Baseline
    pop_b, val_b = baseline_coords
    ax.plot(pop_b, val_b, 'r-', label=f"Baseline (Gini: {baseline_gini:.2f})")
    
    # Optimized
    pop_o, val_o = optimized_coords
    ax.plot(pop_o, val_o, 'g-', label=f"Optimized (Gini: {optimized_gini:.2f})")
    
    ax.set_title("Lorenz Curve: Ambulance Coverage Distribution", fontsize=14, fontweight='bold')
    ax.set_xlabel("Cumulative % of Population", fontsize=12)
    ax.set_ylabel("Cumulative % of Coverage", fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig

def plot_zone_type_coverage(zones_gdf: gpd.GeoDataFrame, baseline_col: str, optimized_col: str, save_path=None) -> plt.Figure:
    """
    Grouped bar chart showing coverage by zone type for both scenarios.
    """
    # Group by type and calculate means
    stats = zones_gdf.groupby("zone_type")[[baseline_col, optimized_col]].mean().reset_index()
    
    # Melt for seaborn
    plot_df = stats.melt(id_vars="zone_type", var_name="Scenario", value_name="Coverage %")
    plot_df["Scenario"] = plot_df["Scenario"].map({baseline_col: "Baseline", optimized_col: "Optimized"})
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=plot_df, x="zone_type", y="Coverage %", hue="Scenario", ax=ax, palette={"Baseline": "tomato", "Optimized": "mediumseagreen"})
    
    ax.set_title("Mean Coverage by Zone Type", fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_ylabel("Coverage (Decimal)")
    ax.grid(axis='y', alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig

def plot_coverage_distribution(zones_gdf: gpd.GeoDataFrame, baseline_col: str, optimized_col: str, save_path=None) -> plt.Figure:
    """
    Histogram/KDE showing the shift in the distribution of coverage rates.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.kdeplot(zones_gdf[baseline_col], ax=ax, fill=True, color="tomato", label="Baseline", alpha=0.4)
    sns.kdeplot(zones_gdf[optimized_col], ax=ax, fill=True, color="mediumseagreen", label="Optimized", alpha=0.4)
    
    ax.set_title("Distribution of Zone-Level Coverage Rates", fontsize=14, fontweight='bold')
    ax.set_xlabel("Coverage Percentage (Decimal)")
    ax.set_xlim(0, 1.1)
    ax.legend()
    ax.grid(alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig
