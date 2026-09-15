# 1E · 第一次可复现检索评测

[全部课程](../course/index.md) · [上一课](01d-cli-tests.md) · [下一课](02a-chunks-versions.md)

- **学习进度：** 进行中；单题 Recall@k 的数值与分母题已答对；排序指标、整组评测及无答案题处理尚未验收。
- **前置理解：** 1D：CLI 与测试可运行
- **验证状态：** 基线实测见验证报告；非生成式问答评测。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 先看一题的 Recall@k（概念题已完成，见 1E-Q1）

前一课主要检查程序是否遵守约定；本课用固定问题集检查它能否找回相关依据。下面只讨论已标注至少一份相关文档的问题，无答案题后面单独处理。

人工标注的相关文档 ID 用作评测对照，不是检索器自己的关键词分数，也不能作为输入告诉检索器去找哪份文档。下面为手工小例子，不是三份真实手册的运行结果。

```python
relevant_ids = {"doc-a", "doc-c"}
retrieved_ids = ["doc-b", "doc-c"]

matched_ids = relevant_ids & set(retrieved_ids)
recall_at_2 = len(matched_ids) / len(relevant_ids)

print(recall_at_2)
```

输出 `0.5`：本应找回的两份相关文档中，前两项只找回了 `doc-c`。

- `relevant_ids`：经过内容核对、人工标注的相关文档集合。
- `retrieved_ids`：检索器实际返回的前两项 ID，保留顺序供后续排名指标使用。
- 转成集合求交集，计算找回多少份不同的相关文档。
- 分母是该问题相关文档总数，不是返回文档数，也不是查询关键词数。

本项目逐题 Recall@k = 前 k 项中找回的相关文档数 / 该题全部相关文档数，再对可回答题宏平均。第一步先理解单题，暂不一次引入 MRR、空返回率与整份评测脚本。

概念检查已完成：相关集合不变，取前 3 项得到 `["doc-a", "doc-b", "doc-c"]`。学习者正确回答 Recall@3 为 1、分母为 2，见 1E-Q1。

## 当前起步：相关结果排得够靠前吗？（待完成）

Recall@k 检查前 k 项找回了多少份相关文档，但不区分这些文档在前 k 项内部的顺序。再用 RR（倒数排名）观察第一份相关文档的位置：找到时 RR=1/位置，前 k 项没有相关文档时 RR=0。位置从 1 开始，而不是 Python 的下标 0。

MRR 是多题 RR 的平均。本项目仅在人工标注为可回答的题中计算该指标；这些题即使未召回，也以 RR=0 参与平均。无答案题的处理下一步单独讲。

以下是手工示例，不是仓库基线结果：固定 k=3，三道题的知识库中都有相关文档。

| 题目 | 返回的前 3 项中，第一份相关文档的位置 | RR |
|---|---|---|
| A | 第 1 位 | 1 |
| B | 第 2 位 | 0.5 |
| C | 未找到 | 0 |

已知这三个位置后，完整的计算示例为：

```python
first_relevant_ranks = [1, 2, None]

reciprocal_ranks = []
for rank in first_relevant_ranks:
    if rank is None:
        reciprocal_ranks.append(0)
    else:
        reciprocal_ranks.append(1 / rank)

mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
print(mrr)
```

输出 `0.5`，即 `(1 + 0.5 + 0) / 3`。

- `None` 在本例表示前 k 项没有相关文档，不是说该题的知识库本来就没有依据。
- 空列表逐次追加每题的 RR：未找回记 0，找到则用排名的倒数。
- `sum` 求和，`len` 给出参与平均的题数。
- 实际评测器会通过人工标注的相关 ID 与返回 ID 比较确定排名；这里先给出排名，专注理解指标。

概念检查（待回答）：能否删掉未召回的 C 题，只对找到相关文档的 A、B 两题求平均？为什么？这里只提出问题，不将学习者尚未回答的理由归档为标准答案。

## 1. 问题：现在为什么需要它？

“感觉搜得不错”不能指导下一次改动。我们要保留固定题集、逐题输出和可解释指标，避免只挑成功演示。

