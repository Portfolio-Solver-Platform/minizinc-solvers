from dataclasses import dataclass, asdict


@dataclass
class SatSolutionResponse:
    kind: str = "optimal"
    solution: str


@dataclass
class SatErrorResponse:
    kind: str = "error"
    error_message: str


RESPONSE_VERSION: int = 1


@dataclass
class SatResponse:
    version: int = RESPONSE_VERSION
    solve_time: float
    solver_id: int
    vcpus: int
    problem_id: int
    instance_id: int
    result: SatSolutionResponse | SatErrorResponse

    def to_dict(self) -> dict:
        return asdict(self)
