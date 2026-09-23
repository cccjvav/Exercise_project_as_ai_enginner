# 7B · 会话状态与可删除长期记忆

> **1A细度源码精讲（2026-09-19补充）：** [examples/memory_lifecycle.py](../code/examples--memory_lifecycle_py.md) · [src/evidencedesk/memory.py](../code/src--evidencedesk--memory_py.md) · [tests/test_core.py](../code/tests--test_core_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](07a-eval-observability.md) · [下一课](07c-integrate-regression-gate.md)

- **前置理解：** 7A；理解隐私和数据生命周期
- **验证状态：** 偏好保存、隔离、到期和删除已测；内存实现不持久化。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

助手应该记得当前会话在讨论 Webhook，但不能把临时错误或另一位用户的偏好永久带入未来回答。记忆既是产品能力，也是隐私风险。

## 2. 原理：在这个问题里理解技术

短期状态是当前会话的消息、摘要或图状态；长期记忆是跨会话保留的已授权信息。历史 ConversationBufferMemory 的概念是保存消息，不应直接照搬旧 API；当前使用框架时核对状态持久化与裁剪接口。

向量记忆按语义找旧记录，不代表旧记录是真事实。先从白名单偏好开始，带租户、用户、同意、到期和删除。now 可注入实现确定性时间测试；读时过期保护与后台清理是两回事。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/memory.py`

完整源文件：[打开源码](../../src/evidencedesk/memory.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/memory.py -->
```python
#: 记忆不是事实知识库；只保存定义好的语言偏好，避免把任意文本当长期指令。
from dataclasses import dataclass, field

#: default_factory 防止不同实例共享同一个可变字典。
@dataclass
class PreferenceMemory:
    records: dict = field(default_factory=dict)

    #: 必须明确同意；now 参数可注入，让到期测试不依赖 sleep。
    def save(self, tenant: str, user: str, language: str, consent: bool, now: float, ttl: float):
        if consent is not True:
            raise PermissionError("需要明确同意")
        if language not in ("zh-CN", "en") or ttl <= 0:
            raise ValueError("只允许已定义的语言偏好和正 TTL")
        self.records[(tenant, user)] = (language, now + ttl)

    #: 读时检查过期，返回前就做租户与用户隔离；不是取出后再让模型过滤。
    def get(self, tenant: str, user: str, now: float):
        key = (tenant, user)
        item = self.records.get(key)
        if item is None:
            return None
        if now >= item[1]:
            self.records.pop(key)
            return None
        return item[0]

    #: 删除幂等；真实系统还需清理向量索引、缓存、备份及保留期内日志副本。
    def forget(self, tenant: str, user: str):
        self.records.pop((tenant, user), None)
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–3 | 记忆不是事实知识库；只保存定义好的语言偏好，避免把任意文本当长期指令。 |
| 4–8 | default_factory 防止不同实例共享同一个可变字典。 |
| 9–16 | 必须明确同意；now 参数可注入，让到期测试不依赖 sleep。 |
| 17–27 | 读时检查过期，返回前就做租户与用户隔离；不是取出后再让模型过滤。 |
| 28–30 | 删除幂等；真实系统还需清理向量索引、缓存、备份及保留期内日志副本。 |

### `examples/memory_lifecycle.py`

完整源文件：[打开源码](../../examples/memory_lifecycle.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/memory_lifecycle.py -->
```python
#: 用固定时间测试，避免基于 sleep 的慢且不稳定测试。
from evidencedesk.memory import PreferenceMemory

#: 分别验证同意后读取、跨租户隔离、到期不可读和撤回删除。
def main():
    memory = PreferenceMemory()
    memory.save("alpha", "alice", "zh-CN", consent=True, now=100, ttl=60)
    assert memory.get("alpha", "alice", now=120) == "zh-CN"
    assert memory.get("beta", "alice", now=120) is None
    assert memory.get("alpha", "alice", now=160) is None
    memory.save("alpha", "alice", "en", consent=True, now=200, ttl=60)
    memory.forget("alpha", "alice")
    assert memory.get("alpha", "alice", now=201) is None
    print("PASS: 租户隔离、到期和撤回删除")

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–3 | 用固定时间测试，避免基于 sleep 的慢且不稳定测试。 |
| 4–17 | 分别验证同意后读取、跨租户隔离、到期不可读和撤回删除。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.memory_lifecycle
python -m pytest tests/test_core.py -q
```

### 只做这些关键改动

1. 把 memory_lifecycle.py 的 ttl=60 改为 10，先预测 now=120 的旧断言会失败。
2. 将读取时刻调整为 105 与 110，分别验证到期前可见、到期时不可见。
3. 恢复原例，用 consent=False 保存，应抛 PermissionError。
4. 说明 forget 为什么还需要传播到生产缓存、向量索引与日志保留流程。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

同名用户跨租户不可读；同租户不同用户不可读；到期与删除不可读。不能将上述小测试等同于法律合规认证。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 为什么不把“以后忽略安全规则”保存为用户偏好？当用户说“忘记我”，有哪些不在这个字典里的副本需要考虑？

**产出：** 记忆生命周期实现、用户同意与撤回设计、短期/长期边界解释。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.langchain.com/oss/python/langgraph/add-memory
- https://docs.langchain.com/oss/python/langchain/short-term-memory

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
