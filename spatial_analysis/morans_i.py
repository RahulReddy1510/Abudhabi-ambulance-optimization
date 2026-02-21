import numpy as np
import geopandas as gpd
import logging
from esda.moran import Moran, Moran_Local
from libpysal.weights import Queen, KNN

logger = logging.getLogger(__name__)

def compute_global_morans_i(zones_gdf: gpd.GeoDataFrame, attribute_col: str, permutations: int = 999) -> dict:
    """
    Compute Global Moran's I for a given attribute.
    Uses Queen weights with KNN(k=6) fallback for disconnected components.
    """
    # Ensure no empty geometries
    gdf = zones_gdf[~zones_gdf.geometry.is_empty].copy()
    
    # Generate weights
    try:
        w = Queen.from_dataframe(gdf, use_index=False)
        if w.n_components > 1:
            k_val = min(8, len(gdf) - 1)
            logger.warning(f"Disconnected components found in Queen weights. Falling back to KNN(k={k_val}).")
            w = KNN.from_dataframe(gdf, k=k_val)
    except Exception as e:
        k_val = min(8, len(gdf) - 1)
        logger.warning(f"Queen weights failed: {e}. Using KNN(k={k_val}).")
        w = KNN.from_dataframe(gdf, k=k_val)

    # Row-standardize weights
    w.transform = 'r'
    
    y = gdf[attribute_col].values
    moran = Moran(y, w, permutations=permutations)
    
    # Interpretation logic
    def _interpret(i_val):
        if i_val >= 0.8: return "Strong positive spatial autocorrelation (highly clustered)"
        if i_val >= 0.5: return "Moderate positive spatial autocorrelation"
        if i_val >= 0.2: return "Weak positive spatial autocorrelation"
        if i_val >= -0.1: return "No significant spatial autocorrelation (near random)"
        return "Dispersed/Negative spatial autocorrelation"

    return {
        "I": float(moran.I),
        "p_sim": float(moran.p_sim),
        "z_sim": float(moran.z_sim),
        "interpretation": _interpret(moran.I)
    }

def compute_local_morans_i(zones_gdf: gpd.GeoDataFrame, attribute_col: str) -> gpd.GeoDataFrame:
    """
    Compute Local Moran's I (LISA) and attach cluster labels to the GeoDataFrame.
    """
    gdf = zones_gdf.copy()
    
    # Weights with fallback
    try:
        w = Queen.from_dataframe(gdf, use_index=False)
        if w.n_components > 1:
            k_val = min(8, len(gdf) - 1)
            w = KNN.from_dataframe(gdf, k=k_val)
    except Exception:
        k_val = min(8, len(gdf) - 1)
        w = KNN.from_dataframe(gdf, k=k_val)
        
    w.transform = 'r'
    
    y = gdf[attribute_col].values
    lisa = Moran_Local(y, w, permutations=999)
    
    # Quadrant labels: 1=HH, 2=LH, 3=LL, 4=HL
    labels = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}
    
    gdf["lisa_I"] = lisa.Is
    gdf["lisa_p"] = lisa.p_sim
    gdf["lisa_cluster"] = [
        labels.get(q, "NS") if p < 0.05 else "NS" 
        for q, p in zip(lisa.q, lisa.p_sim)
    ]
    
    return gdf
