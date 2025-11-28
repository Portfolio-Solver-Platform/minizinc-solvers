def test_health_endpoint(sat_client):
    response = sat_client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_ready_endpoint(sat_client):
    response = sat_client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_version_endpoint(sat_client):
    response = sat_client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data.keys() == {"service", "version", "api_version"}
