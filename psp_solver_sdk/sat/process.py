from psp_solver_sdk.core import SolverRequest
from .results import SatSolution, SatError, SatRequest
from typing import Awaitable, Callable
from .response import (
    SatResponse,
    SatErrorResponse,
    SatSolutionResponse,
)
from ..config import SolverConfig
import httpx


async def _make_get_request(url: str) -> httpx.Response:
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.get(url)


async def _get_text_from_url(url: str) -> str:
    response = await _make_get_request(url)
    return response.text


async def sat_process(
    data: dict,
    solve: Callable[[SatRequest], Awaitable[SatSolution | SatError]],
    config: SolverConfig,
) -> dict:
    request = SolverRequest.from_dict(data)
    problem = await _get_text_from_url(request.problem_url)
    instance = await _get_text_from_url(request.instance_url)
    result = await solve(
        SatRequest(request.solver_name, problem, instance, config.cpu.limit)
    )

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
