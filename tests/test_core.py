import json
import sqlite3
from dataclasses import replace
from pathlib import Path
import pytest
from evidencedesk.documents import Document, load_documents
from evidencedesk.evaluate import evaluate
from evidencedesk.ingest import chunks, replace_document
from evidencedesk.hybrid import bm25, rrf, expand_parents
from evidencedesk.tickets import Approval, payload_hash, submit
from evidencedesk.memory import PreferenceMemory

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("k", [1, 3])
def test_baseline(k):
    rows = [json.loads(line) for line in (ROOT / "data/questions.jsonl").read_text().splitlines()]
    result = evaluate(rows, load_documents(ROOT / "data/sample"), k)
    assert result["recall"] == pytest.approx(5 / 6)
    assert result["mrr"] == pytest.approx(5 / 6)
    assert result["unanswerable_empty_rate"] == 1
    assert result["details"][5]["retrieved"] == []

def test_empty_metrics():
    assert evaluate([], [], 1)["recall"] is None
    row = {"id": "none", "question": "未知", "answerable": False, "relevant_document_ids": []}
    assert evaluate([row], [], 1)["mrr"] is None
    with pytest.raises(ValueError):
        evaluate([row, row], [], 1)

@pytest.mark.parametrize("size,overlap", [(0, 0), (20, 20), (20, -1), (True, 0), (1.2, 0)])
def test_invalid_chunks(size, overlap):
    with pytest.raises(ValueError):
        chunks(Document("x", "title", "body", "x.md"), size, overlap)

def test_chunk_coverage_and_versions():
    doc = Document("x", "title", "0123456789" * 40, "x.md")
    parts = chunks(doc, 120, 20)
    positions = set()
    for part in parts:
        assert part["text"] == doc.text[part["start"]:part["end"]]
        positions.update(range(part["start"], part["end"]))
    assert positions == set(range(len(doc.text)))
    index = replace_document({}, doc)
    assert replace_document(index, doc) == index
    changed = replace_document(index, replace(doc, text="short changed text"))
    assert set(index).isdisjoint(changed)
    assert len(changed) == 1

def test_hybrid():
    assert bm25(["a"], {"x": ["a", "a"], "y": ["b"]})[0][0] == "x"
    assert bm25(["a"], {"x": []}) == []
    assert bm25(["a"], {"empty": [], "match": ["a"]}, b=1)[0][0] == "match"
    assert rrf([["a", "a"], ["b", "a"]]) == rrf([["a"], ["b", "a"]])
    assert rrf([["a"], ["b", "a"]])[0][0] == "a"
    assert expand_parents(["a", "b"], {"a": "p", "b": "p"}) == ["p"]

def test_tickets():
    conn = sqlite3.connect(":memory:")
    payload = {"title": "Test", "priority": "P1"}
    approval = Approval("alpha", "alice", payload_hash(payload))
    with pytest.raises(PermissionError):
        submit(conn, "alpha", "alice", "id-1", payload, None)
    with pytest.raises(PermissionError):
        submit(conn, "beta", "alice", "id-1", payload, approval)
    first = submit(conn, "alpha", "alice", "id-1", payload, approval)
    assert first == submit(conn, "alpha", "alice", "id-1", payload, approval)
    edited = {**payload, "title": "changed"}
    with pytest.raises(PermissionError):
        submit(conn, "alpha", "alice", "id-1", edited, approval)
    with pytest.raises(ValueError):
        submit(conn, "alpha", "alice", "id-1", edited, Approval("alpha", "alice", payload_hash(edited)))
    assert conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 1
    conn.close()

def test_ticket_persistence(tmp_path):
    db = tmp_path / "tickets.db"
    payload = {"title": "Test", "priority": "P3"}
    approval = Approval("a", "u", payload_hash(payload))
    with sqlite3.connect(db) as conn:
        first = submit(conn, "a", "u", "r", payload, approval)
    with sqlite3.connect(db) as conn:
        assert submit(conn, "a", "u", "r", payload, approval) == first

def test_memory():
    memory = PreferenceMemory()
    with pytest.raises(PermissionError):
        memory.save("a", "u", "zh-CN", False, 0, 30)
    memory.save("a", "u", "zh-CN", True, 0, 30)
    assert memory.get("a", "u", 29) == "zh-CN"
    assert memory.get("b", "u", 1) is None
    assert memory.get("a", "other", 1) is None
    assert memory.get("a", "u", 30) is None
    memory.save("a", "u", "en", True, 40, 30)
    memory.forget("a", "u")
    assert memory.get("a", "u", 41) is None
    assert PreferenceMemory().records == {}
