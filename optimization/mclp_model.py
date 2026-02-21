import os
import time
import numpy as np
import logging

logger = logging.getLogger(__name__)

def _detect_solver() -> str:
    """Detect available MIP solver. Checks for Gurobi and CI overrides."""
    if os.environ.get("USE_PULP") == "1":
        logger.info("USE_PULP=1 env variable detected. Initializing PuLP solver.")
        return "pulp"
    
    try:
        import gurobipy
        # Check if license is active
        with gurobipy.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.start()
            logger.info("Gurobi license detected. Initializing Gurobi solver.")
            return "gurobi"
    except Exception:
        logger.info("Gurobi not detected or not licensed. Falling back to PuLP/CBC.")
        return "pulp"

class MCLPModel:
    """
    Maximum Coverage Location Problem (MCLP) formulation.
    Calculates optimal station placement to maximize population coverage.
    """
    def __init__(self, coverage_matrix, demand_weights, p_stations, 
                 p_vehicles=24, verbose=False):
        self.coverage_matrix = coverage_matrix
        self.demand_weights = demand_weights
        self.p_stations = p_stations
        self.p_vehicles = p_vehicles
        self.verbose = verbose
        self.n_demand, self.n_candidates = coverage_matrix.shape
        
        self.solver_type = _detect_solver()
        self.model = None
        
        # Solution attributes
        self.x = None
        self.y = None
        self.v = None
        self.obj_value = None
        self.coverage_pct = None
        self.solve_time = None
        self.optimality_gap = 0.0
        self.status = "UNDEFINED"

    def build(self):
        """Build the model for the detected solver."""
        if self.solver_type == "gurobi":
            self._build_gurobi()
        else:
            self._build_pulp()

    def _build_gurobi(self):
        """Build using gurobipy. Import inside method to avoid dependency errors."""
        import gurobipy as gp
        from gurobipy import GRB
        
        m = gp.Model("AmbulanceMCLP")
        if not self.verbose:
            m.setParam("OutputFlag", 0)
        
        # Decision Variables
        x = m.addVars(self.n_candidates, vtype=GRB.BINARY, name="station")
        y = m.addVars(self.n_demand, vtype=GRB.BINARY, name="covered")
        
        # Vehicle allocation variables (if enabled)
        v = None
        if self.p_vehicles:
            v = m.addVars(self.n_candidates, vtype=GRB.INTEGER, lb=0, ub=4, name="vehicles")
        
        # Objective: Maximize weighted coverage
        m.setObjective(
            gp.quicksum(float(self.demand_weights[i]) * y[i] for i in range(self.n_demand)),
            GRB.MAXIMIZE
        )
        
        # Constraint 1: Coverage logic
        # sum_j a_ij * x_j >= y_i
        # demand node i is covered only if at least one station covering it is open
        for i in range(self.n_demand):
            covering_j = [j for j in range(self.n_candidates) if self.coverage_matrix[i, j]]
            if covering_j:
                m.addConstr(gp.quicksum(x[j] for j in covering_j) >= y[i], name=f"cov_{i}")
            else:
                m.addConstr(y[i] == 0, name=f"unreachable_{i}")
                
        # Constraint 2: Station budget
        m.addConstr(gp.quicksum(x[j] for j in range(self.n_candidates)) <= self.p_stations, name="budget")
        
        # Constraint 3: Vehicle constraints
        if self.p_vehicles:
            m.addConstr(gp.quicksum(v[j] for j in range(self.n_candidates)) <= self.p_vehicles, name="v_budget")
            for j in range(self.n_candidates):
                m.addConstr(v[j] <= 4 * x[j], name=f"v_max_{j}")
                m.addConstr(v[j] >= 1 * x[j], name=f"v_min_{j}")
                
        self.model = m
        self._x_vars = x
        self._y_vars = y
        self._v_vars = v

    def _build_pulp(self):
        """Build using PuLP (CBC fallback)."""
        import pulp
        
        prob = pulp.LpProblem("AmbulanceMCLP", pulp.LpMaximize)
        
        # Variables
        x = [pulp.LpVariable(f"x_{j}", cat="Binary") for j in range(self.n_candidates)]
        y = [pulp.LpVariable(f"y_{i}", cat="Binary") for i in range(self.n_demand)]
        
        v = None
        if self.p_vehicles:
            v = [pulp.LpVariable(f"v_{j}", lowBound=0, upBound=4, cat="Integer") for j in range(self.n_candidates)]
            
        # Objective
        prob += pulp.lpSum(float(self.demand_weights[i]) * y[i] for i in range(self.n_demand))
        
        # Constraints
        for i in range(self.n_demand):
            covering_j = [j for j in range(self.n_candidates) if self.coverage_matrix[i, j]]
            if covering_j:
                prob += pulp.lpSum(x[j] for j in covering_j) >= y[i]
            else:
                prob += y[i] == 0
                
        prob += pulp.lpSum(x[j] for j in range(self.n_candidates)) <= self.p_stations
        
        if self.p_vehicles:
            prob += pulp.lpSum(v[j] for j in range(self.n_candidates)) <= self.p_vehicles
            for j in range(self.n_candidates):
                prob += v[j] <= 4 * x[j]
                prob += v[j] >= 1 * x[j]
                
        self.model = prob
        self._x_vars = x
        self._y_vars = y
        self._v_vars = v

    def solve(self, time_limit=300):
        """Solve the model."""
        if self.model is None:
            self.build()
            
        t0 = time.time()
        
        if self.solver_type == "gurobi":
            self.model.setParam("TimeLimit", time_limit)
            self.model.optimize()
            
            # Extract status
            from gurobipy import GRB
            if self.model.status == GRB.OPTIMAL:
                self.status = "OPTIMAL"
            elif self.model.status == GRB.TIME_LIMIT:
                self.status = "TIME_LIMIT"
            else:
                self.status = str(self.model.status)
            
            # Extract values
            self.x = np.array([self._x_vars[j].X for j in range(self.n_candidates)])
            self.y = np.array([self._y_vars[i].X for i in range(self.n_demand)])
            if self._v_vars:
                self.v = np.array([self._v_vars[j].X for j in range(self.n_candidates)])
            self.obj_value = self.model.objVal
            self.optimality_gap = self.model.mipGap
            
        else:
            import pulp
            solver = pulp.PULP_CBC_CMD(timeLimit=time_limit, msg=self.verbose)
            self.model.solve(solver)
            
            self.status = pulp.LpStatus[self.model.status]
            
            self.x = np.array([pulp.value(self._x_vars[j]) for j in range(self.n_candidates)])
            self.y = np.array([pulp.value(self._y_vars[i]) for i in range(self.n_demand)])
            if self._v_vars:
                self.v = np.array([pulp.value(self._v_vars[j]) for j in range(self.n_candidates)])
            self.obj_value = pulp.value(self.model.objective)
            
        self.solve_time = time.time() - t0
        self.coverage_pct = self.obj_value / np.sum(self.demand_weights)
        
        return self._get_results()

    def _get_results(self):
        """Build results dictionary."""
        open_stations = np_where_binary(self.x)
        vehicles_per_station = {}
        if self.v is not None:
            vehicles_per_station = {int(j): int(round(self.v[j])) for j in open_stations}
            
        return {
            "solver": self.solver_type,
            "status": self.status,
            "obj_value": float(self.obj_value),
            "coverage_pct": float(self.coverage_pct),
            "open_stations": [int(idx) for idx in open_stations],
            "n_stations_used": int(len(open_stations)),
            "vehicles_per_station": vehicles_per_station,
            "solve_time_sec": float(self.solve_time),
            "optimality_gap": float(self.optimality_gap)
        }

    def summary(self):
        """Return a formatted string summary of the solution."""
        lines = [
            "="*40,
            "MCLP OPTIMIZATION SUMMARY",
            "="*40,
            f"Solver:      {self.solver_type.upper()}",
            f"Status:      {self.status}",
            f"Coverage %:  {self.coverage_pct:.2%}",
            f"Stations:    {int(np.sum(self.x))} / {self.p_stations}",
            f"Ambulances:  {int(np.sum(self.v)) if self.v is not None else 'N/A'} / {self.p_vehicles}",
            f"Solve Time:  {self.solve_time:.2f} sec",
            "="*40
        ]
        return "\n".join(lines)

def np_where_binary(arr, threshold=0.5):
    """Utility to get indices of binary 1s."""
    return np.where(arr > threshold)[0]

def run_mclp(coverage_matrix, demand_weights, p_stations=12, p_vehicles=24, verbose=False):
    """Ease-of-use wrapper for the model."""
    model = MCLPModel(coverage_matrix, demand_weights, p_stations, p_vehicles, verbose)
    model.solve()
    return model

if __name__ == "__main__":
    # Small test instance
    np.random.seed(42)
    n_d, n_c = 20, 10
    weights = np.random.uniform(100, 1000, n_d)
    cov = np.random.choice([0, 1], size=(n_d, n_c), p=[0.7, 0.3])
    
    m = run_mclp(cov, weights, p_stations=3, p_vehicles=6, verbose=True)
    print(m.summary())
    print("Open Stations:", m._get_results()["open_stations"])
