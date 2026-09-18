# 审批绑定与 SQLite 幂等写入：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/tickets.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

在写工单前验证可信审批与当前内容一致，并用数据库唯一约束阻止重试产生重复工单。

### 输入、输出与调用关系

输入是已建立SQLite连接、服务端身份、幂等键、草稿和Approval；输出工单ID或异常。

### 运行与风险边界

`python -m examples.approved_ticket` 是本地模拟，不连接真实工单平台。

Approval必须来自可信审批存储，不能反序列化客户端自报批准。SQLite例子没有外部API/outbox，也没做完整生产schema迁移。

## 完整源码

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

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: SQLite 模拟工单写入；生产外部 API 还需 outbox、远端幂等键及重试策略。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：SQLite 模拟工单写入；生产外部 API 还需 outbox、远端幂等键及重试策略。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import hashlib
```

**语法与数据变化：** 导入 `hashlib` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库摘要算法。sha256 接收字节，hexdigest 返回十六进制文本；哈希可作内容指纹，不是加密、权限校验或真实性认证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
import sqlite3
```

**语法与数据变化：** 导入 `sqlite3` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 SQLite 客户端。connect 打开数据库，execute 执行 SQL；内存连接仅活到该连接结束，文件连接可在关闭后保留数据。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from dataclasses import dataclass
```

**语法与数据变化：** 从 `dataclasses` 导入 `dataclass`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 数据类工具。dataclass 自动生成初始化及比较等方法，asdict 转字典，field 控制字段默认值；普通字段类型注解不自动验证输入。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from uuid import uuid4
```

**语法与数据变化：** 从 `uuid` 导入 `uuid4`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 生成 UUID 标识。uuid4 生成随机标识，不负责业务幂等；同一请求只写一次必须依赖下面的键约束和事务。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
#: Approval 只能由可信服务从受保护审批记录构造，绝不能反序列化客户端自报批准。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Approval 只能由可信服务从受保护审批记录构造，绝不能反序列化客户端自报批准。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L9"></a>
### 第 9 行

```python
@dataclass(frozen=True)
```

**语法与数据变化：** 冻结审批数据类，普通字段不能事后改写。

**为什么与边界：** 冻结不是密码学签名；可信性仍来自谁创建和保存这个对象。

<a id="L10"></a>
### 第 10 行

```python
class Approval:
```

**语法与数据变化：** Approval包含身份与草稿摘要，表达批准的是谁的哪一份内容。

**为什么与边界：** 对象可随意在Python中构造，因此不能单凭类型就信任外部输入。

<a id="L11"></a>
### 第 11 行

```python
    tenant: str
```

**语法与数据变化：** tenant记录审批所属租户。

**为什么与边界：** 跨租户不能因为内容相同就复用审批。

<a id="L12"></a>
### 第 12 行

```python
    user: str
```

**语法与数据变化：** user记录审批绑定的用户身份。

**为什么与边界：** 调用submit时必须与可信审批一致，而不是只比租户。

<a id="L13"></a>
### 第 13 行

```python
    payload_hash: str
```

**语法与数据变化：** payload_hash保存规范化草稿摘要。

**为什么与边界：** 不能把哈希当成全文，审核者必须在批准前看实际内容；摘要用于之后检测内容变化。

<a id="L14"></a>
### 第 14 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L15"></a>
### 第 15 行

```python
#: 按键排序后再哈希，字段顺序不同不影响审批绑定，内容变了则必须重新审批。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：按键排序后再哈希，字段顺序不同不影响审批绑定，内容变了则必须重新审批。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L16"></a>
### 第 16 行

```python
def payload_hash(payload: dict) -> str:
```

**语法与数据变化：** 定义字典到稳定摘要的辅助函数。

**为什么与边界：** 规范化范围是当前JSON可表示的草稿，任意不可序列化对象会报错。

<a id="L17"></a>
### 第 17 行

```python
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
```

**语法与数据变化：** 按键排序、保留Unicode、去掉多余JSON空格，得到规范字符串。

**为什么与边界：** 同键值不同插入顺序产生相同表示；它不等于对语义相似文字做归一，也不能忽略内容差异。

<a id="L18"></a>
### 第 18 行

```python
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
```

**语法与数据变化：** 把规范字符串编码UTF-8并取SHA-256十六进制。

**为什么与边界：** 这是内容绑定，不是加密或不可伪造审批；攻击者也能计算同样哈希。

<a id="L19"></a>
### 第 19 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L20"></a>
### 第 20 行

```python
#: 身份与当前 payload 都匹配才允许进入写路径；拒绝不能晚于写操作。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：身份与当前 payload 都匹配才允许进入写路径；拒绝不能晚于写操作。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L21"></a>
### 第 21 行

```python
def submit(conn: sqlite3.Connection, tenant: str, user: str, key: str,
```

**语法与数据变化：** submit开始声明参数：连接、租户、用户、幂等键。

**为什么与边界：** 函数签名跨到下一行才结束，本行尚未执行数据库操作。

<a id="L22"></a>
### 第 22 行

```python
           payload: dict, approval: Approval | None) -> str:
```

**语法与数据变化：** 补充草稿和可为空审批参数，声明返回字符串ID。

**为什么与边界：** 类型注解不阻止调用方传其他对象；关键条件仍在函数体检查。

<a id="L23"></a>
### 第 23 行

```python
    digest = payload_hash(payload)
```

