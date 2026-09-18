# 8B · 对照报告、演示与求职表达

> **1A细度源码精讲（2026-09-19补充）：** [examples/portfolio_snapshot.py](../code/examples--portfolio_snapshot_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](08a-deploy-ci.md) · [下一课](09a-deepagents.md)

- **前置理解：** 8A；所有拟声明的结果都有实测来源
- **验证状态：** 报告生成脚本已运行；不含虚构性能提升或未做的生产部署。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

作品集不是“用过多少框架”的清单。招聘者需要理解你解决了什么问题、如何验证、有哪些限制，以及哪部分真正由你理解和修改。

## 2. 原理：在这个问题里理解技术

对照报告必须记录语料与题集版本、模型版本、参数、代码提交、重复次数、指标与失败。只有基线时就报告基线，不填编造的提升数字。公开开发题成绩不能当留出集泛化。

演示顺序建议：正常引用→无答案→权限隔离→审批拒绝→幂等重试→失败案例。区分离线组件、在线实验与已集成 Web 产品，明确哪些是导师提供参考代码、哪些改动与实验由你完成。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `examples/portfolio_snapshot.py`

完整源文件：[打开源码](../../examples/portfolio_snapshot.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/portfolio_snapshot.py -->
```python
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
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–7 | 从当前代码和数据生成真实基线报告；不手填改善百分比或模型效果。 |
| 8–25 | 哈希含文件名及内容，用于识别语料变动；不是将 hash 当隐私保护。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.portfolio_snapshot
python -m pytest -q
```

### 只做这些关键改动

1. 打开生成的 artifacts/baseline-report.json，找到数据哈希、题数和限制。
2. 按 `docs/experiments/portfolio-template.md` 填写，不把在线实验待验写成已部署。
3. 用自己的话讲清一个失败：q06 在词法基线漏检，以及它的隐含上下文。
4. 录制 3–5 分钟演示；若某组件未集成，单独展示组件测试并明确说明。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

每一句简历效果声明都能追到实际命令、数据版本和结果；能回答“为什么不选择更复杂方案”。当指标下降时也能解释而不隐藏。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 现在你能独立解释项目的哪些关键决策？还需什么证据才能把“课程参考实验”升级为“完整可部署作品”？

**产出：** 基线报告、架构/限制说明、演示脚本和不夸大的简历草稿。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://github.com/dan2mcdr/AI-Engineer-Journey
- https://github.com/Semicolon101/Ai-Engineering-Roadmap

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
