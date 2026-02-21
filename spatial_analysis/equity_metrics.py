import numpy as np
import logging

logger = logging.getLogger(__name__)

def weighted_gini(values: np.ndarray, weights: np.ndarray) -> float:
    """
    Compute the weighted Gini coefficient for a set of values.
    0 = Perfect equality, 1 = Maximum inequality.
    """
    if len(values) == 0:
        return 0.0
        
    # Sort data by value
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    
    # Calculate cumulative sums
    cum_weights = np.cumsum(weights)
    cum_val_weighted = np.cumsum(values * weights)
    
    total_weights = cum_weights[-1]
    total_val_weighted = cum_val_weighted[-1]
    
    if total_val_weighted == 0:
        return 0.0
        
    # Relative portions
    share_pop = cum_weights / total_weights
    share_val = cum_val_weighted / total_val_weighted
    
    # Gini formula using Lorenz area approach
    # Area under Lorenz curve (trapezoidal rule)
    area = np.sum((share_val[1:] + share_val[:-1]) * (share_pop[1:] - share_pop[:-1])) / 2
    # Area between diagonal and Lorenz curve
    gini = 1 - 2 * (area + (share_val[0] * share_pop[0] / 2))
    
    return float(np.clip(gini, 0, 1))

def lorenz_curve(values: np.ndarray, weights: np.ndarray) -> tuple:
    """
    Return coordinates for plotting a Lorenz curve.
    Returns (percent_pop, percent_val).
    """
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    
    cum_weights = np.cumsum(weights)
    cum_val_weighted = np.cumsum(values * weights)
    
    percent_pop = np.insert(cum_weights / cum_weights[-1], 0, 0)
    percent_val = np.insert(cum_val_weighted / cum_val_weighted[-1], 0, 0)
    
    return percent_pop, percent_val
