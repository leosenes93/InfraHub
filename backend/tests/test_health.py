def test_health_returns_ok(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_dependencies(client):
    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert "database" in body
    assert "redis" in body
