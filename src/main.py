from .minizinc import solve
from psp_solver_sdk.sat import sat_solver
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



app = sat_solver("MiniZinc", solve)
