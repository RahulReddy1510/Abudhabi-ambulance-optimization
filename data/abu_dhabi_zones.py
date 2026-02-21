import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real Abu Dhabi place names with approximate coordinates and population estimates
# Calibrated to SCAD 2023 statistics
ZONE_DEFINITIONS = [
    # URBAN CORE (Abu Dhabi Island and surroundings)
    {"name": "Abu Dhabi Downtown", "lat": 24.4900, "lon": 54.3600, "area_km2": 8.2, "type": "urban_core", "pop": 185000},
    {"name": "Corniche District", "lat": 24.4950, "lon": 54.3500, "area_km2": 3.1, "type": "urban_core", "pop": 42000},
    {"name": "Al Bateen", "lat": 24.4780, "lon": 54.3350, "area_km2": 4.8, "type": "urban_core", "pop": 58000},
    {"name": "Al Mushrif", "lat": 24.4700, "lon": 54.3700, "area_km2": 6.4, "type": "urban_core", "pop": 71000},
    {"name": "Al Khalidiyah", "lat": 24.4850, "lon": 54.3450, "area_km2": 5.2, "type": "urban_core", "pop": 89000},
    {"name": "Al Danah", "lat": 24.4760, "lon": 54.3620, "area_km2": 4.1, "type": "urban_core", "pop": 63000},
    {"name": "Al Mina", "lat": 24.4660, "lon": 54.3410, "area_km2": 7.3, "type": "urban_core", "pop": 52000},
    {"name": "Tourist Club Area", "lat": 24.4920, "lon": 54.3780, "area_km2": 2.8, "type": "urban_core", "pop": 38000},
    {"name": "Al Nahyan", "lat": 24.4640, "lon": 54.3830, "area_km2": 5.5, "type": "urban_core", "pop": 47000},
    {"name": "Al Wahda", "lat": 24.4810, "lon": 54.3700, "area_km2": 4.3, "type": "urban_core", "pop": 55000},

    # SUBURBAN MAINLAND
    {"name": "Khalifa City A", "lat": 24.4310, "lon": 54.5100, "area_km2": 32.0, "type": "suburban", "pop": 118000},
    {"name": "Khalifa City B", "lat": 24.4180, "lon": 54.5350, "area_km2": 28.5, "type": "suburban", "pop": 87000},
    {"name": "Mohammed Bin Zayed City", "lat": 24.3850, "lon": 54.5200, "area_km2": 45.2, "type": "suburban", "pop": 134000},
    {"name": "Shakhbout City", "lat": 24.3550, "lon": 54.5500, "area_km2": 38.7, "type": "suburban", "pop": 92000},
    {"name": "Al Shamkhah", "lat": 24.3200, "lon": 54.6000, "area_km2": 52.1, "type": "suburban", "pop": 61000},
    {"name": "Al Wathba", "lat": 24.3100, "lon": 54.7000, "area_km2": 88.4, "type": "suburban", "pop": 28000},
    {"name": "Al Bahia", "lat": 24.3800, "lon": 54.6200, "area_km2": 41.3, "type": "suburban", "pop": 34000},
    {"name": "Al Samha", "lat": 24.3400, "lon": 54.6500, "area_km2": 36.8, "type": "suburban", "pop": 25000},
    {"name": "Al Rahba", "lat": 24.3000, "lon": 54.5800, "area_km2": 29.6, "type": "suburban", "pop": 19000},

    # ISLAND DEVELOPMENTS
    {"name": "Al Reem Island", "lat": 24.5100, "lon": 54.4100, "area_km2": 6.2, "type": "urban_core", "pop": 68000},
    {"name": "Saadiyat Island", "lat": 24.5400, "lon": 54.4400, "area_km2": 27.2, "type": "suburban", "pop": 15000},
    {"name": "Yas Island", "lat": 24.4800, "lon": 54.6100, "area_km2": 25.0, "type": "suburban", "pop": 8000},
    {"name": "Al Raha Beach", "lat": 24.4600, "lon": 54.6000, "area_km2": 8.5, "type": "suburban", "pop": 24000},

    # MUSAFFAH / INDUSTRIAL
    {"name": "Musaffah M1", "lat": 24.3600, "lon": 54.4900, "area_km2": 12.1, "type": "industrial", "pop": 38000},
    {"name": "Musaffah M2", "lat": 24.3500, "lon": 54.4800, "area_km2": 11.8, "type": "industrial", "pop": 35000},
    {"name": "Musaffah M4", "lat": 24.3400, "lon": 54.4700, "area_km2": 13.2, "type": "industrial", "pop": 41000},
    {"name": "Musaffah M7", "lat": 24.3300, "lon": 54.4600, "area_km2": 10.9, "type": "industrial", "pop": 29000},
    {"name": "ICAD Industrial City", "lat": 24.3000, "lon": 54.4200, "area_km2": 48.6, "type": "industrial", "pop": 22000},

    # PERIPHERAL / DESERT
    {"name": "Madinat Zayed", "lat": 23.6870, "lon": 53.7010, "area_km2": 180.0, "type": "peripheral", "pop": 18000},
    {"name": "Ghayathi", "lat": 23.8670, "lon": 52.8120, "area_km2": 220.0, "type": "peripheral", "pop": 8500},
    {"name": "Ruwais", "lat": 24.1120, "lon": 52.7300, "area_km2": 95.0, "type": "peripheral", "pop": 16000},
    {"name": "Al Mirfa", "lat": 23.9220, "lon": 53.3450, "area_km2": 110.0, "type": "peripheral", "pop": 6200},
    {"name": "Sir Baniyas", "lat": 24.3500, "lon": 52.6200, "area_km2": 87.0, "type": "peripheral", "pop": 1800},
    {"name": "Liwa Oasis", "lat": 23.1250, "lon": 53.7700, "area_km2": 350.0, "type": "peripheral", "pop": 4500},
    {"name": "Al Sila", "lat": 24.1100, "lon": 51.6800, "area_km2": 140.0, "type": "peripheral", "pop": 3200},
    {"name": "Al Ain Central", "lat": 24.2070, "lon": 55.7440, "area_km2": 68.0, "type": "suburban", "pop": 145000},
    {"name": "Al Ain Eastern", "lat": 24.2200, "lon": 55.8000, "area_km2": 82.0, "type": "suburban", "pop": 78000},
    {"name": "Al Ain Al Jimi", "lat": 24.1900, "lon": 55.7200, "area_km2": 45.0, "type": "suburban", "pop": 62000},
    {"name": "Al Ain Hili", "lat": 24.2400, "lon": 55.7600, "area_km2": 55.0, "type": "suburban", "pop": 43000},
    {"name": "Al Ain Al Muwaiji", "lat": 24.1700, "lon": 55.7000, "area_km2": 38.0, "type": "suburban", "pop": 31000},
    {"name": "Al Ain Zakher", "lat": 24.1400, "lon": 55.7200, "area_km2": 42.0, "type": "suburban", "pop": 27000},
    {"name": "Al Ain Remah", "lat": 24.2800, "lon": 55.8500, "area_km2": 120.0, "type": "suburban", "pop": 18000},
]

