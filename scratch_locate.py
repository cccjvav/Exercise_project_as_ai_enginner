"""2A-Q5 实操：在真实手册上定位一个块。

直接运行：python scratch_locate.py
预期前两行：
    api-key-policy 243
    3 [(0, 120), (100, 220), (200, 243)]
最后一行断言通过时不打印任何内容。
"""
from pathlib import Path

from evidencedesk.documents import load_documents
from evidencedesk.ingest import chunks

doc = load_documents(Path("data/sample"))[0]
print(doc.id, len(doc.text))

parts = chunks(doc)
print(len(parts), [(p["start"], p["end"]) for p in parts])

part = parts[1]
print(part["parent_id"], part["source"], part["start"], part["end"])
assert doc.text[part["start"]:part["end"]] == part["text"]
