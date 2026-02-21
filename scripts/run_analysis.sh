#!/bin/bash
# Run post-optimization analysis
echo "Running Spatial Equity Analysis..."
# Note: Results are often checked via Notebook 03, but this can be expanded
echo "Analyzing optimization_results.json..."
python -c "import json; r=json.load(open('results/optimization_results.json')); print(f\"Coverage: {r['coverage_pct']:.2%}, Gap Closure: {r['gap_closure_pct']:.2%}\")"
