import asyncio
from typing import Callable
from fastapi import FastAPI
from dataclasses import dataclass
import datetime
from glob import glob

from .config import SolverConfig
from .routers import health, version
import prometheus_fastapi_instrumentator
from contextlib import asynccontextmanager


def problem_instances_from_file(path: str) -> tuple[str, list[str]]:
    problem = glob(f"{path}/*.mzn")[0]
    instances = glob(f"{path}/*.dzn")
    print(f"loaded {len(instances)} instances")
    return problem, instances


@dataclass
class SatRequest:
    solver: str
    problem: str
    instance: str
    vcpus: int


@dataclass
class SatSolution:
    solution: str
    solve_time: datetime.timedelta


@dataclass
class SatError:
    error_message: str


def sat_solver(
    name: str,
    solve: Callable[[SatRequest], SatSolution | SatError],
    config: SolverConfig = SolverConfig(),
) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        problem, instances = problem_instances_from_file("./problems/nfc")
        request = SatRequest("coinbc", problem, instances[0], 1)

        async def task():
            await solve(request)

        asyncio.create_task(task())
        yield

    app = FastAPI(
        debug=config.debug,
        root_path=config.api.root_path,
        title=f"{config.api.title_prefix}{name}",
        description=config.api.description,
        version=config.service.version,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["Health"])
    app.include_router(version.router(config), tags=["Info"])

    # Monitoring
    prometheus_fastapi_instrumentator.Instrumentator().instrument(app).expose(app)

    # Exclude /metrics from docs schema
    for route in app.routes:
        if route.path == "/metrics":
            route.include_in_schema = False
            break

    return app
