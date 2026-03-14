from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_aapl_analysis():
    r = client.get("/analysis/AAPL")
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["status"] == "analyzed"


def test_special_case_analysis():
    r = client.get("/analysis/SANA")
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["status"] == "special_case_excluded"


def test_unsupported_analysis():
    r = client.get("/analysis/SPY")
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["status"] == "unsupported_asset"


def test_ui_routes():
    assert client.get("/").status_code == 200
    assert client.get("/ui").status_code == 200