def generate_zones() -> gpd.GeoDataFrame:
    """
    Generate a GeoDataFrame of Abu Dhabi zones based on the defined constants.
    Uses circular buffers to approximate zone polygons.
    """
    data = []
    for i, z in enumerate(ZONE_DEFINITIONS):
        data.append({
            "zone_id": i,
            "zone_name": z["name"],
            "zone_type": z["type"],
            "population": z["pop"],
            "area_km2": z["area_km2"],
            "geometry": Point(z["lon"], z["lat"])
        })

    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
    
    # Project to UTM Zone 40N (EPSG:32640) for accurate area/distance calculations
    gdf_utm = gdf.to_crs("EPSG:32640")
    
    # Create circular polygons based on area: area = pi * r^2  => r = sqrt(area / pi)
    # We use a simplified sqrt(area_km2)/2 approx buffer for visual variety
    gdf_utm.geometry = gdf_utm.apply(
        lambda row: row.geometry.buffer(np.sqrt(row.area_km2 * 1000000) / 2), 
        axis=1
    )
    
    # Return to WGS84 for storage, but we'll project back for calculations later
    return gdf_utm.to_crs("EPSG:4326")

def generate_candidate_stations(zones_gdf: gpd.GeoDataFrame, n_candidates: int = 80, seed: int = 42) -> gpd.GeoDataFrame:
    """
    Generate potential station locations distributed across zones.
    """
    np.random.seed(seed)
    candidates = []
    
    # Project to UTM for stable buffering/sampling
    zones_utm = zones_gdf.to_crs("EPSG:32640")
    
    # Distribution logic based on zone type
    candidate_counts = {
        "urban_core": 3,
        "suburban": 2,
        "industrial": 2,
        "peripheral": 1
    }
    
    station_id = 0
    for _, zone in zones_utm.iterrows():
        count = candidate_counts.get(zone.zone_type, 1)
        for _ in range(count):
            if station_id >= n_candidates:
                break
            
            # Sample a random point within the zone polygon
            # For speed, we just do a small random shift from centroid in UTM meters
            # Ensuring it stays roughly in the zone
            max_offset = np.sqrt(zone.area_km2 * 1000000) / 4
            dx = np.random.uniform(-max_offset, max_offset)
            dy = np.random.uniform(-max_offset, max_offset)
            
            point = Point(zone.geometry.centroid.x + dx, zone.geometry.centroid.y + dy)
            
            candidates.append({
                "station_id": station_id,
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "zone_type": zone.zone_type,
                "geometry": point
            })
            station_id += 1
            
    gdf = gpd.GeoDataFrame(candidates, crs="EPSG:32640")
    return gdf.to_crs("EPSG:4326")

def generate_existing_stations(zones_gdf: gpd.GeoDataFrame, n_stations: int = 12, seed: int = 42) -> gpd.GeoDataFrame:
    """
    Generate 12 'baseline' stations concentrated in the urban core.
    """
    np.random.seed(seed)
    zones_utm = zones_gdf.to_crs("EPSG:32640")
    
    # Concentration logic: 8 in core, 3 in suburban, 1 in peripheral/industrial (Ruwais)
    selected_zones = []
    
    core_zones = zones_utm[zones_utm.zone_type == "urban_core"].sample(8, random_state=seed)
    suburban_zones = zones_utm[zones_utm.zone_type == "suburban"].sample(3, random_state=seed)
    ruwais = zones_utm[zones_utm.zone_name == "Ruwais"]
    
    selected_zones = pd.concat([core_zones, suburban_zones, ruwais])
    
    stations = []
    for i, (_, zone) in enumerate(selected_zones.iterrows()):
        stations.append({
            "station_id": 1000 + i,
            "zone_id": zone.zone_id,
            "zone_name": zone.zone_name,
            "zone_type": zone.zone_type,
            "is_existing": True,
            "geometry": zone.geometry.centroid
        })
        
    gdf = gpd.GeoDataFrame(stations, crs="EPSG:32640")
    return gdf.to_crs("EPSG:4326")

if __name__ == "__main__":
    zones = generate_zones()
    print(f"Generated {len(zones)} zones.")
    print(f"Total population: {zones.population.sum():,}")
