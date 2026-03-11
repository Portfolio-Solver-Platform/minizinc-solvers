import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psp_solver_sdk.sat import sat_solver
from tests.mocks import mock_process_loop


@pytest.fixture
def sat_app(mock_env, monkeypatch) -> FastAPI:
    def do_nothing(*args, **kwargs):
        pass

    # Do no checks
    mock_process_loop(monkeypatch, [], do_nothing)
    yield sat_solver("MiniZinc", do_nothing)


@pytest.fixture
def sat_client(sat_app):
    """Test client"""
    with TestClient(sat_app) as client:
        yield client


@pytest.fixture
def mock_env(monkeypatch):
    values = {
        "CPU_LIMIT": "1",
        "SOLVER_TIMEOUT": "300",
        "QUEUE_IN_NAME": "inqueue",
        "QUEUE_OUT_NAME": "outqueue",
        "QUEUE_HOST": "queuehost",
        "QUEUE_PORT": "8080",
        "QUEUE_USER": "queue_user",
        "QUEUE_PASSWORD": "queue_password",
    }

    for key, value in values.items():
        monkeypatch.setenv(key, value)
