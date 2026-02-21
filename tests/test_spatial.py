import pytest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, box
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spatial_analysis.morans_i import compute_global_morans_i

def test_spatial_weights_knn_fallback():
    """
    Test that spatial analysis handles disconnected components 
    (like Abu Dhabi Island) using KNN fallback.
    """
    # Create two disconnected squares
    poly1 = box(0, 0, 1, 1)
    poly2 = box(10, 10, 11, 11) # Far away
    
    gdf = gpd.GeoDataFrame({
        'geometry': [poly1, poly2],
        'val': [1.0, 2.0]
    }, crs="EPSG:4326")
    
    # This should trigger KNN fallback since Queen weights would have 2 components
    try:
        results = compute_global_morans_i(gdf, "val")
        assert "I" in results
    except Exception as e:
        pytest.fail(f"Spatial analysis failed on disconnected components: {e}")

def test_morans_i_range():
    """Ensure Moran's I is within expected theoretical bounds."""
    # 4 grid squares
    geoms = [box(0,1,1,2), box(1,1,2,2), box(0,0,1,1), box(1,0,2,1)]
    gdf = gpd.GeoDataFrame({'geometry': geoms, 'val': [1, 1, 0, 0]})
    
    results = compute_global_morans_i(gdf, "val")
    assert -1.0 <= results["I"] <= 1.0
