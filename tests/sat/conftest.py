import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psp_solver_sdk.sat import sat_solver
from src.minizinc import solve


@pytest.fixture
def sat_app(mock_env, monkeypatch) -> FastAPI:
    monkeypatch.setenv("CPU_LIMIT", "2")
    yield sat_solver("MiniZinc", solve)


@pytest.fixture
def sat_client(sat_app):
    """Test client"""
    with TestClient(sat_app) as client:
        yield client


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("CPU_LIMIT", "2")
