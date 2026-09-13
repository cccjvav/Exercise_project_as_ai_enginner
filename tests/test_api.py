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

#: 浏览器的专用演示头必须保持双向 ACL，而不是遇到 401 就关闭身份检查。
@pytest.mark.parametrize("token,query,ids", [
    ("demo-alice", "Webhook", ["webhook-delivery"]),
    ("demo-bob", "Webhook", []),
    ("demo-bob", "工单", ["incident-escalation"]),
    ("demo-alice", "工单", []),
])
def test_demo_header_acl(client, token, query, ids):
    response = client.post("/api/search", headers={"X-Demo-Token": token}, json={"question": query})
    assert response.status_code == 200
    assert [hit["document_id"] for hit in response.json()] == ids


#: 无效专用头不回退到另一套凭据；关闭演示模式时，两种头都不能启用接口。
@pytest.mark.parametrize("token", ["", "unknown", "Bearer demo-alice"])
def test_invalid_demo_header_does_not_fall_back(client, token):
    response = client.post("/api/search", headers={"X-Demo-Token": token, "Authorization": "Bearer demo-alice"},
                           json={"question": "Webhook"})
    assert response.status_code == 401


def test_demo_header_still_requires_explicit_mode(client, monkeypatch):
    monkeypatch.delenv("EVIDENCEDESK_DEMO")
    response = client.post("/api/search", headers={"X-Demo-Token": "demo-alice"}, json={"question": "Webhook"})
    assert response.status_code == 503


#: 模拟代理剥离 Authorization，验证专用头仍可用；这不是对真实代理行为的直接观测。
def test_preview_transport_with_authorization_stripped(monkeypatch):
    # Model the suspected proxy behavior, without claiming this observes the real proxy.
    class StripAuthorization:
        def __init__(self, wrapped):
            self.wrapped = wrapped

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                scope = {**scope, "headers": [(k, v) for k, v in scope["headers"] if k.lower() != b"authorization"]}
            await self.wrapped(scope, receive, send)

    monkeypatch.setenv("EVIDENCEDESK_DEMO", "1")
    with TestClient(StripAuthorization(app)) as proxied:
        payload = {"question": "Webhook"}
        assert proxied.post("/api/search", headers={"Authorization": "Bearer demo-alice"}, json=payload).status_code == 401
        response = proxied.post("/api/search", headers={"X-Demo-Token": "demo-alice"}, json=payload)
        assert response.status_code == 200 and response.json()[0]["document_id"] == "webhook-delivery"
        events = proxied.post("/api/events", headers={"X-Demo-Token": "demo-alice"}, json=payload)
        assert events.status_code == 200 and "event: evidence" in events.text


def test_proxy_authorization_can_coexist_with_demo_header(client):
    response = client.post("/api/search", headers={"Authorization": "Bearer proxy-owned-placeholder", "X-Demo-Token": "demo-bob"},
                           json={"question": "工单"})
    assert response.status_code == 200 and response.json()[0]["document_id"] == "incident-escalation"
