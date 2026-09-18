# 4B · 重排序、多查询、父子检索与消融

> **1A细度源码精讲（2026-09-19补充）：** [examples/live_variants.py](../code/examples--live_variants_py.md) · [examples/retrieval_variants.py](../code/examples--retrieval_variants_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](04a-hybrid.md) · [下一课](05a-api-security.md)

- **前置理解：** 4A；已有固定基线
- **验证状态：** 管道连接机制已提供；重排分数与改写排名是明确 fixture，尚未验证真实质量。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

> **跨阶段回归检查：** 将 [q06/q09 回归跟踪](../course/regression-cases.md) 纳入真实消融对照。一次改一种策略，查询改写不得悄悄增加原题没有的上下文或答案。

## 1. 问题：现在为什么需要它？

候选有正确文档却排太后，需要重排；原问题表达太窄，需要多查询；命中碎片缺少条件，需要取父文档。三者解决的是不同问题，不应一次全开。

## 2. 原理：在这个问题里理解技术

双编码器分别表示 query/document，利于预索引；cross-encoder 联合看一对文本，通常更贵，因此仅对召回候选打分。MultiQuery 生成若干保留原意的查询，去重融合候选；改写也可能引入假设。父子检索用小块定位，再取父级上下文，必须重新检查父级权限与总 token 预算。

一次只改一个变量，记录 Recall@k、MRR、人工证据支持率、延迟和实际费用。公开开发集调参，冻结的留出集只用于最终比较。不能因为均值提高就忽略权限或拒答回归。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `examples/retrieval_variants.py`

完整源文件：[打开源码](../../examples/retrieval_variants.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/retrieval_variants.py -->
```python
#: MultiQuery 与 rerank 先用受控 fixture 演示数据流，真实质量需要模型和实验验证。
from evidencedesk.hybrid import rrf, expand_parents

#: 两条查询的候选排名来自固定样例，不宣称是模型自动改写的结果。
def main():
    original_ranking = ["retry-child", "keys-child"]
    rewritten_ranking = ["retry-child", "ticket-child"]
    fused = [doc_id for doc_id, score in rrf([original_ranking, rewritten_ranking])]
    #: Cross-encoder 对 (query, passage) 打分；这里用预置分数替身验证排序连接方式。
    fixture_pair_scores = {"retry-child": 0.8, "keys-child": 0.1, "ticket-child": 0.3}
    reranked = sorted(fused, key=lambda item: (-fixture_pair_scores[item], item))[:2]
    parents = expand_parents(reranked, {"retry-child": "webhook-delivery", "keys-child": "api-key-policy", "ticket-child": "incident-escalation"})
    print({"fused": fused, "fixture_reranked": reranked, "parents": parents})

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–3 | MultiQuery 与 rerank 先用受控 fixture 演示数据流，真实质量需要模型和实验验证。 |
| 4–8 | 两条查询的候选排名来自固定样例，不宣称是模型自动改写的结果。 |
| 9–16 | Cross-encoder 对 (query, passage) 打分；这里用预置分数替身验证排序连接方式。 |

### `examples/live_variants.py`

完整源文件：[打开源码](../../examples/live_variants.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/live_variants.py -->
```python
#: 4B 的真实模型对照扩展：需要下载本地模型、配置在线查询改写模型；未默认运行。
import os
from pathlib import Path
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_openai import ChatOpenAI
from evidencedesk.documents import load_documents
from evidencedesk.hybrid import rrf

#: 改写数量受限，包含原查询作保底；结构化格式不保证改写保持原意。
class Queries(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=2)

#: 显式模型名和 revision 使模型选择可追溯；下载前检查许可证、内存与网络费用。
def main():
    question = os.environ.get("QUESTION", "Webhook 失败后还会再发吗？")
    docs = load_documents(Path("data/sample"))
    embedding = SentenceTransformer(os.environ["LOCAL_EMBEDDING_MODEL"], revision=os.environ["LOCAL_EMBEDDING_REVISION"])
    reranker = CrossEncoder(os.environ["RERANK_MODEL"], revision=os.environ["RERANK_REVISION"])
    vectors = embedding.encode([doc.title + "\n" + doc.text for doc in docs], normalize_embeddings=True)
    model = ChatOpenAI(model=os.environ["CHAT_MODEL"], temperature=0, max_tokens=200, timeout=30, max_retries=1)
    rewrites = model.with_structured_output(Queries).invoke([
        ("system", "给出至多两条保留原意的检索问题，不增加原问题未提供的事实。"), ("human", question)])
    queries = list(dict.fromkeys([question] + rewrites.queries))
    #: 归一化向量点积等于余弦；前缀按具体模型卡配置，不能任意换。
    rankings = []
    for query in queries:
        vector = embedding.encode(os.environ.get("QUERY_PREFIX", "") + query, normalize_embeddings=True)
        scores = vectors @ vector
        ranking = sorted(range(len(docs)), key=lambda i: (-float(scores[i]), docs[i].id))[:3]
        rankings.append([docs[i].id for i in ranking])
    fused = [doc_id for doc_id, score in rrf(rankings)]
    by_id = {doc.id: doc for doc in docs}
    #: 先召回候选，再联合编码原始问题与每份候选正文；模型应输出每对单一相关性分数。
    scores = reranker.predict([(question, by_id[doc_id].text) for doc_id in fused])
    reranked = sorted(zip(fused, map(float, scores)), key=lambda item: (-item[1], item[0]))
    print({"queries_for_human_review": queries, "vector_rankings": rankings, "rrf": fused, "reranked": reranked})

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–9 | 4B 的真实模型对照扩展：需要下载本地模型、配置在线查询改写模型；未默认运行。 |
| 10–13 | 改写数量受限，包含原查询作保底；结构化格式不保证改写保持原意。 |
| 14–24 | 显式模型名和 revision 使模型选择可追溯；下载前检查许可证、内存与网络费用。 |
| 25–33 | 归一化向量点积等于余弦；前缀按具体模型卡配置，不能任意换。 |
| 34–40 | 先召回候选，再联合编码原始问题与每份候选正文；模型应输出每对单一相关性分数。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.retrieval_variants
# 在线/模型下载可选：在独立环境安装 sentence-transformers 与 llm extra 后，按正文配置模型和 revision
# python -m examples.live_variants
```

### 只做这些关键改动

1. 运行 fixture，手工追踪 retry-child 怎样进入父文档。
2. 将 fixture_pair_scores 中 keys-child 改为 0.9，观察错误高分如何把无关候选推前。
3. 真实实验可运行本课第二份完整脚本 live_variants.py：另装 sentence-transformers，配置 LOCAL_EMBEDDING_MODEL、LOCAL_EMBEDDING_REVISION、RERANK_MODEL、RERANK_REVISION、CHAT_MODEL 和密钥；QUERY_PREFIX 按嵌入模型卡设置。选择输出单一相关性分数、支持任务语言的 reranker；模型会下载，先确认资源。本脚本尚未实跑。
4. 使用 `docs/experiments/ablation-template.md`，只填实际跑过的行，没跑标“未运行”。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

说明为什么 rerank 无法找回完全未召回的文档；解释父级放大可能降低精度并扩大越权风险。模型分数不是事实概率。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果多查询花费翻倍而 Recall 不变，应保留它吗？描述一个你会关闭策略的明确条件。

**产出：** 策略适用条件表、单因素实验记录、保留或舍弃的理由。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://www.sbert.net/docs/cross_encoder/usage/usage.html
- https://github.com/SIGILIPELLI/rag-mastery-path

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
