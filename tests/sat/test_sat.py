from psp_solver_sdk.sat.solver import _solve_loop
import json
import datetime
from tests.mocks import mock_process_loop
from tests.sat.mocks import mock_get_request_content, load_file
from psp_solver_sdk.config import SolverConfig
from psp_solver_sdk.sat import SatRequest, SatSolution, SatError
from psp_solver_sdk.sat.response import SatSolutionResponse, SatErrorResponse


async def test_solve(monkeypatch, mock_env):
    solution_input_dict = {
        "solver_id": 2,
        "solver_name": "solution",
        "problem_id": 3,
        "instance_id": 4,
        "problem_url": "problem_url",
        "instance_url": "instance_url",
    }
    error_input_dict = {
        "solver_id": 2,
        "solver_name": "error",
        "problem_id": 3,
        "instance_id": 4,
        "problem_url": "problem_url",
        "instance_url": "instance_url",
    }
    input_bytes = [
        json.dumps(d).encode() for d in [solution_input_dict, error_input_dict]
    ]
    file_contents = {
        "problem_url": load_file("tests/sat/fixtures/problem"),
        "instance_url": load_file("tests/sat/fixtures/instance"),
    }

    async def solve(request: SatRequest) -> SatSolution | SatError:
        assert request.vcpus == 1
        if request.solver == "solution":
            return SatSolution(
                "my solution", datetime.timedelta(seconds=2, milliseconds=200)
            )
        elif request.solver == "error":
            return SatError("my error")
        else:
            raise ValueError("Solver is neither solution nor error")

    def output_check(outputs: list[bytes]) -> None:
        outputs = [json.loads(output) for output in outputs]
        output_fields = [
            "version",
            "solver_id",
            "vcpus",
            "problem_id",
            "instance_id",
            "result",
        ]
        success_result_fields = ["kind", "solution", "solve_time"]
        error_result_fields = ["kind", "error_message"]
        for output in outputs:
            for field in output_fields:
                assert field in output
        for field in success_result_fields:
            assert field in outputs[0]["result"]
        for field in error_result_fields:
            assert field in outputs[1]["result"]

    mock_process_loop(monkeypatch, input_bytes, output_check)
    mock_get_request_content(monkeypatch, file_contents)
    await _solve_loop(solve, SolverConfig())
