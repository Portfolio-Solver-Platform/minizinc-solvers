from psp_solver_sdk.sat.solver import _solve_loop
import json
from tests.mocks import mock_process_loop
from tests.sat.mocks import mock_get_request_content, load_file
from src.minizinc import solve
from psp_solver_sdk.config import SolverConfig


async def test_solve(monkeypatch, mock_env):
    input_dict = {
        "solver_id": 2,
        "solver_name": "coinbc",
        "problem_id": 3,
        "instance_id": 4,
        "problem_url": "problem_url",
        "instance_url": "instance_url",
    }
    input_bytes = json.dumps(input_dict).encode()
    file_contents = {
        "problem_url": load_file("tests/sat/fixtures/problem"),
        "instance_url": load_file("tests/sat/fixtures/instance"),
    }

    def output_check(outputs: list[bytes]) -> None:
        output_fields = [
            "version",
            "solve_time",
            "solver_id",
            "vcpus",
            "problem_id",
            "instance_id",
            "result",
        ]
        for output_bytes in outputs:
            output = json.loads(output_bytes.decode())
            for field in output_fields:
                assert field in output

    mock_process_loop(monkeypatch, [input_bytes], output_check)
    mock_get_request_content(monkeypatch, file_contents)
    await _solve_loop(solve, SolverConfig())
