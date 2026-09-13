#: mean 做宏平均；评测依赖检索，但不能把金标准输入给检索器。
import argparse
import json
from pathlib import Path
from statistics import mean
from .documents import load_documents
from .search import search

#: 即使评测集为空也要校验 k；None 在 JSON 中会变成 null，表示无定义。
def evaluate(rows: list[dict], documents: list, k: int) -> dict:
    if type(k) is not int or k <= 0:
        raise ValueError("k 必须是正整数")
    recalls, ranks, empty_returns, details = [], [], [], []
    known = {doc.id for doc in documents}
    seen = set()
    for row in rows:
        gold = set(row["relevant_document_ids"])
        if row["id"] in seen or not gold <= known or bool(gold) != row["answerable"]:
            raise ValueError(f"{row['id']}: 重复 ID、未知文档或标注不一致")
        seen.add(row["id"])
        #: 检索只接收 question；reference_facts 不参与检索，防止答案泄漏。
        hits = search(row["question"], documents, k)
        retrieved = [hit.document_id for hit in hits]
        recall = len(gold & set(retrieved)) / len(gold) if gold else None
        if gold:
            recalls.append(recall)
            rank = next((i for i, doc_id in enumerate(retrieved, 1) if doc_id in gold), None)
            ranks.append(1 / rank if rank else 0)
        else:
            empty_returns.append(not retrieved)
        #: 保存逐题结果比只看均值更容易定位失败。
        details.append({"id": row["id"], "retrieved": retrieved,
                        "scores": [hit.score for hit in hits], "recall": recall})
    return {"k": k, "recall": mean(recalls) if recalls else None,
            "mrr": mean(ranks) if ranks else None,
            "unanswerable_empty_rate": mean(empty_returns) if empty_returns else None,
            "details": details}

#: JSONL 每行一个对象；从根目录运行，切换 k 时保留相同数据与代码版本。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=Path("data/questions.jsonl"))
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--k", type=int, default=1)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.questions.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(evaluate(rows, load_documents(args.data_dir), args.k), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
