#: 哈希记录内容版本；JSON 编码复合身份避免拼接歧义。
import hashlib
import json
from .documents import Document

#: 本实现按字符分块，绝非 token 分块；步长必须正，否则可能死循环。
def chunks(doc: Document, size: int = 120, overlap: int = 20) -> list[dict]:
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("要求整数且 0 <= overlap < size")
    version = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
    result = []
    #: 半开区间 [start,end) 可直接定位 Python 字符串；版本变化时全部块 ID 变化。
    for start in range(0, len(doc.text), size - overlap):
        end = min(start + size, len(doc.text))
        identity = json.dumps([doc.id, version, size, overlap, start], ensure_ascii=False)
        chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        result.append({"id": chunk_id, "parent_id": doc.id, "version": version,
                       "source": doc.source, "start": start, "end": end, "text": doc.text[start:end]})
        if end == len(doc.text):
            break
    return result

#: 先剔除该父文档旧块，再合入新块；返回新字典，校验失败也不破坏旧索引。
def replace_document(index: dict[str, dict], doc: Document, size: int = 120) -> dict[str, dict]:
    updated = {key: value for key, value in index.items() if value["parent_id"] != doc.id}
    updated.update({chunk["id"]: chunk for chunk in chunks(doc, size)})
    return updated