**语法与数据变化：** 先计算当前草稿摘要digest。

**为什么与边界：** 这一步可能因不可JSON序列化输入失败，尚未写数据库。

<a id="L24"></a>
### 第 24 行

```python
    if approval != Approval(tenant, user, digest):
```

**语法与数据变化：** 构造期望Approval并做数据类字段相等比较。

**为什么与边界：** 要同时匹配租户、用户和当前摘要；None或旧内容的审批都不等。

<a id="L25"></a>
### 第 25 行

```python
        raise PermissionError("缺少与身份、当前草稿一致的可信审批")
```

**语法与数据变化：** 不匹配就抛PermissionError，写路径被阻断。

**为什么与边界：** 不要让模型自己声称“已批准”来创建可比较对象；生产必须验证审批来源。

<a id="L26"></a>
### 第 26 行

```python
    if set(payload) != {"title", "priority"} or not isinstance(payload["title"], str) or not 1 <= len(payload["title"].strip()) <= 120:
```

**语法与数据变化：** 要求字段集合恰好title/priority，标题为字符串且strip后长度1–120。

**为什么与边界：** or短路避免在键不完整时继续访问title；检查strip长度不代表写入时已经清洗原文，本例只存摘要。

<a id="L27"></a>
### 第 27 行

```python
        raise ValueError("工单字段无效")
```

**语法与数据变化：** 草稿字段异常立即抛错。

**为什么与边界：** 审批匹配仍不能替代输入合法性，所以还要有这一层检查。

<a id="L28"></a>
### 第 28 行

```python
    if payload["priority"] not in ("P1", "P3") or not key:
```

**语法与数据变化：** 只支持P1/P3，并要求幂等键truthy。

**为什么与边界：** 本例未严格限制key类型或长度；生产接口应再加契约，不应把此行当成完整键验证。

<a id="L29"></a>
### 第 29 行

```python
        raise ValueError("优先级或幂等键无效")
```

**语法与数据变化：** 不符合优先级/键条件就抛ValueError。

**为什么与边界：** 不会自动降级优先级或生成新key掩盖问题。

<a id="L30"></a>
### 第 30 行

```python
    #: 参数占位符避免 SQL 拼接注入；唯一约束由数据库执行，事务内处理冲突。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：参数占位符避免 SQL 拼接注入；唯一约束由数据库执行，事务内处理冲突。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L31"></a>
### 第 31 行

```python
    with conn:
```

**语法与数据变化：** 进入SQLite连接事务上下文：成功退出提交，异常退出回滚适用的事务操作。

**为什么与边界：** 它不自动关闭连接，不能把它等同外部平台的分布式事务。

<a id="L32"></a>
### 第 32 行

```python
        conn.execute("CREATE TABLE IF NOT EXISTS tickets (tenant TEXT, key TEXT, digest TEXT, id TEXT, PRIMARY KEY (tenant,key))")
```

**语法与数据变化：** 若表不存在则创建，联合主键为(tenant,key)。

**为什么与边界：** 唯一性必须交给数据库，不靠“先查再写”的竞态敏感逻辑；生产通常将建表迁移与请求分离。

<a id="L33"></a>
### 第 33 行

```python
        conn.execute("INSERT OR IGNORE INTO tickets VALUES (?,?,?,?)", (tenant, key, digest, str(uuid4())))
```

**语法与数据变化：** 参数占位符绑定四个值，INSERT OR IGNORE 对主键冲突不重复插入。

**为什么与边界：** uuid4在尝试时生成，即使冲突被忽略也可能生成一个未使用ID；不要用字符串拼接插入用户字段。

<a id="L34"></a>
### 第 34 行

```python
        row = conn.execute("SELECT digest,id FROM tickets WHERE tenant=? AND key=?", (tenant, key)).fetchone()
```

**语法与数据变化：** 按同一租户与key读取已存在或刚插入记录，拿到(digest,id)。

**为什么与边界：** 取回数据库确认的ID，而不是返回本次新生成但可能未写入的UUID。

<a id="L35"></a>
### 第 35 行

```python
        if row[0] != digest:
```

**语法与数据变化：** 比较数据库中的内容摘要与本次请求摘要。

**为什么与边界：** “同key”只允许重试同内容，不能变成任意覆盖旧工单。

<a id="L36"></a>
### 第 36 行

```python
            raise ValueError("同一个幂等键不能用于不同内容")
```

**语法与数据变化：** 同key不同内容时抛错，退出with触发事务错误处理。

**为什么与边界：** 不能以幂等为名接受内容漂移，也不应自动换key偷偷创建新单。

<a id="L37"></a>
### 第 37 行

```python
    return row[1]
```

**语法与数据变化：** 事务成功后返回数据库记录中的ID。

**为什么与边界：** 只证明本地模拟工单记录的幂等写入，不证明外部工单系统已收到请求。

## 跟一遍数据与验证边界

相同身份、相同key和内容重试得到相同ID；相同key改内容被拒绝。换租户的同key可独立存在。审批后改正文必须重新审批，不能复用旧payload_hash。

## 只练一个关键点（不是新的学习验收记录）

1. 运行test_tickets，对照None审批、跨租户、变内容和同key冲突四种路径。
2. 用草稿字段顺序交换计算hash，随后只改title再算，观察哪种变化需要新审批。
3. **复盘：** 哈希绑定为什么不是不可伪造的审批签名？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
