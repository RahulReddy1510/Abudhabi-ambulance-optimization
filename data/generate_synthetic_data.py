import os
import logging
import json
import geopandas as gpd
from abu_dhabi_zones import generate_zones, generate_candidate_stations, generate_existing_stations
from demand_estimation import generate_demand_nodes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main orchestration function for synthetic data generation.
    """
    output_dir = os.path.join(os.path.dirname(__file__), "synthetic")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("Starting synthetic data generation...")
    
    # 1. Generate Zones
    logger.info("Generating 47 Abu Dhabi zones...")
    zones_gdf = generate_zones()
    zones_path = os.path.join(output_dir, "zones.geojson")
    zones_gdf.to_file(zones_path, driver="GeoJSON")
    logger.info(f"Saved zones to {zones_path}")
    
    # 2. Generate Demand Nodes
    logger.info("Generating demand nodes (5 per zone)...")
    demand_gdf = generate_demand_nodes(zones_gdf)
    demand_path = os.path.join(output_dir, "demand_nodes.geojson")
    demand_gdf.to_file(demand_path, driver="GeoJSON")
    logger.info(f"Saved demand nodes to {demand_path}")
    
    # 3. Generate Candidate Stations
    logger.info("Generating 80 candidate station locations...")
    candidates_gdf = generate_candidate_stations(zones_gdf, n_candidates=80)
    candidates_path = os.path.join(output_dir, "candidate_stations.geojson")
    candidates_gdf.to_file(candidates_path, driver="GeoJSON")
    logger.info(f"Saved candidate stations to {candidates_path}")
    
    # 4. Generate Existing Stations
    logger.info("Generating 12 existing (baseline) station locations...")
    existing_gdf = generate_existing_stations(zones_gdf, n_stations=12)
    existing_path = os.path.join(output_dir, "existing_stations.geojson")
    existing_gdf.to_file(existing_path, driver="GeoJSON")
    logger.info(f"Saved existing stations to {existing_path}")
    
    # 5. Metadata Summary
    summary = {
        "n_zones": len(zones_gdf),
        "total_population": int(zones_gdf.population.sum()),
        "n_demand_nodes": len(demand_gdf),
        "n_candidate_stations": len(candidates_gdf),
        "n_existing_stations": len(existing_gdf),
        "projection": "EPSG:4326 (WGS84)",
        "calculation_projection": "EPSG:32640 (UTM 40N)"
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(summary, f, indent=4)
        
    logger.info("Data generation complete!")
    for k, v in summary.items():
        logger.info(f"  {k}: {v}")

if __name__ == "__main__":
    main()
