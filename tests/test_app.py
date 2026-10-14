import httpx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_quote_returns_upstream_data(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"fact": "cats sleep a lot"}

    monkeypatch.setattr(httpx, "get", lambda url, timeout: FakeResponse())
    r = client.get("/quote")
    assert r.status_code == 200
    assert r.json()["data"]["fact"] == "cats sleep a lot"


def test_quote_upstream_failure_is_502(monkeypatch):
    def boom(url, timeout):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(httpx, "get", boom)
    assert client.get("/quote").status_code == 502
