# 4A · BM25 与混合检索

> **1A细度源码精讲（2026-09-19补充）：** [examples/hybrid_rankings.py](../code/examples--hybrid_rankings_py.md) · [src/evidencedesk/hybrid.py](../code/src--evidencedesk--hybrid_py.md) · [tests/test_core.py](../code/tests--test_core_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](03c-integrate-answer-api.md) · [下一课](04b-rerank-multiquery.md)

- **前置理解：** 阶段 3；理解词法与向量各自的失败
- **验证状态：** BM25/RRF 机制已测试；演示向量排名为 fixture。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

> **跨阶段回归检查：** 优化时必须复测 [q06/q09 与固定九题集](../course/regression-cases.md)，保留基线和无改善结果；fixture 向量排名不能充当真实质量改善证据。

## 1. 问题：现在为什么需要它？

向量可能漏掉准确的错误码，词法可能漏掉同义表达。我们先分别测，再用融合排名组合不同检索器，而不是直接相加不可比的分数。

## 2. 原理：在这个问题里理解技术

BM25 使用词频 tf、逆文档频率 IDF 和文档长度归一化：常见词区分力低，重复词收益饱和，长文不应仅靠词多获得优势。课程实现让公式可见；中文分词是独立选择，不用英语 split 代替。

RRF 对每个列表的名次 r 累加 1/(c+r)，避免不同评分量纲。融合前列表去重，融合后再 top-k。扩大候选池可能提高召回，同时增加重排和上下文成本。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/hybrid.py`

完整源文件：[打开源码](../../src/evidencedesk/hybrid.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/hybrid.py -->
```python
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
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–4 | 教学版 BM25：先让公式可见，后续数据变大再换成熟索引实现。 |
| 5–14 | 查询分词由调用者负责；这里接收 token 列表，不把英语 split 冒充中文分词。 |
| 15–30 | df 是含词文档数；IDF 让稀有词更有区分力，不等于词越少越正确。 |
| 31–40 | RRF 用排名融合而非相加不同量纲的原始分数；同一列表内去重防刷分。 |
| 41–43 | 父子检索取回父级上下文并保留首次出现顺序；父文档仍需重新检查访问权限。 |

### `examples/hybrid_rankings.py`

完整源文件：[打开源码](../../examples/hybrid_rankings.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/hybrid_rankings.py -->
```python
#: 这是排名机制实验，不是假装已跑完真实向量对照。
from evidencedesk.hybrid import bm25, rrf, expand_parents

#: 显式 token 列表保留词频，和阶段 1 的去重词集合形成对比。
def main():
    corpus = {"retry": ["webhook", "重试", "重试"], "keys": ["密钥", "轮换"], "ticket": ["故障", "工单"]}
    lexical = [doc_id for doc_id, score in bm25(["webhook", "重试"], corpus)]
    vector_fixture = ["keys", "retry"]
    print({"bm25": lexical, "fixture_vector": vector_fixture, "rrf": rrf([lexical, vector_fixture])})
    print(expand_parents(["child-a", "child-b"], {"child-a": "parent-1", "child-b": "parent-1"}))

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–3 | 这是排名机制实验，不是假装已跑完真实向量对照。 |
| 4–13 | 显式 token 列表保留词频，和阶段 1 的去重词集合形成对比。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.hybrid_rankings
python -m pytest tests/test_core.py -q
```

### 只做这些关键改动

1. 打开 hybrid_rankings.py，把 retry 的“重试”重复 10 次。
2. 先在 main 中加入 `print(bm25(["webhook", "重试"], corpus))`，改重复次数前后分别运行，对比分数变化，解释它与阶段1集合分数的区别。
3. 将 vector_fixture 改成 ["retry","keys"]，运行观察 RRF。
4. 正式实验时将 fixture 替换为 3B 实际返回的 ID 排名，保持同题同语料；不要把 fixture 输出写成真实模型提升。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

手算一条文档在两个列表中都排第一时的 RRF=2/61。解释 c 改变排名差距敏感度，不代表概率；确认相同列表中重复 ID 不会多加分。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 你的真实失败是精确词漏召回还是语义漏召回？若增加融合后没有收益，为什么保留更简单方案也是合格工程决策？

**产出：** 可解释 BM25 与 RRF、真实/fixture 分离的实验记录。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://en.wikipedia.org/wiki/Okapi_BM25
- https://qdrant.tech/documentation/concepts/hybrid-queries/

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
