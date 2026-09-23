# 6B · 工具调用、参数校验与幂等

> **1A细度源码精讲（2026-09-19补充）：** [examples/approved_ticket.py](../code/examples--approved_ticket_py.md) · [src/evidencedesk/tickets.py](../code/src--evidencedesk--tickets_py.md) · [tests/test_core.py](../code/tests--test_core_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](06a-langgraph.md) · [下一课](06c-integrate-ticket-flow.md)

- **前置理解：** 6A；理解审批不等于写权限
- **验证状态：** SQLite 模拟工单与重启幂等测试已通过；不连接真实工单系统。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

模型可能重复调用工具，网络可能超时重试，审批后草稿也可能被改。我们要保证未审批不写、内容改变重审、相同请求不重复创建。

## 2. 原理：在这个问题里理解技术

Function Calling 只让模型给出工具名和参数，不代表参数可信。执行层校验 schema、当前身份、允许操作与审批绑定。审批摘要绑定规范化 payload 的哈希；哈希不是签名，Approval 对象必须来自可信审批存储。

数据库唯一约束和事务实现幂等，不能只先查后插。外部 API 还存在“请求成功但本地没记下”的故障窗口，需 outbox、远端幂等键与对账。课程 SQLite 只模拟同数据库写路径。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/tickets.py`

完整源文件：[打开源码](../../src/evidencedesk/tickets.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/tickets.py -->
```python
#: SQLite 模拟工单写入；生产外部 API 还需 outbox、远端幂等键及重试策略。
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from uuid import uuid4

#: Approval 只能由可信服务从受保护审批记录构造，绝不能反序列化客户端自报批准。
@dataclass(frozen=True)
class Approval:
    tenant: str
    user: str
    payload_hash: str

#: 按键排序后再哈希，字段顺序不同不影响审批绑定，内容变了则必须重新审批。
def payload_hash(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

#: 身份与当前 payload 都匹配才允许进入写路径；拒绝不能晚于写操作。
def submit(conn: sqlite3.Connection, tenant: str, user: str, key: str,
           payload: dict, approval: Approval | None) -> str:
    digest = payload_hash(payload)
    if approval != Approval(tenant, user, digest):
        raise PermissionError("缺少与身份、当前草稿一致的可信审批")
    if set(payload) != {"title", "priority"} or not isinstance(payload["title"], str) or not 1 <= len(payload["title"].strip()) <= 120:
        raise ValueError("工单字段无效")
    if payload["priority"] not in ("P1", "P3") or not key:
        raise ValueError("优先级或幂等键无效")
    #: 参数占位符避免 SQL 拼接注入；唯一约束由数据库执行，事务内处理冲突。
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tickets (tenant TEXT, key TEXT, digest TEXT, id TEXT, PRIMARY KEY (tenant,key))")
        conn.execute("INSERT OR IGNORE INTO tickets VALUES (?,?,?,?)", (tenant, key, digest, str(uuid4())))
        row = conn.execute("SELECT digest,id FROM tickets WHERE tenant=? AND key=?", (tenant, key)).fetchone()
        if row[0] != digest:
            raise ValueError("同一个幂等键不能用于不同内容")
    return row[1]
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–7 | SQLite 模拟工单写入；生产外部 API 还需 outbox、远端幂等键及重试策略。 |
| 8–14 | Approval 只能由可信服务从受保护审批记录构造，绝不能反序列化客户端自报批准。 |
| 15–19 | 按键排序后再哈希，字段顺序不同不影响审批绑定，内容变了则必须重新审批。 |
| 20–29 | 身份与当前 payload 都匹配才允许进入写路径；拒绝不能晚于写操作。 |
| 30–37 | 参数占位符避免 SQL 拼接注入；唯一约束由数据库执行，事务内处理冲突。 |

### `examples/approved_ticket.py`

完整源文件：[打开源码](../../examples/approved_ticket.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/approved_ticket.py -->
```python
#: 内存 SQLite 不会创建真实工单或保存客户资料。
import sqlite3
from evidencedesk.tickets import Approval, payload_hash, submit

#: 先证明拒绝路径，再模拟人工批准；演示不是公网审批接口。
def main():
    conn = sqlite3.connect(":memory:")
    draft = {"title": "Webhook 投递失败", "priority": "P1"}
    try:
        submit(conn, "alpha", "alice", "request-1", draft, None)
    except PermissionError:
        print("PASS: 未审批的写入被拒绝")
    #: 生产中这一对象必须从受保护记录读取，并检查审批过期、撤回和用户权限。
    approval = Approval("alpha", "alice", payload_hash(draft))
    first = submit(conn, "alpha", "alice", "request-1", draft, approval)
    second = submit(conn, "alpha", "alice", "request-1", draft, approval)
    assert first == second
    print("PASS: 相同请求重试返回同一工单 ID")
    conn.close()

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–4 | 内存 SQLite 不会创建真实工单或保存客户资料。 |
| 5–12 | 先证明拒绝路径，再模拟人工批准；演示不是公网审批接口。 |
| 13–22 | 生产中这一对象必须从受保护记录读取，并检查审批过期、撤回和用户权限。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.approved_ticket
python -m pytest tests/test_core.py -q
```

### 只做这些关键改动

1. 跟踪未审批调用如何在 SQL 之前失败。
2. 在 approved_ticket.py 创建 approval 后把 draft["title"] 改成另一个值，再提交；预期 PermissionError。
3. 恢复草稿，重复相同 key，预期两个 ID 相同。
4. 阅读 test_tickets 中同 key 不同 payload 的冲突用例，解释为什么不能静默复用旧 ID。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

拒绝无审批、跨租户、改草稿和幂等键冲突；相同请求进程重启后仍复用持久文件数据库中的 ID。没有做真实外部 API 并发/故障演练，不能声称 exactly-once。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果允许浏览器直接提交 Approval 对象，这套检查为什么会失效？你会把哪项校验放在模型之外？

**产出：** 受控工具执行参考、幂等/审批测试、真实外部集成的故障清单。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.langchain.com/oss/python/langchain/tools
- https://docs.python.org/3/library/sqlite3.html

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
