"""Contract and budget-guard tests use a mock transport, NOT real model results."""
import json
import pytest
httpx = pytest.importorskip("httpx")
from evidencedesk.agnes import answer, prepare, validate_answer


def test_dry_run_never_calls_network():
    def forbidden(request):
        raise AssertionError("dry-run tried network")
    assert "dry-run" in answer("Webhook", transport=httpx.MockTransport(forbidden))["mode"]


def test_explicit_opt_in_and_missing_key(monkeypatch):
    monkeypatch.delenv("AGNES_API_KEY", raising=False)
    with pytest.raises(ValueError, match="免费"):
        answer("Webhook", live=True)
    with pytest.raises(ValueError, match="AGNES_API_KEY"):
        answer("Webhook", live=True, confirmed_current_free=True)


def test_one_request_and_no_key_in_result(monkeypatch):
    monkeypatch.setenv("AGNES_API_KEY", "test-only-not-a-real-key")
    calls = []
    def handler(request):
        calls.append(request)
        payload = json.loads(request.content)
        assert str(request.url) == "https://apihub.agnes-ai.com/v1/chat/completions"
        assert payload["model"] == "agnes-2.5-flash" and payload["max_tokens"] == 400
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
            "answer": "最多重试 3 次，不包含首次投递。", "citation_ids": ["webhook-delivery"], "insufficient_evidence": False})}}]})
    result = answer("Webhook", live=True, confirmed_current_free=True, transport=httpx.MockTransport(handler))
    assert len(calls) == 1 and "test-only" not in json.dumps(result)


@pytest.mark.parametrize("status", [302, 401, 402, 429, 500])
def test_errors_no_retry_or_fallback(monkeypatch, status):
    monkeypatch.setenv("AGNES_API_KEY", "test-only")
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status, headers={"Location": "https://example.com"}, text="sensitive error not logged")
    with pytest.raises(RuntimeError, match=f"HTTP {status}") as caught:
        answer("Webhook", live=True, confirmed_current_free=True, transport=httpx.MockTransport(handler))
    assert len(calls) == 1 and "sensitive" not in str(caught.value)


@pytest.mark.parametrize("value", [
    {"answer": "x", "citation_ids": ["missing"], "insufficient_evidence": False},
    {"answer": "x", "citation_ids": [], "insufficient_evidence": False},
    {"answer": "x", "citation_ids": ["webhook-delivery"], "insufficient_evidence": True},
    {"answer": "x", "citation_ids": [], "insufficient_evidence": "true"},
])
def test_invalid_output(value):
    with pytest.raises(ValueError):
        validate_answer(json.dumps(value), {"webhook-delivery"})


def test_no_matching_evidence_skips_model(monkeypatch):
    monkeypatch.setenv("AGNES_API_KEY", "test-only")
    def forbidden(request):
        raise AssertionError("should not call for empty candidates")
    assert answer("年付折扣是多少？", live=True, confirmed_current_free=True,
                  transport=httpx.MockTransport(forbidden))["mode"] == "no model call"


def test_input_limit():
    for question in ("", " " * 5, "a" * 1001):
        with pytest.raises(ValueError):
            prepare(question)
