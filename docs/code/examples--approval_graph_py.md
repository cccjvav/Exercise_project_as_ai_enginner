# 可暂停和恢复的审批图：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/approval_graph.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用真实工作流引擎展示等待人工决定，而不让模型自主执行写入。

### 输入、输出与调用关系

State字典经过review暂停、恢复后route给出状态；不创建工单。

### 运行与风险边界

安装workflow依赖后 `python -m examples.approval_graph`，没有模型调用。

内存checkpointer不跨进程持久化；thread_id字符串不是认证机制。恢复前节点代码会重跑，副作用需幂等或放在正确边界。

## 完整源码

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

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 使用真实 LangGraph，无模型调用；内存 checkpoint 不支持进程重启恢复。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：使用真实 LangGraph，无模型调用；内存 checkpoint 不支持进程重启恢复。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
from typing import TypedDict
```

**语法与数据变化：** 从 `typing` 导入 `TypedDict`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 类型提示工具。TypedDict描述字典字段给阅读者与静态工具，不会像Pydantic那样自动执行运行时权限或类型验证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
from langgraph.graph import StateGraph, START, END
```

**语法与数据变化：** 从 `langgraph.graph` 导入 `StateGraph, START, END`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 图式工作流组件，用节点、边描述状态流转；能运行图不等于有持久化存储或真实人工审批。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
from langgraph.checkpoint.memory import InMemorySaver
```

**语法与数据变化：** 从 `langgraph.checkpoint.memory` 导入 `InMemorySaver`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 内存检查点，仅在当前进程保留状态；进程退出会丢失，不能宣称生产持久化。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from langgraph.types import interrupt, Command
```

**语法与数据变化：** 从 `langgraph.types` 导入 `interrupt, Command`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 中断与恢复命令类型。恢复必须针对正确 thread_id，且要先核验操作者身份。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

```python
#: 类型定义告诉读者状态字段；它本身不执行权限校验。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：类型定义告诉读者状态字段；它本身不执行权限校验。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L8"></a>
### 第 8 行

```python
class State(TypedDict):
```

**语法与数据变化：** TypedDict描述状态是具有这些键的字典。

**为什么与边界：** 不是运行时校验器或权限模型；不能用它信任客户端状态。

<a id="L9"></a>
### 第 9 行

```python
    draft: str
```

**语法与数据变化：** draft保存待审核草稿字符串。

**为什么与边界：** 审批应绑定具体版本，不能批准后任意换内容再写入。

<a id="L10"></a>
### 第 10 行

```python
    approved: bool
```

**语法与数据变化：** approved为批准标志，初始示例False。

**为什么与边界：** 状态中的布尔值本身不能作为生产可信审批来源。

<a id="L11"></a>
### 第 11 行

```python
    status: str
```

**语法与数据变化：** status描述流程阶段。

**为什么与边界：** 它是业务标签，不是HTTP退出码或数据库事务状态。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
#: interrupt 抛出暂停信号，恢复时当前节点从头重跑；前面不能随便放副作用。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：interrupt 抛出暂停信号，恢复时当前节点从头重跑；前面不能随便放副作用。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L14"></a>
### 第 14 行

```python
def review(state: State):
```

**语法与数据变化：** review节点接收当前状态并返回局部更新。

**为什么与边界：** 节点恢复可能从头执行，因此interrupt前不能随意放一次性写操作。

<a id="L15"></a>
### 第 15 行

```python
    decision = interrupt({"draft": state["draft"], "question": "是否批准该草稿？"})
```

**语法与数据变化：** interrupt把草稿与问题交给外部，第一次暂停；恢复时返回人工决定并赋给decision。

**为什么与边界：** 不是普通input阻塞读终端；LangGraph检查点负责保存暂停上下文。

<a id="L16"></a>
### 第 16 行

```python
    return {"approved": decision is True}
```

**语法与数据变化：** 只接受精确True作为批准，返回approved字段更新。

**为什么与边界：** 非空字符串或数字1不应被当作明确同意；返回局部字典并非手动复制全部状态。

<a id="L17"></a>
### 第 17 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L18"></a>
### 第 18 行

```python
#: 只计算状态，不写工单；审批通过和拥有写权限是两个不同条件。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：只计算状态，不写工单；审批通过和拥有写权限是两个不同条件。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L19"></a>
### 第 19 行

```python
def route(state: State):
```

**语法与数据变化：** route接收含审批结果的状态。

**为什么与边界：** 这里只选择状态标签，不调用外部工具。

<a id="L20"></a>
### 第 20 行

```python
    return {"status": "ready_for_authorized_tool" if state["approved"] else "rejected"}
```

**语法与数据变化：** 三元表达式按approved决定ready或rejected。

**为什么与边界：** ready表示可进入受权工具的下一步，不等于已经通过工具的身份/审批/幂等检查。

<a id="L21"></a>
### 第 21 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L22"></a>
### 第 22 行

