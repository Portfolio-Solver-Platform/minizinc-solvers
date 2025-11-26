from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SolverRequest:
    solver_id: int
    solver_name: str
    problem_id: int
    instance_id: int
    problem_url: str
    instance_url: str

    def from_dict(data: dict) -> SolverRequest:
        return SolverRequest(
            data["solver_id"],
            data["solver_name"],
            data["problem_id"],
            data["instance_id"],
            data["problem_url"],
            data["instance_url"],
        )
