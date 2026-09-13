# 6A · LangGraph 的暂停、恢复与审批

[全部课程](../course/index.md) · [上一课](05c-postgres-cache.md) · [下一课](06b-authorized-tools.md)

- **前置理解：** 阶段 5；理解服务端身份与副作用
- **验证状态：** 真实 LangGraph 无模型流程已测；checkpoint 只在内存。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

用户让助手“帮我建个工单”时，必须先看草稿再确认。把所有步骤塞进一段提示不能保证暂停、恢复或拒绝路径。

## 2. 原理：在这个问题里理解技术

图状态存储草稿、审批和状态；节点返回局部更新，边定义固定顺序。interrupt 暂停并把可序列化载荷返回调用者，Command(resume=...) 送回人工决定。恢复会重跑暂停节点开始部分，所以之前的副作用可能再次发生。

checkpointer 与 thread_id 共同决定恢复位置。内存 Saver 只适合原理课，进程重启会丢；生产持久化需数据库 checkpointer 与用户/thread 的授权映射。thread_id 猜不出来不是访问控制。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `examples/approval_graph.py`

完整源文件：[打开源码](../../examples/approval_graph.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/approval_graph.py -->
```python
#: 使用真实 LangGraph，无模型调用；内存 checkpoint 不支持进程重启恢复。
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

#: 类型定义告诉读者状态字段；它本身不执行权限校验。
class State(TypedDict):
    draft: str
    approved: bool
    status: str

#: interrupt 抛出暂停信号，恢复时当前节点从头重跑；前面不能随便放副作用。
def review(state: State):
    decision = interrupt({"draft": state["draft"], "question": "是否批准该草稿？"})
    return {"approved": decision is True}

#: 只计算状态，不写工单；审批通过和拥有写权限是两个不同条件。
def route(state: State):
    return {"status": "ready_for_authorized_tool" if state["approved"] else "rejected"}

#: 图明确固定执行顺序；这类流程不需要模型自主选择下一步。
def build_graph():
    graph = StateGraph(State)
    graph.add_node("review", review)
    graph.add_node("route", route)
    graph.add_edge(START, "review")
    graph.add_edge("review", "route")
    graph.add_edge("route", END)
    return graph.compile(checkpointer=InMemorySaver())

#: thread_id 必须由可信服务映射到当前用户；仅拼接身份字符串不构成鉴权。
def main():
    graph = build_graph()
    config = {"configurable": {"thread_id": "alpha:alice:demo-1"}}
    paused = graph.invoke({"draft": "Webhook 投递失败排查", "approved": False, "status": "draft"}, config)
    assert "__interrupt__" in paused
    print("已暂停，未执行任何工单写操作")
    resumed = graph.invoke(Command(resume=True), config)
    print(resumed["status"])

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–6 | 使用真实 LangGraph，无模型调用；内存 checkpoint 不支持进程重启恢复。 |
| 7–12 | 类型定义告诉读者状态字段；它本身不执行权限校验。 |
| 13–17 | interrupt 抛出暂停信号，恢复时当前节点从头重跑；前面不能随便放副作用。 |
| 18–21 | 只计算状态，不写工单；审批通过和拥有写权限是两个不同条件。 |
| 22–31 | 图明确固定执行顺序；这类流程不需要模型自主选择下一步。 |
| 32–43 | thread_id 必须由可信服务映射到当前用户；仅拼接身份字符串不构成鉴权。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pip install -e ".[workflow]"
python -m examples.approval_graph
python -m pytest tests/test_integrations.py -q
```

### 只做这些关键改动

1. 先运行默认流程，看到暂停后 ready_for_authorized_tool，注意没有创建工单。
2. 将 main 中 Command(resume=True) 改为 False，预期 rejected。
3. 再改成字符串 "true"，仍应 rejected，避免宽松真假值。
4. 恢复原示例，解释为什么批准节点之前不能直接调用外部写工具。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

通过 approve/reject/字符串三条路径；能解释为什么重新运行脚本不会恢复上次内存状态。生产恢复还要验证请求者是否拥有该线程和审批权限。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 固定审批流程为什么比自主 Agent 更容易验证？哪些真实任务才需要模型选择下一步？

**产出：** 可暂停恢复的工作流、拒绝测试、持久化迁移需求。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.langchain.com/oss/python/langgraph/interrupts
- https://docs.langchain.com/oss/python/langgraph/persistence

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
