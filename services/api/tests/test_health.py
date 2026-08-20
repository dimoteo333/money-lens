"""/health acceptance tests (M0-02).

GET /health must not expose provider or secret information.
"""

from fastapi.testclient import TestClient

from app.main import API_VERSION, APP_NAME, app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == APP_NAME
    assert body["version"] == API_VERSION


def test_health_has_no_provider_or_secret_fields() -> None:
    body = client.get("/health").json()
    forbidden = {
        "provider",
        "providers",
        "secret",
        "secrets",
        "token",
        "key",
        "api_key",
        "password",
        "env",
        "config",
        "credentials",
    }
    for field in body:
        assert field.lower() not in forbidden, f"/health leaks field: {field}"
    assert set(body) == {"status", "service", "version"}
