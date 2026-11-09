"""2A-Q7 实操：正文更新后，用 replace_document 整体替换这篇文档的块。

直接运行：python scratch_replace.py
预期输出：
    3 1
    3 1
第一个数是索引里的块数，第二个数是父文档数。
想对照"用 update 会残留旧块"，把最后两行换成课程里的写法即可。
"""
from dataclasses import replace
from pathlib import Path

from evidencedesk.documents import load_documents
from evidencedesk.ingest import chunks, replace_document

doc = load_documents(Path("data/sample"))[0]
index = {p["id"]: p for p in chunks(doc)}
print(len(index), len({p["parent_id"] for p in index.values()}))

edited = replace(doc, text=doc.text + "新增一句说明。")
index = replace_document(index, edited)
print(len(index), len({p["parent_id"] for p in index.values()}))
