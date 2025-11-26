import os
from dataclasses import dataclass, field


def _env(name: str, default: str | None = None) -> str:
    try:
        return os.environ[name]
    except KeyError as e:
        if default is not None:
            return default
        raise ValueError(
            f"Environment variable '{name}' not found. Please set it in the configuration or as an environment variable before running the application"
        ) from e


@dataclass
class CpuConfig:
    limit: int = int(_env("CPU_LIMIT"))


@dataclass
class QueueAuthConfig:
    host: str = _env("QUEUE_HOST")
    port: int = _env("QUEUE_PORT")
    user: str = _env("QUEUE_USER")
    password: str = _env("QUEUE_PASSWORD")


@dataclass
class QueueConfig:
    request_timeout: tuple[int, int] = (1, 5)
    in_name: str = _env("QUEUE_IN_NAME")
    out_name: str = _env("QUEUE_OUT_NAME")

    auth: QueueAuthConfig = field(default_factory=QueueAuthConfig)


@dataclass
class ServiceConfig:
    name: str = "solver"
    version: str = "0.1.0"


@dataclass
class ApiConfig:
    title_prefix: str = "Solver API: "
    description: str = "API to see information about the solver"
    version: str = "v1"
    root_path: str = "/"


@dataclass
class SolverConfig:
    debug: str = _env("DEBUG", "false").lower() == "true"
    service: ServiceConfig = field(default_factory=ServiceConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    cpu: CpuConfig = field(default_factory=CpuConfig)
    queue: QueueConfig = field(default_factory=QueueConfig)