## 2. 原理：在这个问题里理解技术

可回答题 Recall@k=|检索ID∩相关ID|/|相关ID|，先逐题计算再宏平均。MRR 看第一个相关结果的倒数排名。无答案题没有 Recall 分母，应另算空返回率；无对应类型题目时返回 null，而不是伪造零分。

8 条是公开开发题，不是留出测试集。q06 的标签假设上下文已明确讨论 Webhook，单独一句“消息”其实有歧义。reference_facts 只供人工核对，输入检索器会形成答案泄漏。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/evaluate.py`

完整源文件：[打开源码](../../src/evidencedesk/evaluate.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/evaluate.py -->
```python
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
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–8 | mean 做宏平均；评测依赖检索，但不能把金标准输入给检索器。 |
| 9–20 | 即使评测集为空也要校验 k；None 在 JSON 中会变成 null，表示无定义。 |
| 21–30 | 检索只接收 question；reference_facts 不参与检索，防止答案泄漏。 |
| 31–38 | 保存逐题结果比只看均值更容易定位失败。 |
| 39–50 | JSONL 每行一个对象；从根目录运行，切换 k 时保留相同数据与代码版本。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m evidencedesk.evaluate --k 1
python -m evidencedesk.evaluate --k 3
python -m pytest tests/test_core.py -q
```

### 只做这些关键改动

1. 运行 k=1 与 k=3，找出 q06 的 retrieved。
2. 手算六条可回答题平均：5/6；与程序结果对比。
3. 先运行 `python -m examples.portfolio_snapshot` 创建 artifacts 目录。在编辑器将原题集另存为 `artifacts/questions-extra.jsonl`，末尾另起一行追加：`{"id":"q09","question":"Webhook 年付折扣是多少？","answerable":false,"relevant_document_ids":[],"reference_facts":[],"category":"unanswerable"}`。不要覆盖原数据。
4. 运行 `python -m evidencedesk.evaluate --questions artifacts/questions-extra.jsonl --k 1`；预测无答案空返回率从 1 变为 2/3，然后验证。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

预期原题集 Recall 与 MRR 都为约 0.8333，无答案空返回率为 1。解释这不代表真实拒答能力 100%，也不代表你已经掌握了 RAG。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 下一阶段为什么先解决长文分块与版本，而不是同时更换语料、模型、提示和指标？

**产出：** 逐题基线结果、一个带关键词的无答案反例、阶段 1 复盘。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://en.wikipedia.org/wiki/Mean_reciprocal_rank
- https://github.com/SIGILIPELLI/rag-mastery-path

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。


## 已完成问答与标准答案

只记录已完成的回答；单题通过不代表整个 1E 或阶段 1 已完成。

### 1E-Q1：找回全部相关文档时，Recall@3 是多少？

记录日期：2026-09-15。

**题目：** 相关文档集合为 `{"doc-a", "doc-c"}`，检索器返回的前 3 项为 `["doc-a", "doc-b", "doc-c"]`。Recall@3 是多少？分母是什么？

**学习者回答：** “应该为1，分母等于2。”

**判断：** 正确。

**标准答案：** 交集为 `{"doc-a", "doc-c"}`，找回 2 份相关文档；全部相关文档也有 2 份。因此 Recall@3 = 2/2 = 1.0，分母是 2，而不是返回数量 3。

**标准解析：** Recall@k 衡量已找回的相关文档占该题全部相关文档的比例。额外返回的无关文档 `doc-b` 不改变这个分母。本题的 @3 表示查看前 3 项，并不是规定要除以 3。

**复习要点：**

- 相关性由对照文档内容的评测标注决定，不是由检索器自己的关键词分数自动决定。
- 这是文档级召回率，不是查询词覆盖分数，也不是生成答案正确率。
- Recall@k 本身不会因前 k 项中混入无关文档直接扣分，也不区分相关结果在前 k 项内部的顺序；需要其他指标补充。

**记录范围：** 已完成数值与分母的概念题，未要求学习者运行完整评测脚本，不记录为已获得真实基线结果。
