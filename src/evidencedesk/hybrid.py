#: 教学版 BM25：先让公式可见，后续数据变大再换成熟索引实现。
import math
from collections import Counter, defaultdict

#: 查询分词由调用者负责；这里接收 token 列表，不把英语 split 冒充中文分词。
def bm25(query: list[str], corpus: dict[str, list[str]], k1: float = 1.5, b: float = 0.75):
    if not k1 > 0 or not 0 <= b <= 1:
        raise ValueError("要求 k1>0，0<=b<=1")
    if not corpus:
        return []
    n = len(corpus)
    average = sum(map(len, corpus.values())) / n
    if not average:
        return []
    #: df 是含词文档数；IDF 让稀有词更有区分力，不等于词越少越正确。
    df = Counter(term for terms in corpus.values() for term in set(terms))
    scores = []
    for doc_id, terms in corpus.items():
        tf = Counter(terms)
        score = 0.0
        for term in set(query):
            if not tf[term]:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            denominator = tf[term] + k1 * (1 - b + b * len(terms) / average)
            score += idf * tf[term] * (k1 + 1) / denominator
        if score > 0:
            scores.append((doc_id, score))
    return sorted(scores, key=lambda item: (-item[1], item[0]))

#: RRF 用排名融合而非相加不同量纲的原始分数；同一列表内去重防刷分。
def rrf(rankings: list[list[str]], c: int = 60):
    if c <= 0:
        raise ValueError("c 必须大于 0")
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(dict.fromkeys(ranking), 1):
            scores[doc_id] += 1 / (c + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))

#: 父子检索取回父级上下文并保留首次出现顺序；父文档仍需重新检查访问权限。
def expand_parents(child_ids: list[str], parent_by_child: dict[str, str]):
    return list(dict.fromkeys(parent_by_child[child_id] for child_id in child_ids))
