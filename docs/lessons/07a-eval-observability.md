# 7A · 回归评测、Ragas 与 LangSmith

[全部课程](../course/index.md) · [上一课](06b-authorized-tools.md) · [下一课](07b-memory.md)

- **前置理解：** 阶段 6；已有检索基线和实际候选答案
- **验证状态：** 离线遥测已运行；Ragas/托管 LangSmith 参考示例未发起在线调用。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

升级提示或检索策略后，既要知道质量是否退化，也要定位慢在哪一步，同时不能把日志变成泄露原文和密钥的副本。

## 2. 原理：在这个问题里理解技术

将确定性测试、检索指标、人工答案审核和 LLM 裁判分开。Faithfulness 关注回答断言能否由上下文支持，不等于回答完整、正确引用或安全；裁判也有偏差，需固定版本、重复抽样并与人工标注校准。

追踪记录阶段耗时、候选数量、模型调用和错误类别，而不是默认采集整个 prompt。允许列表比随意正则脱敏更保守。开发/验证/测试分离，回归阈值应结合样本量与错误代价，不承诺一个神奇百分比。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `examples/trace_allowlist.py`

完整源文件：[打开源码](../../examples/trace_allowlist.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/trace_allowlist.py -->
```python
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
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–7 | 与其靠正则猜所有敏感信息，不如默认不采集原始请求、原文和凭据。 |
| 8–19 | perf_counter 衡量持续时间，不受系统时钟回拨影响；这里不测模型延迟。 |

### `examples/judge_answer.py`

完整源文件：[打开源码](../../examples/judge_answer.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/judge_answer.py -->
```python
#: 在线可选：Ragas 的 LLM 裁判也会收费，且评分有随机性与模型偏差。
import asyncio
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness
from evidencedesk.documents import load_documents

#: 从真实候选答案构造单条评测，不能把人工标准答案伪装为系统输出。
async def main():
    os.environ["OPENAI_API_KEY"]
    candidate = os.environ["CANDIDATE_ANSWER"]
    doc = next(doc for doc in load_documents(Path("data/sample")) if doc.id == "webhook-delivery")
    sample = SingleTurnSample(user_input="Webhook 重试多少次？", response=candidate, retrieved_contexts=[doc.text])
    #: 此接口属于 Ragas 0.3 系列；升级应先核对迁移说明，不能只更新版本号。
    judge = LangchainLLMWrapper(ChatOpenAI(model=os.environ["JUDGE_MODEL"], temperature=0, timeout=30, max_retries=1))
    metric = Faithfulness(llm=judge)
    score = await metric.single_turn_ascore(sample)
    print({"metric": "faithfulness", "score": score, "human_review_required": True})

if __name__ == "__main__":
    asyncio.run(main())
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–10 | 在线可选：Ragas 的 LLM 裁判也会收费，且评分有随机性与模型偏差。 |
| 11–16 | 从真实候选答案构造单条评测，不能把人工标准答案伪装为系统输出。 |
| 17–24 | 此接口属于 Ragas 0.3 系列；升级应先核对迁移说明，不能只更新版本号。 |

### `examples/langsmith_metrics.py`

完整源文件：[打开源码](../../examples/langsmith_metrics.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/langsmith_metrics.py -->
```python
#: 显式上传有限字段，默认不启用自动追踪，不上传原始问题或证据。
import os
from uuid import uuid4
from langsmith import Client

#: 必须先设置账号、项目和密钥；这里只演示遥测写入，不能当真实业务指标。
def main():
    os.environ["LANGSMITH_API_KEY"]
    project = os.environ["LANGSMITH_PROJECT"]
    client = Client()
    run_id = uuid4()
    client.create_run(name="course-synthetic-metric", run_type="chain", id=run_id,
                      inputs={"fixture": True}, project_name=project)
    client.update_run(run_id, outputs={"candidate_count": 1, "model_calls": 0, "synthetic": True})
    print("已上传明确标注 synthetic 的课程遥测；请在项目中检查并按保留策略删除。")

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–5 | 显式上传有限字段，默认不启用自动追踪，不上传原始问题或证据。 |
| 6–18 | 必须先设置账号、项目和密钥；这里只演示遥测写入，不能当真实业务指标。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.trace_allowlist
python -m evidencedesk.evaluate --k 1
# 在线可选，另建隔离环境核对依赖：pip install "ragas>=0.3,<0.4" "langchain-openai>=1,<2"
# 配置候选答案、模型与密钥后：python -m examples.judge_answer
# 配置 LangSmith 项目与密钥后：python -m examples.langsmith_metrics
```

### 只做这些关键改动

1. 先运行离线 trace，确认没有原始问题、正文或 authorization 字段。
2. 若执行 Ragas，将 3B 实际生成答案放入 CANDIDATE_ANSWER；不要把参考答案当系统输出。同时设置 JUDGE_MODEL。
3. 对一个正确答案与一个故意写成“重试30次”的答案分别人工审查，再比较裁判分数；观察分歧，不预填结果。
4. LangSmith 示例只上传 synthetic 指标；查看项目并按保留策略删除，未授权前不启用全链自动追踪。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

最终至少列出检索召回、答案支持、拒答、权限四类不同信号；解释高 Faithfulness 为什么不保证答案有用。Ragas 示例针对 0.3 系列，升级前需检查 API 与兼容性。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果裁判同意了错误答案，你是改金标准迎合裁判，还是记录失败并校准？为什么将原文交给评估模型也属于数据外发？

**产出：** 回归表、隐私允许列表、人工/裁判分歧记录与费用观察。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。

### Pandas 与 TruLens 的引入条件

问题数增加后，用 `pd.DataFrame(result["details"])` 将逐题结果转成表，再按错误类别 groupby 分析；小数据时标准库足够。TruLens 可作为反馈/诊断方案对照，不与 LangSmith 同时复制一套追踪链。无论选谁，都先确认上传字段、保存期限与删除能力。

## 卡住时按需查阅

- https://docs.ragas.io/
- https://docs.langchain.com/langsmith/observability
- https://www.trulens.org/

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
