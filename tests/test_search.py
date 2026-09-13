#: tmp_path 由 pytest 提供，测试不修改真实语料；每个用例拥有独立临时目录。
import json
import subprocess
import sys
from pathlib import Path
import pytest
from evidencedesk.documents import Document, load_documents
from evidencedesk.search import search

ROOT = Path(__file__).resolve().parents[1]

#: 断言字段而不仅是数量；读取失败、格式错误和空目录应表现不同。
def test_loading(tmp_path):
    (tmp_path / "x.md").write_text("# 中文标题\n\n中文正文\n", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("not a document")
    assert load_documents(tmp_path) == [Document("x", "中文标题", "中文正文", "x.md")]

@pytest.mark.parametrize("content", ["", "无标题\n正文", "# \n正文", "# 标题\n\n"])
def test_invalid_document(tmp_path, content):
    (tmp_path / "bad.md").write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="bad.md"):
        load_documents(tmp_path)

def test_directory_errors(tmp_path):
    assert load_documents(tmp_path) == []
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "missing")
    file = tmp_path / "file"
    file.touch()
    with pytest.raises(NotADirectoryError):
        load_documents(file)

#: 通过人工可算的分数建立 oracle；打乱输入、重复查询词不应改结果。
def test_scores_order_and_no_mutation():
    docs = [Document("z", "Webhook", "重试", "z.md"), Document("a", "Webhook", "重试", "a.md"), Document("b", "重试", "说明", "b.md")]
    original = docs.copy()
    hits = search("WEBHOOK 重试 重试", docs, 10)
    assert [(h.document_id, h.score) for h in hits] == [("a", 1), ("z", 1), ("b", 0.5)]
    assert docs == original
    assert search("webhook 重试", list(reversed(docs)), 10) == hits

@pytest.mark.parametrize("k", [0, -1, True, False, 1.5, "1"])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        search("", [], k)

@pytest.mark.parametrize("query", ["", "   ", "消息没送到还会再发吗？"])
def test_no_terms(query):
    assert search(query, load_documents(ROOT / "data/sample")) == []

#: 子进程检查真实 CLI 行为，而不是只测试内部函数。
def test_cli():
    result = subprocess.run([sys.executable, "-m", "evidencedesk.search", "--query", "Webhook 重试"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)[0]["document_id"] == "webhook-delivery"
    bad = subprocess.run([sys.executable, "-m", "evidencedesk.search", "--query", "x", "--k", "0"], cwd=ROOT, capture_output=True, text=True)
    assert bad.returncode != 0 and not bad.stdout
