"""2A 闭卷小实现：分块区间的测试（导师提供；学习者只写实现，不改本文件）。

运行：python -m pytest tests/test_learning_02a.py -q
尚未创建实现文件时，本文件整体跳过，CI 保持通过。
"""
import pytest

module = pytest.importorskip("scratch_02a_ranges")
chunk_ranges = getattr(module, "chunk_ranges", None)
pytestmark = pytest.mark.skipif(chunk_ranges is None, reason="chunk_ranges 尚未实现")


def test_default_parameters_on_sample_length():
    # 与 2A-Q5 在真实手册上看到的区间一致。
    assert chunk_ranges(243, 120, 20) == [(0, 120), (100, 220), (200, 243)]


def test_small_text_with_overlap():
    # 步长 = 4 - 2 = 2，所以起点是 0、2、4、6，共四块。
    assert chunk_ranges(10, 4, 2) == [(0, 4), (2, 6), (4, 8), (6, 10)]


def test_overlap_one_less_than_size():
    # 步长为 1：每次只前进一个字符，直到某块覆盖到末尾。
    assert chunk_ranges(10, 4, 3) == [(0, 4), (1, 5), (2, 6), (3, 7), (4, 8), (5, 9), (6, 10)]


def test_text_shorter_than_size():
    assert chunk_ranges(3, 120, 20) == [(0, 3)]


def test_empty_text():
    assert chunk_ranges(0, 120, 20) == []


@pytest.mark.parametrize("length, size, overlap", [
    (243, 120, 120),   # overlap 等于 size，步长为 0
    (243, 120, -1),    # overlap 为负
    (243, 120.0, 20),  # size 不是 int
    (243, True, 0),    # bool 是 int 的子类，也要拒绝
])
def test_invalid_arguments(length, size, overlap):
    with pytest.raises(ValueError):
        chunk_ranges(length, size, overlap)


def test_agrees_with_reference_implementation():
    from pathlib import Path
    from evidencedesk.documents import load_documents
    from evidencedesk.ingest import chunks

    doc = load_documents(Path("data/sample"))[0]
    expected = [(chunk["start"], chunk["end"]) for chunk in chunks(doc)]
    assert chunk_ranges(len(doc.text), 120, 20) == expected
