# 3A · 向量、余弦相似度与 Qdrant

[全部课程](../course/index.md) · [上一课](02b-pdf-tokens.md) · [下一课](03b-live-rag.md)

- **前置理解：** 阶段 2；掌握块身份与来源
- **验证状态：** 真实 Qdrant 本地模式已测；向量为手写几何样例，不是语义模型效果。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

关键词不能处理换说法。引入嵌入前，先理解向量数据库究竟比较什么，以及如何在检索时排除不该访问的内容。

## 2. 原理：在这个问题里理解技术

向量是数值列表。余弦相似度=点积/(两向量范数乘积)，主要比较方向。真实 embedding 用训练得到的映射把文本放到高维空间；本课手写二维点只是解释计算，不能证明系统理解中文。

collection 约定维数与距离；payload 存来源和权限。索引与查询不仅要维数一致，还要模型、版本、归一化和查询前缀约定一致。元数据过滤先约束可见候选，不能交给生成模型做授权。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `examples/vector_geometry.py`

完整源文件：[打开源码](../../examples/vector_geometry.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/vector_geometry.py -->
```python
#: 使用真实 Qdrant 本地内存模式，但向量是手写的，仅解释几何和过滤。
from qdrant_client import QdrantClient, models

#: collection 规定维数与距离函数，查询向量必须同维，真实模型还必须同版本。
def main():
    client = QdrantClient(":memory:")
    client.create_collection("geometry", vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE))
    client.upsert("geometry", points=[
        models.PointStruct(id=1, vector=[1.0, 0.0], payload={"topic": "重试", "tenant": "alpha"}),
        models.PointStruct(id=2, vector=[0.0, 1.0], payload={"topic": "密钥", "tenant": "alpha"}),
        models.PointStruct(id=3, vector=[0.9, 0.1], payload={"topic": "私有", "tenant": "beta"}),
    ])
    #: 过滤发生在检索候选阶段；第三点再相似，也不能跨租户进入结果。
    scope = models.Filter(must=[models.FieldCondition(key="tenant", match=models.MatchValue(value="alpha"))])
    points = client.query_points("geometry", query=[0.9, 0.1], query_filter=scope, limit=2).points
    print([(point.id, round(point.score, 4)) for point in points])
    assert points[0].id == 1 and all(point.payload["tenant"] == "alpha" for point in points)
    client.close()

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–3 | 使用真实 Qdrant 本地内存模式，但向量是手写的，仅解释几何和过滤。 |
| 4–12 | collection 规定维数与距离函数，查询向量必须同维，真实模型还必须同版本。 |
| 13–21 | 过滤发生在检索候选阶段；第三点再相似，也不能跨租户进入结果。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pip install -e ".[vector]"
python -m examples.vector_geometry
python -m pytest tests/test_integrations.py -q
```

### 只做这些关键改动

1. 手算查询 [0.9,0.1] 与点1、点2的余弦关系，预测谁更近。
2. 运行，预期点1在前，点3虽完全相同却被 alpha 过滤排除。
3. 临时将 query 改为 [0.1,0.9]，同步把示例断言预期改成点2；运行验证。
4. 恢复原示例；解释过滤不能由浏览器随意提供的 tenant 决定。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

原始输出约为 [(1,0.9939),(2,0.1104)]。说明向量维数匹配为什么不等于模型匹配；相似度不是答案可信度。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** FAISS、Chroma、Qdrant、Pinecone 分别作为本地索引、易用原型、带过滤服务和托管选择时，你会比较哪些需求？不要求同时安装。

**产出：** 向量几何实验、过滤用例、嵌入模型选择记录草稿。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。

### 模型选择，不按品牌凑数量

HuggingFace 是生态，BGE 是模型系列，sentence-transformers 是加载/推理库，OpenAI 是托管服务。中文任务应先用少量已标注的换说法题对比；本地模型还需考虑下载授权、内存和版本 revision。选择一个方案并记录维数、版本、费用和隐私理由，再进入 3B。

## 卡住时按需查阅

- https://qdrant.tech/documentation/quickstart/
- https://www.sbert.net/docs/sentence_transformer/usage/usage.html

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
