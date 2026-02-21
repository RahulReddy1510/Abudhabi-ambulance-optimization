#!/bin/bash
# Run baseline optimization
echo "Running MCLP Optimization Pipeline..."
python optimization/solver.py --config configs/base.yaml
echo "Optimization cycle complete."
