import datetime
from dataclasses import dataclass


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
