from psp_solver_sdk.core import SolverRequest
from .results import SatSolution, SatError, SatRequest
from typing import Awaitable, Callable
from .response import (
    SatResponse,
    SatErrorResponse,
    SatSolutionResponse,
)
from ..config import SolverConfig


async def sat_process(
    data: dict,
    solve: Callable[[SatRequest], Awaitable[SatSolution | SatError]],
    config: SolverConfig,
) -> dict:
    request = SolverRequest.from_dict(data)
    result = await solve(request)

    response = SatResponse(
        result.solve_time,
        request.solver_id,
        config.cpu.limit,
        request.problem_id,
        request.instance_id,
        None,
    )
    if result is SatSolution:
        response.result = SatSolutionResponse(str(result.solution))
    else:
        response.result = SatErrorResponse(result.error_message)
    return response.to_dict()
