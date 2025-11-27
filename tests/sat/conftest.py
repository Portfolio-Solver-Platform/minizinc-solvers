import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psp_solver_sdk.sat import sat_solver
from src.minizinc import solve
from psp_solver_sdk.queue import QueueMessageProcessor
import json
from tests.mocks import mock_process_loop


@pytest.fixture
def sat_app(mock_env, monkeypatch) -> FastAPI:
    input_dict = {
        "solver_id": 2,
        "solver_name": "coinbc",
        "problem_id": 3,
        "instance_id": 4,
        "problem_url": "problem_url",
        "instance_url": "instance_url",
    }
    input_bytes = json.dumps(input_dict).encode()

    mock_process_loop(monkeypatch, [input_bytes])
    yield sat_solver("MiniZinc", solve)


@pytest.fixture
def sat_client(sat_app):
    """Test client"""
    with TestClient(sat_app) as client:
        yield client


@pytest.fixture
def mock_env(monkeypatch):
    values = {
        "CPU_LIMIT": "2",
        "QUEUE_IN_NAME": "inqueue",
        "QUEUE_OUT_NAME": "outqueue",
        "QUEUE_HOST": "queuehost",
        "QUEUE_PORT": "8080",
        "QUEUE_USER": "queue_user",
        "QUEUE_PASSWORD": "queue_password",
    }

    for key, value in values.items():
        monkeypatch.setenv(key, value)