```python
#: 图明确固定执行顺序；这类流程不需要模型自主选择下一步。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：图明确固定执行顺序；这类流程不需要模型自主选择下一步。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L23"></a>
### 第 23 行

```python
def build_graph():
```

**语法与数据变化：** build_graph封装图的构造，每次调用返回新编译图。

**为什么与边界：** 新建内存存储与恢复已有运行不是同一件事，不能每次请求都重建后期望旧检查点还在。

<a id="L24"></a>
### 第 24 行

```python
    graph = StateGraph(State)
```

**语法与数据变化：** 用State声明图状态结构。

**为什么与边界：** 创建builder而非立即执行节点。

<a id="L25"></a>
### 第 25 行

```python
    graph.add_node("review", review)
```

**语法与数据变化：** 将review函数注册为名为review的节点。

**为什么与边界：** 传函数对象而不是调用review()，执行由图调度。

<a id="L26"></a>
### 第 26 行

```python
    graph.add_node("route", route)
```

**语法与数据变化：** 注册route节点，后续边通过字符串名称引用它。

**为什么与边界：** 名称与函数可以不同，但边必须指向已注册节点。

<a id="L27"></a>
### 第 27 行

```python
    graph.add_edge(START, "review")
```

**语法与数据变化：** 入口连接到review，先审核。

**为什么与边界：** 不能把route提前到审批之前。

<a id="L28"></a>
### 第 28 行

```python
    graph.add_edge("review", "route")
```

**语法与数据变化：** review完成后再进入route。

**为什么与边界：** 如果review暂停，这条边要等恢复后才继续，不自动跳过人工步骤。

<a id="L29"></a>
### 第 29 行

```python
    graph.add_edge("route", END)
```

**语法与数据变化：** route结束后到END，终止这条执行路径。

**为什么与边界：** 没有循环工具或自动创建工单步骤。

<a id="L30"></a>
### 第 30 行

```python
    return graph.compile(checkpointer=InMemorySaver())
```

**语法与数据变化：** 编译图并设置新的内存检查点保存器。

**为什么与边界：** 它使同进程可恢复，不保证重启恢复；生产需持久化后端及用户权限映射。

<a id="L31"></a>
### 第 31 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L32"></a>
### 第 32 行

```python
#: thread_id 必须由可信服务映射到当前用户；仅拼接身份字符串不构成鉴权。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：thread_id 必须由可信服务映射到当前用户；仅拼接身份字符串不构成鉴权。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L33"></a>
### 第 33 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L34"></a>
### 第 34 行

```python
    graph = build_graph()
```

**语法与数据变化：** 构造可执行图及本次内存状态容器。

**为什么与边界：** 不等于发起一次审批运行，首次invoke才开始。

<a id="L35"></a>
### 第 35 行

```python
    config = {"configurable": {"thread_id": "alpha:alice:demo-1"}}
```

**语法与数据变化：** 配置thread_id以关联本次运行。

**为什么与边界：** 拼接alpha:alice看起来有身份含义，却不是认证；服务端必须控制哪些用户能恢复这个ID。

<a id="L36"></a>
### 第 36 行

```python
    paused = graph.invoke({"draft": "Webhook 投递失败排查", "approved": False, "status": "draft"}, config)
```

**语法与数据变化：** 给初始草稿、False审批和draft状态，连同配置启动图。

**为什么与边界：** 会进入review暂停；初始approved=False不是永久拒绝，恢复决定可更新它。

<a id="L37"></a>
### 第 37 行

```python
    assert "__interrupt__" in paused
```

**语法与数据变化：** 断言结果包含暂停标志，证明没有一路跑到终点。

**为什么与边界：** 只打印“已暂停”而不检查返回值可能误报流程行为。

<a id="L38"></a>
### 第 38 行

```python
    print("已暂停，未执行任何工单写操作")
```

**语法与数据变化：** 说明当前未执行工单写操作。

**为什么与边界：** 因为本图根本没有写工具，不是所有带interrupt的图都天然无副作用。

<a id="L39"></a>
### 第 39 行

```python
    resumed = graph.invoke(Command(resume=True), config)
```

**语法与数据变化：** 用同配置发送恢复命令True。

**为什么与边界：** 必须复用对应thread_id和检查点，换ID会改变运行上下文；恢复请求仍需真实鉴权。

<a id="L40"></a>
### 第 40 行

```python
    print(resumed["status"])
```

**语法与数据变化：** 打印恢复后的status以观察分支。

**为什么与边界：** 打印ready不是写入完成回执，下一课的工具还要独立校验。

<a id="L41"></a>
### 第 41 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L42"></a>
### 第 42 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L43"></a>
### 第 43 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

首次invoke返回__interrupt__；同thread_id以Command(resume=True)恢复得到ready_for_authorized_tool。False应走rejected，但ready仍不代表拥有写权限。

## 只练一个关键点（不是新的学习验收记录）

1. 运行无模型示例，观察先暂停后ready的两次invoke。
2. 运行tests/test_integrations.py -k graph，比较True、False、字符串true。
3. **复盘：** ready状态、可信批准和实际写权限是同一件事吗？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
