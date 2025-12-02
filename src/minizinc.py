from time import sleep
from psp_solver_sdk.sat import SatSolution, SatError, SatRequest
from minizinc import Status, Result, Model, Instance, Solver
from pprint import pprint
import logging

logger = logging.getLogger(__name__)

async def solve(request: SatRequest) -> SatSolution | SatError:
    """
    Solver examples: coinbc, gecode
    """
    logger.info(f"solver: {request.solver}")
    try:
        solver = Solver.lookup(request.solver)
    except Exception as e:
        print(
            "Failed to find solver. Make sure minizinc is installed on the system, and the solver name is correct."
        )
        raise e

    logger.info(f"problem: {request.problem}")

    print("Loading model")
    model = Model(request.problem)
    logger.info(f"instance: {request.instance}")

    print("Adding instance")
    model.add_file(request.instance)

    print("Create instance")
    instance = Instance(solver, model)

    print("Solving...")
    result = await instance.solve_async(processes=request.vcpus)
    if result.status == Status.ERROR:
        return SatError("Failed to solve")
    elif result.status != Status.OPTIMAL_SOLUTION:
        return SatError("Solution is not optimal")

    return SatSolution(str(result.solution), result.statistics["solveTime"])


def print_result(result: Result) -> None:
    pprint(result, depth=None, width=80)
    status = result.status
    status_str = None
    if status == Status.ERROR or status == Status.UNKNOWN:
        status_str = "error"
        print(f"Status: {status_str}")
        return
    elif status == Status.UNBOUNDED:
        status_str = "unbounded"
        print(f"Status: {status_str}")
        return
    elif status == Status.UNSATISFIABLE:
        status_str = "unsatisfiable"
        print(f"Status: {status_str}")
        return

    if status == Status.OPTIMAL_SOLUTION:
        status_str = "optimal"
    elif status == Status.SATISFIED:
        status_str = "satisfied"
    elif status == Status.ALL_SOLUTIONS:
        status_str = "all solutions"

    print("Status:", status_str)
    print("Solve time:", result.statistics["solveTime"])
    print("Total time:", result.statistics["time"])
    print("Solution:")
    print(result.solution)
