#: asdict 用于将数据类变为 JSON 可编码的字典；相对导入要求以包方式运行。
import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from .documents import Document, load_documents

#: 固定领域词表是教学基线，不是中文分词器或语义模型；集合去除重复词。
TERMS = ("webhook", "重试", "签名", "密钥", "轮换", "工单", "升级", "故障")

def tokens(text: str) -> set[str]:
    return {term for term in TERMS if term in text.casefold()}

#: Hit 保留完整原文与来源；score 仅表示词覆盖率，不是回答正确概率。
@dataclass(frozen=True)
class SearchHit:
    document_id: str
    title: str
    score: float
    text: str
    source: str

#: bool 在 Python 是 int 子类，故用 type 而非 isinstance 排除 True/False。
def search(query: str, documents: list[Document], k: int = 3) -> list[SearchHit]:
    if type(k) is not int or k <= 0:
        raise ValueError("k 必须是正整数，不接受布尔值")
    query_terms = tokens(query)
    if not query_terms:
        return []
    #: 交集计算覆盖词数；先处理空集合，才能避免除以零。search 不做文件 I/O。
    hits = []
    for doc in documents:
        score = len(query_terms & tokens(doc.title + "\n" + doc.text)) / len(query_terms)
        if score > 0:
            hits.append(SearchHit(doc.id, doc.title, score, doc.text, doc.source))
    #: 负号实现降序；同分时按 ID 升序。不原地排序输入，调用方数据不会改变。
    return sorted(hits, key=lambda hit: (-hit.score, hit.document_id))[:k]

#: argparse 将终端字符串解析成类型化参数；默认数据目录相对于当前工作目录。
def main() -> None:
    parser = argparse.ArgumentParser(description="返回候选证据，不生成答案")
    parser.add_argument("--query", required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()
    #: 文件与参数错误写入 stderr 并以非零状态退出；成功输出只有可解析 JSON。
    try:
        hits = search(args.query, load_documents(args.data_dir), args.k)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps([asdict(hit) for hit in hits], ensure_ascii=False, indent=2))

#: 导入模块不会执行 CLI；运行 python -m evidencedesk.search 才进入 main。
if __name__ == "__main__":
    main()
