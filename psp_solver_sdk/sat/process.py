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
import time

_token_cache: dict = {"token": None, "expires_at": 0.0}  # nosec B105


async def _get_service_token(config: SolverConfig) -> str:
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 15:
        return _token_cache["token"]
    timeout = httpx.Timeout(5.0, connect=2.0)
    async with httpx.AsyncClient(timeout=timeout) as http:
        r = await http.get(config.keycloak.well_known_url)
        r.raise_for_status()
        token_endpoint = r.json()["token_endpoint"]
        r = await http.post(token_endpoint, data={
            "grant_type": "client_credentials",
            "client_id": config.keycloak.client_id,
            "client_secret": config.keycloak.client_secret,
            "scope": "solver-director:problems:read",
        })
        r.raise_for_status()
        data = r.json()
        _token_cache["token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data.get("expires_in", 300)
        return _token_cache["token"]


async def _make_get_request(url: str, config: SolverConfig) -> httpx.Response:
    token = await _get_service_token(config)
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.get(url, headers={"Authorization": f"Bearer {token}"})


async def _get_text_from_url(url: str, config: SolverConfig) -> str:
    response = await _make_get_request(url, config)
    return response.text


async def sat_process(
    data: dict,
    solve: Callable[[SatRequest], Awaitable[SatSolution | SatError]],
    config: SolverConfig,
) -> dict:
    request = SolverRequest.from_dict(data)
    problem_bytes = await _get_text_from_url(request.problem_url, config)
    instance_bytes = await _get_text_from_url(request.instance_url, config)
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
                    config.cpu.timeout,
                )
            )

    response = SatResponse(
        request.solver_id,
        config.cpu.limit,
        request.problem_id,
        request.instance_id,
        None,
    )
    if type(result) is SatSolution:
        response.result = SatSolutionResponse(
            str(result.solution), result.solve_time.total_seconds()
        )
    elif type(result) is SatError:
        response.result = SatErrorResponse(result.error_message)
    else:
        raise ValueError(f"Unknown result type: {type(result)}")

    return response.to_dict()
