# 5C · PostgreSQL、RLS 与缓存隔离

> **1A细度源码精讲（2026-09-19补充）：** [deploy/schema.sql](../code/deploy--schema_sql.md) · [examples/cache_scope.py](../code/examples--cache_scope_py.md) · [tools/fetch_public_manuals.py](../code/tools--fetch_public_manuals_py.md) · [tools/local_postgres.py](../code/tools--local_postgres_py.md) · [tools/postgres_lab.py](../code/tools--postgres_lab_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](05b-typescript-ui.md) · [下一课](06a-langgraph.md)

- **前置理解：** 5A；理解认证与授权区别
- **验证状态：** 缓存键与本地 PostgreSQL 18.4 的 documents RLS 已实测。完整复现见 [零预算执行记录](../course/zero-budget.md)，托管云数据库仍未创建。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

应用过滤可能漏写一次查询，缓存也可能把 Alice 的答案直接给 Bob。需要在存储层增加隔离，并让缓存身份、权限与数据版本一致。

## 2. 原理：在这个问题里理解技术

PostgreSQL 复合主键同时绑定租户和业务 ID。RLS 的 USING 限制可读行，WITH CHECK 限制写入行；FORCE RLS 仍不能约束超级用户或 BYPASSRLS。应用必须用权限最小化角色，身份来自可信认证层。

连接池会复用连接，使用事务内 set_config(..., true) 设置身份，使事务结束自动清理。Redis 的 TTL 只控制寿命，不自动理解撤权；键必须含租户、用户、ACL 版本、索引版本和问题。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `deploy/schema.sql`

完整源文件：[打开源码](../../deploy/schema.sql)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: deploy/schema.sql -->
```sql
--: 使用事务避免半套 schema；用于空的实验数据库，生产迁移需专门版本工具。
BEGIN;
CREATE TABLE documents (
    tenant_id text NOT NULL,
    document_id text NOT NULL,
    version text NOT NULL,
    body text NOT NULL,
    PRIMARY KEY (tenant_id, document_id)
);
--: RLS 使行可见性取决于会话身份；应用必须是非超级用户、非 BYPASSRLS 角色。
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));
--: 幂等键以租户为作用域，唯一约束处理并发冲突，而不是仅靠先查询后插入。
CREATE TABLE tickets (
    tenant_id text NOT NULL,
    idempotency_key text NOT NULL,
    approved_payload_hash text NOT NULL,
    ticket_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, idempotency_key)
);
COMMIT;
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–9 | 使用事务避免半套 schema；用于空的实验数据库，生产迁移需专门版本工具。 |
| 10–15 | RLS 使行可见性取决于会话身份；应用必须是非超级用户、非 BYPASSRLS 角色。 |
| 16–24 | 幂等键以租户为作用域，唯一约束处理并发冲突，而不是仅靠先查询后插入。 |

### `examples/cache_scope.py`

完整源文件：[打开源码](../../examples/cache_scope.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/cache_scope.py -->
```python
#: 缓存键可能成为旁路权限漏洞；演示键设计，不假装已经连接 Redis。
import hashlib
import json

#: 用户、授权版本、索引版本与问题共同决定键；JSON 数组避免简单拼接冲突。
def cache_key(tenant: str, user: str, acl_version: str, index_version: str, query: str) -> str:
    payload = json.dumps([tenant, user, acl_version, index_version, query], ensure_ascii=False)
    return "answer:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

#: 相同问题跨用户不可复用缓存，ACL 改变后也不能继续命中旧授权结果。
def main():
    a = cache_key("alpha", "alice", "acl-v1", "index-v1", "重试")
    b = cache_key("beta", "bob", "acl-v1", "index-v1", "重试")
    assert a != b
    assert a != cache_key("alpha", "alice", "acl-v2", "index-v1", "重试")
    print("PASS: 用户、租户和授权版本改变都会隔离缓存键")

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–4 | 缓存键可能成为旁路权限漏洞；演示键设计，不假装已经连接 Redis。 |
| 5–9 | 用户、授权版本、索引版本与问题共同决定键；JSON 数组避免简单拼接冲突。 |
| 10–19 | 相同问题跨用户不可复用缓存，ACL 改变后也不能继续命中旧授权结果。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.cache_scope
# 仅在专用、可丢弃的实验 PostgreSQL 数据库执行，PG_DSN 不进入 Git
psql "$PG_DSN" -v ON_ERROR_STOP=1 -f deploy/schema.sql
```

### 只做这些关键改动

1. 先跑缓存示例，确认租户/ACL版本变化产生不同键。
2. 有 PostgreSQL 时，让管理员在新实验库创建 schema 与非超级用户应用角色，并仅授予需要的表权限。
3. 用该应用角色开启 BEGIN，执行 `SELECT set_config('app.tenant_id', 'alpha', true);`，插入 alpha 文档；尝试插入 beta 应失败。失败后 ROLLBACK。
4. 新事务不设置 tenant，预期查询不可见；分别以 alpha/beta 测试，不以管理员角色声称隔离通过。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

记录数据库版本、角色属性、SQL 和实际结果。当前 schema 只有 documents 做 RLS，tickets 未附策略；接入真实工单库之前必须补充租户隔离或受控查询，不把本文件当完备生产 schema。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果用户权限被撤销而缓存 TTL 还有一天，如何确保旧答案立即不可见？为什么哈希缓存键并不等于敏感信息加密？

**产出：** 存储权限实验记录、缓存键设计、未验证项目清单。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- https://redis.io/docs/latest/develop/data-types/strings/

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
