import src.minizinc as minizinc
from psp_solver_sdk.sat import SatRequest, SatSolution


async def test_solve():
    request = SatRequest(
        "coinbc", "tests/sat/fixtures/problem.mzn", "tests/sat/fixtures/instance.dzn", 1, 300
    )
    result = await minizinc.solve(request)
    assert type(result) is SatSolution
