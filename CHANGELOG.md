# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-15

### Added
- Final capstone submission.
- Full results and all analysis complete.

## [0.9.0] - 2025-02-28

### Added
- Sensitivity analysis: model robust to +/-2 min threshold changes.
- Visualization suite and final figures.

## [0.8.0] - 2025-02-10

### Added
- Spatial equity analysis complete. Moran's I = 0.62 (p < 0.001).
- Gini coefficient reduction from 0.38 to 0.14.
- Local Moran's I identification of Musaffah and peripheral mainland as underserved clusters.

## [0.7.0] - 2025-01-20

### Added
- Vehicle allocation constraint implementation.
- Optimal distribution of 24 ambulances across 12 stations.
- Gurobi solver performance optimization (solve time: 4.2 seconds).

## [0.6.0] - 2025-01-05

### Added
- Full Abu Dhabi synthetic dataset (47 zones, 235 demand nodes, 80 candidates).
- Coverage matrix generation (235 x 80).

## [0.5.0] - 2024-12-15

### Added
- MIP model producing optimal solution: 94.8% coverage with 12 stations.
- Baseline comparison: 60.0% coverage with existing configuration.
- Gap closure calculation (87%).

## [0.4.0] - 2024-12-01

### Added
- Gurobi solver integration.
- PuLP fallback implementation for environments without Gurobi licenses.

## [0.3.0] - 2024-11-15

### Added
- Coverage matrix computation logic.
- First feasible MIP solution using PuLP (89% coverage at this stage).

## [0.2.0] - 2024-11-01

### Added
- Abu Dhabi zone data finalization.
- Population estimates calibrated to Statistics Centre 2023 figures.
- Travel time model validation against Google Maps spot checks.

## [0.1.0] - 2024-10-01

### Added
- Initial project commit.
- Choice of Maximum Coverage Location Problem (MCLP) formulation.
- Literature review completion.
