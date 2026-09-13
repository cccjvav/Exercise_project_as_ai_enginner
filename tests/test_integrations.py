import importlib.util
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.skipif(importlib.util.find_spec("qdrant_client") is None, reason="optional vector extra")
def test_qdrant():
    result = subprocess.run([sys.executable, "-m", "examples.vector_geometry"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

@pytest.mark.skipif(importlib.util.find_spec("langgraph") is None, reason="optional workflow extra")
@pytest.mark.parametrize("decision,expected", [(True, "ready_for_authorized_tool"), (False, "rejected"), ("true", "rejected")])
def test_graph(decision, expected):
    from examples.approval_graph import build_graph
    from langgraph.types import Command
    graph = build_graph()
    config = {"configurable": {"thread_id": "test:actor:1"}}
    result = graph.invoke({"draft": "draft", "approved": False, "status": "draft"}, config)
    assert "__interrupt__" in result
    assert graph.invoke(Command(resume=decision), config)["status"] == expected

@pytest.mark.skipif(importlib.util.find_spec("mcp") is None, reason="optional MCP extra")
def test_mcp():
    result = subprocess.run([sys.executable, "-m", "examples.mcp_client"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "webhook-delivery" in result.stdout

@pytest.mark.skipif(importlib.util.find_spec("pypdf") is None, reason="optional ingest extra")
def test_pdf_fixture_and_empty_page(tmp_path):
    from pypdf import PdfReader, PdfWriter
    from examples.make_demo_pdf import main
    import os
    previous = Path.cwd()
    try:
        os.chdir(tmp_path)
        main()
        assert "Webhook retries: 3." in PdfReader("artifacts/demo.pdf").pages[0].extract_text()
    finally:
        os.chdir(previous)
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    target = tmp_path / "blank.pdf"
    with target.open("wb") as handle:
        writer.write(handle)
    result = subprocess.run([sys.executable, "-m", "examples.pdf_tokens", str(target)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0 and "无文本层" in result.stderr
