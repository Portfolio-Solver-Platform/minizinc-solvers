import asyncio
from typing import Callable, Awaitable
from fastapi import FastAPI
from ..queue import QueueMessageProcessor
from .process import sat_process
from .results import SatError, SatRequest, SatSolution

from ..config import SolverConfig
from ..routers import health, version
import prometheus_fastapi_instrumentator
from contextlib import asynccontextmanager


async def _solve_loop(
    solve: Callable[[SatRequest], Awaitable[SatSolution | SatError]],
    config: SolverConfig | None = None,
):
    async def process(data: dict) -> dict:
        return await sat_process(data, solve, config)

    queue_processor = QueueMessageProcessor(config.queue)
    await queue_processor.json_process_loop(process)


def sat_solver(
    name: str,
    solve: Callable[[SatRequest], Awaitable[SatSolution | SatError]],
    config: SolverConfig | None = None,
) -> FastAPI:
    if config is None:
        config = SolverConfig()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async def task():
            await _solve_loop(solve, config)

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
