from .minizinc import solve
from psp_solver_sdk.sat import sat_solver


app = sat_solver("MiniZinc", solve)
