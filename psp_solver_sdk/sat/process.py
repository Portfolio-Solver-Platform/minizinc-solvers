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
import tempfile


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
    problem_bytes = await _get_text_from_url(request.problem_url)
    instance_bytes = await _get_text_from_url(request.instance_url)
    with tempfile.NamedTemporaryFile(
        mode="w+", prefix="problem_", suffix=".mzn", delete=True
    ) as problem_file:
        problem_file.write(problem_bytes)
        problem_file.flush()
        with tempfile.NamedTemporaryFile(
            mode="w+", prefix="instance_", suffix=".dzn", delete=True
        ) as instance_file:
            instance_file.write(instance_bytes)
            instance_file.flush()
            result = await solve(
                SatRequest(
                    request.solver_name,
                    problem_file.name,
                    instance_file.name,
                    config.cpu.limit,
                )
            )

    response = SatResponse(
        result.solve_time.total_seconds(),
        request.solver_id,
        config.cpu.limit,
        request.problem_id,
        request.instance_id,
        None,
    )
    if type(result) is SatSolution:
        response.result = SatSolutionResponse(str(result.solution))
    elif type(result) is SatError:
        response.result = SatErrorResponse(result.error_message)
    else:
        raise ValueError(f"Unknown result type: {type(result)}")

    return response.to_dict()
