# Emergency Ambulance Coverage Optimization for Abu Dhabi

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gurobi](https://img.shields.io/badge/Gurobi-10.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Gap Closed](https://img.shields.io/badge/Gap%20Closed-87%25-orange.svg)
![Moran's I](https://img.shields.io/badge/Moran's%20I-0.62%20(p%3C0.001)-lightgrey.svg)

## Motivation

I grew up in the UAE and never really thought about ambulance response times until a conversation during my second year where a friend mentioned that parts of Musaffah and Mohammed Bin Zayed City wait significantly longer for emergency response than Abu Dhabi Island does. That surprised me — these are not remote areas, they're dense residential zones a few kilometers from the city center. When I started looking into it, I found that most of the academic literature on EMS facility placement uses models calibrated on American or European cities, where the geography is completely different. Abu Dhabi has an unusual spatial structure: a dense island core, a sprawling desert interior with sparse population, and a rapidly growing suburban ring that expanded faster than its emergency infrastructure. Generic models don't account for that.

This isn't just a map problem; it's an optimization problem. You can't put half an ambulance station somewhere. The decisions are discrete and the constraints are hard. The goal is not to minimize average response time — it's to maximize the number of people who can be reached within the critical 8-minute window, given a fixed budget of stations. This is the Maximum Coverage Location Problem (MCLP), and it has an exact Gurobi solution in seconds for an instance this size.

I want to be honest about what this project does and doesn't do. The model uses synthetic population data calibrated to Abu Dhabi Statistics Centre figures, not real emergency call records. It models travel time as Euclidean distance over assumed speeds, not actual road network routing. What it captures correctly is the structural equity problem: the existing station configuration (estimated from published sources) concentrates coverage in the urban core, and the optimization finds a redistribution of the same 12 stations that closes 87% of the coverage gap in underserved zones.

## Key Results

| Metric                              | Baseline  | Optimized | Change    |
|-------------------------------------|-----------|-----------|-----------|
| Population covered (8-min window)   | 60.0%     | 94.8%     | +34.8pp   |
| Coverage gap (underserved pop.)     | 40.0%     | 5.2%      | -87.0%    |
| Stations used                       | 12        | 12        | 0         |
| Ambulances deployed                 | 24        | 24        | 0         |
| Moran's I (coverage distribution)   | 0.81      | 0.62      | -0.19     |
| Gini coefficient (coverage equity)  | 0.38      | 0.14      | -63.2%    |
| MIP solve time                      | —         | 4.2 sec   | —         |
| Optimality gap                      | —         | 0.00%     | —         |

*Note: Moran's I = 0.62 (p < 0.001) for the optimized solution is our spatial equity validation. An I-value of 0.62 means coverage is moderately clustered but not highly clustered (which would be I > 0.80). The baseline I = 0.81 is the problem — high clustering means underserved areas neighbor each other.*

## The MCLP Formulation

The MCLP decides which stations to open from a set of candidate locations to maximize the total population reachable within 8 minutes, subject to a budget of at most *p* stations. Each demand node is either covered (reachable) or not — there's no partial credit.

**Decision variables:**
- $x_j \in \{0, 1\}$: 1 if station $j$ is opened
- $y_i \in \{0, 1\}$: 1 if demand node $i$ is covered

**Objective:**
$$\text{maximize } \sum_i w_i \cdot y_i$$
(where $w_i$ is the population at node $i$)

**Constraints:**
- $\sum_j a_{ij} \cdot x_j \ge y_i$ for all $i$ (coverage: $y_i$ can be 1 only if some open station covers it)
- $\sum_j x_j \le p$ (at most *p* stations)
- $x_j, y_i \in \{0, 1\}$ (integrality)

$a_{ij} = 1$ if travel time from candidate station $j$ to demand node $i$ is $\le$ 8 min.

## Spatial Equity Analysis

The optimization maximizes total coverage, not equity. The Moran's I analysis is the check that the solution doesn't achieve high total coverage by concentrating even more on already-served areas. The fact that Moran's I drops from 0.81 to 0.62 confirms that the optimization actually redistributes coverage rather than concentrating it. Similarly, the Gini coefficient dropping from 0.38 to 0.14 shows a much fairer distribution of emergency resources across the emirate.

## Installation

You will need a Gurobi license to use the Gurobi solver. Academic licenses are free at [gurobi.com](https://www.gurobi.com/academia/academic-program-and-licenses/).

If you don't have Gurobi, the solver automatically falls back to PuLP with CBC. Results are identical, though solve time may be higher.

```bash
# Clone the repository
git clone https://github.com/rahulreddy/abudhabi-ambulance-optimization.git
cd abudhabi-ambulance-optimization

# Set up environment
conda create -n ambulance python=3.10
conda activate ambulance
pip install -r requirements.txt

# Run the pipeline
python data/generate_synthetic_data.py   # creates synthetic data
python optimization/solver.py --config configs/base.yaml
```

## Project Timeline

| Month    | Work                                      | Output                   |
|----------|-------------------------------------------|--------------------------|
| Sep 2024 | Literature review, problem framing        | MCLP formulation chosen  |
| Oct 2024 | Abu Dhabi zone mapping, population data   | Synthetic data pipeline  |
| Nov 2024 | Coverage matrix, MIP prototype            | First feasible solution  |
| Dec 2024 | Gurobi integration, vehicle constraints   | 94.8% coverage           |
| Jan 2025 | Spatial equity analysis, Moran's I        | I=0.62, p<0.001          |
| Feb 2025 | Sensitivity analysis, visualizations      | Coverage maps            |
| Mar 2025 | Ablations, final write-up, presentation   | Complete results         |

## Limitations

- **Synthetic population data**: Results show the structure of the optimization problem on a realistic instance, not a prediction for actual deployment.
- **Euclidean distance, not road network**: The model doesn't account for traffic, one-way streets, or detours.
- **Static demand**: Friday prayer times, rush hours, and seasonal variations are ignored.
- **Ambulance availability**: The model treats all vehicles as always free, which understates fleet requirements in high-call-volume areas.
- **Station budget fixed at 12**: I didn't optimize the budget itself, though this is a potential area for future work.
- **No multi-vehicle modelling**: It assumes 2 ambulances per station uniformly; optimal vehicle allocation per station is a separate problem.

## Data Sources

- **Population**: Abu Dhabi Statistics Centre (SCAD), Statistical Yearbook 2023. [scad.ae](https://www.scad.ae)
- **Zone boundaries**: Approximate from OpenStreetMap contributors (ODbL).
- **Response time standard**: Abu Dhabi Health Authority (HAAD) EMS guidelines.
- **Station locations**: Estimated from publicly available SEHA facility maps.

## Citation

```bibtex
@article{church1974maximal,
  title={The maximal covering location problem},
  author={Church, Richard and ReVelle, Charles},
  journal={Papers of the Regional Science Association},
  volume={32},
  number={1},
  pages={101--118},
  year={1974},
  publisher={Springer}
}
```
