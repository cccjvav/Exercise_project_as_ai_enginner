#: 与其靠正则猜所有敏感信息，不如默认不采集原始请求、原文和凭据。
import json
import time
from pathlib import Path
from evidencedesk.documents import load_documents
from evidencedesk.search import search

#: perf_counter 衡量持续时间，不受系统时钟回拨影响；这里不测模型延迟。
def main():
    documents = load_documents(Path("data/sample"))
    started = time.perf_counter()
    hits = search("Webhook 重试", documents, 2)
    trace = {"operation": "lexical_retrieval", "duration_ms": round((time.perf_counter() - started) * 1000, 3),
             "candidate_count": len(hits), "error_type": None, "model_calls": 0}
    print(json.dumps(trace, ensure_ascii=False))
    assert "question" not in trace and "authorization" not in trace

if __name__ == "__main__":
    main()
