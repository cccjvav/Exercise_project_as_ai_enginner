# 文档行级权限与工单幂等表：逐行精讲

[精讲总目录](index.md) · [对应源码](../../deploy/schema.sql)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把租户范围约束交给数据库策略与唯一键，而不是只依赖应用先查再写。

### 输入、输出与调用关系

在空实验schema创建documents/tickets及documents RLS；整个DDL事务提交。

### 运行与风险边界

优先通过已隔离的tools.postgres_lab执行，不对生产库直接运行此文件。

不是版本迁移工具，重复建同名表会失败。只有documents启用RLS；tickets尚无策略，不能宣称全库多租户安全。

## 完整源码

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

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```sql
--: 使用事务避免半套 schema；用于空的实验数据库，生产迁移需专门版本工具。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：使用事务避免半套 schema；用于空的实验数据库，生产迁移需专门版本工具。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```sql
BEGIN;
```

**语法与数据变化：** BEGIN开启事务。

**为什么与边界：** 中途DDL失败应回滚整套创建，仍需调用方正确处理事务状态。

<a id="L3"></a>
### 第 3 行

```sql
CREATE TABLE documents (
```

**语法与数据变化：** 开始创建documents表。

**为什么与边界：** 未用IF NOT EXISTS，目标需空实验schema。

<a id="L4"></a>
### 第 4 行

```sql
    tenant_id text NOT NULL,
```

**语法与数据变化：** tenant_id为非NULL文本。

**为什么与边界：** NOT NULL不拒绝空字符串，也不自动验证真实租户身份。

<a id="L5"></a>
### 第 5 行

```sql
    document_id text NOT NULL,
```

**语法与数据变化：** document_id为非NULL文本业务标识。

**为什么与边界：** 与tenant组合才唯一，不要求全库不同租户共用ID时冲突。

<a id="L6"></a>
### 第 6 行

```sql
    version text NOT NULL,
```

**语法与数据变化：** version保存内容版本文本。

**为什么与边界：** 字段名不自动计算hash，由写入方负责一致性。

<a id="L7"></a>
### 第 7 行

```sql
    body text NOT NULL,
```

**语法与数据变化：** body存正文，禁止NULL。

**为什么与边界：** 不自动验证非空、许可证、敏感信息或文本质量。

<a id="L8"></a>
### 第 8 行

```sql
    PRIMARY KEY (tenant_id, document_id)
```

**语法与数据变化：** 复合主键限定(tenant,document_id)唯一。

**为什么与边界：** version不在主键，因此这是每租户每文档一条当前记录，不是完整历史版本表。

<a id="L9"></a>
### 第 9 行

```sql
);
```

**语法与数据变化：** 闭合表定义并结束语句。

**为什么与边界：** 实际创建仍在前面BEGIN的事务中。

<a id="L10"></a>
### 第 10 行

```sql
--: RLS 使行可见性取决于会话身份；应用必须是非超级用户、非 BYPASSRLS 角色。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：RLS 使行可见性取决于会话身份；应用必须是非超级用户、非 BYPASSRLS 角色。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L11"></a>
### 第 11 行

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
```

**语法与数据变化：** 为documents启用RLS。

**为什么与边界：** 只有开启后策略才控制普通角色行访问。

<a id="L12"></a>
### 第 12 行

```sql
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

**语法与数据变化：** FORCE让表所有者通常也受RLS约束。

**为什么与边界：** 超级用户/BYPASSRLS仍可绕过，实验必须使用受限角色。

<a id="L13"></a>
### 第 13 行

```sql
CREATE POLICY tenant_isolation ON documents
```

**语法与数据变化：** 定义名为tenant_isolation的策略。

**为什么与边界：** 未指定单一命令时作用于适用操作，不替代GRANT表权限。

<a id="L14"></a>
### 第 14 行

```sql
    USING (tenant_id = current_setting('app.tenant_id', true))
```

**语法与数据变化：** USING限制可见旧行：行tenant等于当前会话配置。

**为什么与边界：** current_setting第二参true在缺配置时不抛错；NULL比较不为true，默认无行可见。

<a id="L15"></a>
### 第 15 行

```sql
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));
```

**语法与数据变化：** WITH CHECK限制插入/更新后的新行仍属于当前租户。

**为什么与边界：** 只写USING不足以阻止把合法旧行改到别的租户；应用必须可信设置该GUC。

<a id="L16"></a>
### 第 16 行

```sql
--: 幂等键以租户为作用域，唯一约束处理并发冲突，而不是仅靠先查询后插入。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：幂等键以租户为作用域，唯一约束处理并发冲突，而不是仅靠先查询后插入。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L17"></a>
### 第 17 行

```sql
CREATE TABLE tickets (
```

**语法与数据变化：** 开始建立tickets表。

**为什么与边界：** 此SQL表与SQLite教学submit实现不是已经自动连通的一套后端。

<a id="L18"></a>
### 第 18 行

```sql
    tenant_id text NOT NULL,
```

**语法与数据变化：** 工单tenant非NULL。

**为什么与边界：** 字段存在不等于RLS已配置。

<a id="L19"></a>
### 第 19 行

```sql
    idempotency_key text NOT NULL,
```

**语法与数据变化：** idempotency_key标记同一业务请求。

**为什么与边界：** 调用者重试应复用key，不应每次新建。

<a id="L20"></a>
### 第 20 行

```sql
    approved_payload_hash text NOT NULL,
```

**语法与数据变化：** 保存审批绑定内容的摘要。

**为什么与边界：** 数据库不在此验证审批来源、过期或正文摘要正确性。

<a id="L21"></a>
### 第 21 行

```sql
    ticket_id uuid NOT NULL,
```

**语法与数据变化：** ticket_id使用UUID类型，禁止NULL。

**为什么与边界：** 此定义没有DEFAULT，写入方必须提供；也未独立声明其全表UNIQUE。

<a id="L22"></a>
### 第 22 行

```sql
    PRIMARY KEY (tenant_id, idempotency_key)
```

**语法与数据变化：** 租户与请求key组成唯一主键。

**为什么与边界：** 同租户重复key在数据库层冲突，支持并发幂等；是否同内容仍需应用检查。

<a id="L23"></a>
### 第 23 行

```sql
);
```

**语法与数据变化：** 结束tickets定义。

**为什么与边界：** 本文件没有给tickets加RLS，不能从documents策略推导另一表自动受保护。

<a id="L24"></a>
### 第 24 行

```sql
COMMIT;
```

**语法与数据变化：** 提交完整DDL事务。

**为什么与边界：** 成功才生效，生产迁移需要额外版本、回滚和权限审查流程。

## 跟一遍数据与验证边界

alpha会话SELECT只能见alpha；UPDATE把tenant改beta应被WITH CHECK拒绝。不同tenant可用同document_id，但同tenant只能保存一个当前文档版本。

## 只练一个关键点（不是新的学习验收记录）

1. 先逐行标出documents策略和tickets定义，不在生产库执行。
2. 在授权的本地实验中通过postgres_lab验证，确认角色非超管；执行前核对socket路径。
3. **复盘：** tickets有tenant字段为什么仍不能说已启用RLS？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
