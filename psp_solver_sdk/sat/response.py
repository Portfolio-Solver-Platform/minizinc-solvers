from dataclasses import dataclass, asdict


@dataclass
class SatSolutionResponse:
    solution: str
    kind: str = "optimal"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SatErrorResponse:
    error_message: str
    kind: str = "error"

    def to_dict(self) -> dict:
        return asdict(self)


RESPONSE_VERSION: int = 1


@dataclass
class SatResponse:
    solve_time: float
    solver_id: int
    vcpus: int
    problem_id: int
    instance_id: int
    result: SatSolutionResponse | SatErrorResponse
    version: int = RESPONSE_VERSION

    def to_dict(self) -> dict:
        return asdict(self)
