import os
from dataclasses import dataclass, field
from typing import Callable


def _env(name: str, default: str | None = None) -> str:
    try:
        return os.environ[name]
    except KeyError as e:
        if default is not None:
            return default
        raise ValueError(
            f"Environment variable '{name}' not found. Please set it in the configuration or as an environment variable before running the application"
        ) from e


def _env_field[T](
    name: str, default: str | None = None, process: Callable[[str], T] | None = None
) -> T:
    def default_process(x: str) -> str:
        return x

    if process is None:
        process = default_process

    return field(default_factory=lambda: process(_env(name, default)))


@dataclass
class CpuConfig:
    limit: int = _env_field("CPU_LIMIT", process=int)
    memory_gib: float = _env_field("MEMORY_LIMIT", process=float)
    timeout: int = _env_field("SOLVER_TIMEOUT", process=int)


@dataclass
class QueueAuthConfig:
    host: str = _env_field("QUEUE_HOST")
    port: int = _env_field("QUEUE_PORT", process=int)
    user: str = _env_field("QUEUE_USER")
    password: str = _env_field("QUEUE_PASSWORD")


@dataclass
class QueueConfig:
    request_timeout: tuple[int, int] = (1, 5)
    in_name: str = _env_field("QUEUE_IN_NAME")
    out_name: str = _env_field("QUEUE_OUT_NAME")
    consumer_timeout: int = _env_field("SOLVER_TIMEOUT", process=int)

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
class KeycloakConfig:
    client_id: str = _env_field("KEYCLOAK_CLIENT_ID", default="")
    client_secret: str = _env_field("KEYCLOAK_CLIENT_SECRET", default="")
    well_known_url: str = field(default="http://user.psp.svc.cluster.local:8080/v1/internal/.well-known/openid-configuration")


@dataclass
class SolverConfig:
    debug: bool = _env_field("DEBUG", "false", process=lambda s: s.lower() == "true")
    service: ServiceConfig = field(default_factory=ServiceConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    cpu: CpuConfig = field(default_factory=CpuConfig)
    queue: QueueConfig = field(default_factory=QueueConfig)
    keycloak: KeycloakConfig = field(default_factory=KeycloakConfig)
