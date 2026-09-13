#: replace 为 frozen 数据类创建修改后的副本，而不是原地写入。
from pathlib import Path
from dataclasses import replace
from evidencedesk.documents import load_documents
from evidencedesk.ingest import chunks, replace_document

#: 同样输入重复导入得到同一结果，这是幂等；不是“没有异常”就算幂等。
def main():
    doc = load_documents(Path("data/sample"))[0]
    index = replace_document({}, doc)
    assert replace_document(index, doc) == index
    #: 增加内容会换版本；确认新快照没有旧块，避免过期内容继续被搜到。
    changed = replace(doc, text=doc.text + "\n练习：增加一条说明。")
    new_index = replace_document(index, changed)
    assert set(index).isdisjoint(new_index)
    print({"initial_chunks": len(chunks(doc)), "updated_chunks": len(new_index), "old_chunks_removed": True})

if __name__ == "__main__":
    main()
