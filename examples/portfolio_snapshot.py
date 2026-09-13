#: 从当前代码和数据生成真实基线报告；不手填改善百分比或模型效果。
import hashlib
import json
from pathlib import Path
from evidencedesk.documents import load_documents
from evidencedesk.evaluate import evaluate

#: 哈希含文件名及内容，用于识别语料变动；不是将 hash 当隐私保护。
def main():
    paths = sorted(Path("data/sample").glob("*.md")) + [Path("data/questions.jsonl")]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.as_posix().encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    rows = [json.loads(line) for line in Path("data/questions.jsonl").read_text(encoding="utf-8").splitlines()]
    result = {"system": "lexical-baseline", "dataset_sha256": digest.hexdigest(),
              "synthetic_data": True, "question_count": len(rows),
              "metrics": evaluate(rows, load_documents(Path("data/sample")), 1),
              "limitations": ["公开开发题不是最终测试集", "未评估生成答案", "q06 有隐含 Webhook 上下文"]}
    target = Path("artifacts/baseline-report.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)

if __name__ == "__main__":
    main()
