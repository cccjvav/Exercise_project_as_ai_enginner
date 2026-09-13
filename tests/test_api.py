import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from evidencedesk.api import app

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("EVIDENCEDESK_DEMO", "1")
    with TestClient(app) as client:
        yield client

def test_health_and_default_closed(client, monkeypatch):
    assert client.get("/health").status_code == 200
    monkeypatch.delenv("EVIDENCEDESK_DEMO")
    assert client.post("/api/search", json={"question": "工单"}).status_code == 503

def test_auth_acl_and_sse(client):
    payload = {"question": "工单", "k": 3}
    assert client.post("/api/search", json=payload).status_code == 401
    a = {"Authorization": "Bearer demo-alice"}
    b = {"Authorization": "Bearer demo-bob"}
    assert client.post("/api/search", json=payload, headers=a).json() == []
    assert client.post("/api/search", json=payload, headers=b).json()[0]["document_id"] == "incident-escalation"
    stream = client.post("/api/events", json=payload, headers=b)
    assert stream.headers["content-type"].startswith("text/event-stream")
    assert "event: evidence\n" in stream.text and stream.text.endswith('event: done\ndata: {}\n\n')
    for k in [0, True, "3", 11]:
        assert client.post("/api/search", json={"question": "工单", "k": k}, headers=b).status_code == 422
