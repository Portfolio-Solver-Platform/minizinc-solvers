import os
from dataclasses import dataclass, field


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
    debug: str = os.getenv("DEBUG", "false").lower() == "true"
    service: ServiceConfig = field(default_factory=ServiceConfig)
    api: ApiConfig = field(default_factory=ApiConfig)

    class Queue:
        DEBUG = os.getenv("DEBUG", "false").lower() == "true"
