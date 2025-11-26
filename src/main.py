from .sat import sat_solver
from .minizinc import solve


app = sat_solver("MiniZinc", solve)
