# 真实PostgreSQL文档RLS与重启回执实验：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tools/postgres_lab.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用非超管、无绕过RLS的随机角色验证读写隔离，清理随机资源并保留最小非敏感运行回执。

### 输入、输出与调用关系

本地socket、虚构/授权公开文档、schema.sql→隔离断言及artifacts报告。

### 运行与风险边界

仅在课程确认本地PG启动、公开语料已下载且psycopg已安装后 `python -m tools.postgres_lab`；重启后才用--check-persisted验证回执可读。

创建/删除数据库schema和角色；只对自有本地实验集群运行。不是应用鉴权、tickets RLS或托管云DB验收；本轮材料准备不重新启动它。

## 完整源码

<!-- source: tools/postgres_lab.py -->
```python
"""Execute real PostgreSQL RLS tests; only the owned local lab socket is used.
Temporary schema/role names are random. Only those resources are cleaned up.
"""
import argparse
import hashlib
import json
from pathlib import Path
from uuid import uuid4
import psycopg
from psycopg import sql
from evidencedesk.documents import load_documents

ROOT = Path(__file__).resolve().parents[1]
SOCKET = ROOT / "artifacts/postgres/socket"


def connect():
    return psycopg.connect(host=str(SOCKET), port=55432, dbname="postgres", autocommit=True)


def persisted():
    with connect() as conn:
        count = conn.execute("SELECT count(*) FROM evidencedesk_lab_state.runs").fetchone()[0]
        assert count > 0
        print(json.dumps({"persisted_run_count": count, "restart_read": "PASS"}))


def run():
    schema = "course_" + uuid4().hex[:16]
    role = "reader_" + uuid4().hex[:16]
    checks = []
    sample = load_documents(ROOT / "data/sample")
    public = load_documents(ROOT / "data/processed/fastapi")
    with connect() as conn:
        version = conn.execute("SELECT version()").fetchone()[0]
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("CREATE ROLE {} NOLOGIN NOSUPERUSER NOBYPASSRLS").format(sql.Identifier(role)))
        try:
            conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
            conn.execute((ROOT / "deploy/schema.sql").read_text())
            for tenant, docs in [("alpha", sample), ("beta", public)]:
                for doc in docs:
                    conn.execute("INSERT INTO documents VALUES (%s,%s,%s,%s)",
                                 (tenant, doc.id, hashlib.sha256(doc.text.encode()).hexdigest(), doc.text))
            conn.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(sql.Identifier(schema), sql.Identifier(role)))
            conn.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE ON documents TO {}").format(sql.Identifier(role)))
            for tenant, expected in [("alpha", sample), ("beta", public)]:
                with conn.transaction():
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                    current, superuser, bypass = conn.execute("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user").fetchone()
                    assert current == role and not superuser and not bypass
                    conn.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant,))
                    actual = conn.execute("SELECT document_id FROM documents").fetchall()
                    assert {row[0] for row in actual} == {doc.id for doc in expected}
                checks.append(f"{tenant}: non-superuser tenant isolation PASS")
            try:
                with conn.transaction():
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                    conn.execute("SELECT set_config('app.tenant_id', 'alpha', true)")
                    conn.execute("INSERT INTO documents VALUES ('beta','forbidden','v1','blocked')")
            except psycopg.errors.InsufficientPrivilege:
                checks.append("cross-tenant INSERT rejected PASS")
            else:
                raise AssertionError("RLS write check failed")
            try:
                with conn.transaction():
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                    conn.execute("SELECT set_config('app.tenant_id', 'alpha', true)")
                    conn.execute("UPDATE documents SET tenant_id='beta' WHERE document_id='webhook-delivery'")
            except psycopg.errors.InsufficientPrivilege:
                checks.append("cross-tenant UPDATE rejected PASS")
            else:
                raise AssertionError("RLS update check failed")
            with conn.transaction():
                conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                setting = conn.execute("SELECT current_setting('app.tenant_id',true)").fetchone()[0]
                assert setting in (None, "")
                assert conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
            checks.append("transaction-local identity reset; no identity sees zero rows PASS")
            # Keep only a tiny nonsensitive receipt to verify a server restart, not copied document bodies.
            conn.execute("CREATE SCHEMA IF NOT EXISTS evidencedesk_lab_state")
            conn.execute("CREATE TABLE IF NOT EXISTS evidencedesk_lab_state.runs (id text PRIMARY KEY, checked_at timestamptz DEFAULT now())")
            conn.execute("INSERT INTO evidencedesk_lab_state.runs(id) VALUES(%s)", (uuid4().hex,))
        finally:
            conn.execute("RESET search_path")
            conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
            conn.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
    result = {"postgres": version, "transport": "private Unix socket; TCP disabled", "documents_imported": len(sample)+len(public),
              "synthetic_documents": len(sample), "public_licensed_documents": len(public), "checks": checks,
              "scope": "documents RLS only; app authentication, tickets RLS and managed cloud DB not certified"}
    path = ROOT / "artifacts/postgres-validation.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-persisted", action="store_true")
    args = parser.parse_args()
    persisted() if args.check_persisted else run()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""Execute real PostgreSQL RLS tests; only the owned local lab socket is used.
```

**语法与数据变化：** 模块说明声明真实数据库测试和私有socket范围。

**为什么与边界：** 不是SQLite/mock，也不能改成任意生产URL随便执行。

<a id="L2"></a>
### 第 2 行

```python
Temporary schema/role names are random. Only those resources are cleaned up.
```

**语法与数据变化：** 随机临时命名并只清理这些资源。

**为什么与边界：** 仍需有创建/删除角色权限的本地实验所有者连接。

<a id="L3"></a>
### 第 3 行

```python
"""
```

**语法与数据变化：** 闭合说明字符串。

**为什么与边界：** 不参与SQL执行。

<a id="L4"></a>
### 第 4 行

```python
import argparse
```

**语法与数据变化：** 导入 `argparse` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库命令行解析器。它把终端字符串按参数规则转换，type=int 是实际调用整数转换，而不是类型注解。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
import hashlib
```

**语法与数据变化：** 导入 `hashlib` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库摘要算法。sha256 接收字节，hexdigest 返回十六进制文本；哈希可作内容指纹，不是加密、权限校验或真实性认证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
from uuid import uuid4
```

**语法与数据变化：** 从 `uuid` 导入 `uuid4`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 生成 UUID 标识。uuid4 生成随机标识，不负责业务幂等；同一请求只写一次必须依赖下面的键约束和事务。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

```python
import psycopg
```

**语法与数据变化：** 导入 `psycopg` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** PostgreSQL 客户端。连接、事务与 SQL 均作用于实际数据库；安装驱动不等于已安装服务器。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L10"></a>
### 第 10 行

```python
from psycopg import sql
```

**语法与数据变化：** 导入psycopg.sql安全组合标识符工具。

**为什么与边界：** 表/schema/role名称不能用值占位符替代，也不能直接拼不可信字符串。

<a id="L11"></a>
### 第 11 行

```python
from evidencedesk.documents import load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 定位仓库根目录。

**为什么与边界：** 数据和schema输入固定可审阅。

<a id="L14"></a>
### 第 14 行

```python
SOCKET = ROOT / "artifacts/postgres/socket"
```

**语法与数据变化：** 固定私有socket路径。

**为什么与边界：** 没有从用户请求接收远程数据库地址。

<a id="L15"></a>
### 第 15 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L16"></a>
### 第 16 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L17"></a>
### 第 17 行

```python
def connect():
```

**语法与数据变化：** 封装每次建立连接。

**为什么与边界：** 后面上下文负责真实连接生命周期。

<a id="L18"></a>
### 第 18 行

```python
    return psycopg.connect(host=str(SOCKET), port=55432, dbname="postgres", autocommit=True)
```

**语法与数据变化：** 连接socket的postgres库，开启autocommit。

**为什么与边界：** 常规语句独立提交，conn.transaction仍可显式开启事务；默认系统用户名需具备实验权限。

<a id="L19"></a>
### 第 19 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L20"></a>
### 第 20 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L21"></a>
### 第 21 行

```python
def persisted():
```

**语法与数据变化：** 定义读取持久回执的检查。

**为什么与边界：** 它不主动重启服务器。

<a id="L22"></a>
### 第 22 行

```python
    with connect() as conn:
```

**语法与数据变化：** 建立连接并上下文管理关闭。

**为什么与边界：** psycopg与sqlite3上下文关闭语义不同，不能混为一谈。

<a id="L23"></a>
### 第 23 行

```python
        count = conn.execute("SELECT count(*) FROM evidencedesk_lab_state.runs").fetchone()[0]
```

**语法与数据变化：** 查询专用回执表数量并取第一行第一列。

**为什么与边界：** 表不存在应失败，不能当作重启验证成功。

<a id="L24"></a>
### 第 24 行

```python
        assert count > 0
```

**语法与数据变化：** 要求至少一次有效运行回执。

**为什么与边界：** 这只证明当前可读，需外部实际停启记录才能声称重启持久。

<a id="L25"></a>
### 第 25 行

```python
        print(json.dumps({"persisted_run_count": count, "restart_read": "PASS"}))
```

**语法与数据变化：** 输出数量和restart_read标签。

**为什么与边界：** 标签不是自动观察重启事件，报告必须说明执行上下文。

<a id="L26"></a>
### 第 26 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L27"></a>
### 第 27 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L28"></a>
### 第 28 行

```python
def run():
```

**语法与数据变化：** 定义完整RLS实验流程。

**为什么与边界：** 有数据库创建/写入/删除副作用。

<a id="L29"></a>
### 第 29 行

```python
    schema = "course_" + uuid4().hex[:16]
```

**语法与数据变化：** 生成随机course_ schema名。

**为什么与边界：** 降低与其他实验碰撞，避免删除固定业务schema。

<a id="L30"></a>
### 第 30 行

```python
    role = "reader_" + uuid4().hex[:16]
```

**语法与数据变化：** 另生成随机只读测试角色名。

**为什么与边界：** role作用域是集群，不仅当前schema。

<a id="L31"></a>
### 第 31 行

```python
    checks = []
```

**语法与数据变化：** 建立成功检查记录列表。

**为什么与边界：** 只有对应断言通过后才append，不能提前填PASS。

<a id="L32"></a>
### 第 32 行

```python
    sample = load_documents(ROOT / "data/sample")
```

**语法与数据变化：** 加载公开虚构样例。

**为什么与边界：** 用于alpha租户。

<a id="L33"></a>
### 第 33 行

```python
    public = load_documents(ROOT / "data/processed/fastapi")
```

**语法与数据变化：** 加载已下载授权FastAPI规范文本。

**为什么与边界：** 未下载目录会失败，不应拿空数据冒充beta隔离成功。

<a id="L34"></a>
### 第 34 行

```python
    with connect() as conn:
```

**语法与数据变化：** 建立本地所有者连接。

**为什么与边界：** 初始化权限比后续被测角色高，所以必须显式降角色再测RLS。

<a id="L35"></a>
### 第 35 行

```python
        version = conn.execute("SELECT version()").fetchone()[0]
```

**语法与数据变化：** 查询真实服务器版本。

**为什么与边界：** 不把驱动版本或npm标签当数据库版本。

<a id="L36"></a>
### 第 36 行

```python
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
```

**语法与数据变化：** 安全引用随机schema标识符并创建。

**为什么与边界：** 不是SQL值占位符；此处在try前，创建失败不会走后面finally。

<a id="L37"></a>
### 第 37 行

```python
        conn.execute(sql.SQL("CREATE ROLE {} NOLOGIN NOSUPERUSER NOBYPASSRLS").format(sql.Identifier(role)))
```

**语法与数据变化：** 创建NOLOGIN/NOSUPERUSER/NOBYPASSRLS角色。

**为什么与边界：** 防止超管/绕过权限让RLS实验失真；若此步失败，前一步schema可能残留，当前清理保护不是全程完备。

<a id="L38"></a>
### 第 38 行

```python
        try:
```

**语法与数据变化：** 开始被finally保护的实验部分。

**为什么与边界：** 后面错误也尝试清理，但清理自身失败仍需人工核对随机资源。

<a id="L39"></a>
### 第 39 行

```python
            conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
```

**语法与数据变化：** 设置search_path到本次schema。

**为什么与边界：** 不在public业务schema建表；标识符用Identifier保护。

<a id="L40"></a>
### 第 40 行

```python
            conn.execute((ROOT / "deploy/schema.sql").read_text())
```

**语法与数据变化：** 读取受控schema.sql并执行多条DDL。

**为什么与边界：** 脚本可产生副作用，必须审查仓库SQL，不能执行任意下载SQL。

<a id="L41"></a>
### 第 41 行

```python
            for tenant, docs in [("alpha", sample), ("beta", public)]:
```

**语法与数据变化：** 将两组文档配给alpha/beta。

**为什么与边界：** 租户值由实验构造，不是来自浏览器身份声明。

<a id="L42"></a>
### 第 42 行

```python
                for doc in docs:
```

**语法与数据变化：** 遍历当前租户每份文档。

**为什么与边界：** 每次插入一行，不是向量分块索引。

<a id="L43"></a>
### 第 43 行

```python
                    conn.execute("INSERT INTO documents VALUES (%s,%s,%s,%s)",
```

**语法与数据变化：** 参数化INSERT四列值。

**为什么与边界：** %s交给驱动绑定，不要用Python字符串格式化插值正文。

<a id="L44"></a>
### 第 44 行

```python
                                 (tenant, doc.id, hashlib.sha256(doc.text.encode()).hexdigest(), doc.text))
```

**语法与数据变化：** 传租户、文档ID、正文摘要和正文。

**为什么与边界：** hash针对正文，未包含标题/ACL；这里列顺序依赖schema定义。

<a id="L45"></a>
### 第 45 行

```python
            conn.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(sql.Identifier(schema), sql.Identifier(role)))
```

**语法与数据变化：** 授予角色使用本次schema权限。

**为什么与边界：** 只授表SELECT而没schema USAGE可能因另一权限错误产生假阳性。

<a id="L46"></a>
### 第 46 行

```python
            conn.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE ON documents TO {}").format(sql.Identifier(role)))
```

**语法与数据变化：** 授documents的SELECT/INSERT/UPDATE。

**为什么与边界：** 测试拒绝应来自RLS而非完全没表操作权限；不授权DROP或绕过RLS。

<a id="L47"></a>
### 第 47 行

```python
            for tenant, expected in [("alpha", sample), ("beta", public)]:
```

**语法与数据变化：** 分别验证两个租户应见文档集合。

**为什么与边界：** 不能只查alpha看不到beta而漏掉beta本身能否正常访问。

<a id="L48"></a>
### 第 48 行

```python
                with conn.transaction():
```

**语法与数据变化：** 显式事务限定角色和tenant配置生命周期。

**为什么与边界：** 配合SET LOCAL与set_config第三参true，退出不残留身份。

<a id="L49"></a>
### 第 49 行

```python
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
```

**语法与数据变化：** 在事务内切到随机受限角色。

**为什么与边界：** 确保不是所有者/超管在执行待测查询。

<a id="L50"></a>
### 第 50 行

```python
                    current, superuser, bypass = conn.execute("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user").fetchone()
```

**语法与数据变化：** 读取current_user及超管/绕过标志。

**为什么与边界：** 实际验证会话权限，不能仅信CREATE ROLE写了选项。

<a id="L51"></a>
### 第 51 行

```python
                    assert current == role and not superuser and not bypass
```

**语法与数据变化：** 断言角色正确且没有两种绕过能力。

**为什么与边界：** 失败就不能解释后续结果为有效RLS验证。

<a id="L52"></a>
### 第 52 行

```python
                    conn.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant,))
```

**语法与数据变化：** 设置当前事务tenant GUC，用参数绑定值。

**为什么与边界：** 生产必须由可信应用设置；用户能任意SET tenant就会破坏身份边界。

<a id="L53"></a>
### 第 53 行

```python
                    actual = conn.execute("SELECT document_id FROM documents").fetchall()
```

**语法与数据变化：** 不带WHERE查询document_id。

**为什么与边界：** 隔离应由数据库策略实现，而不是应用WHERE碰巧过滤。

<a id="L54"></a>
### 第 54 行

```python
                    assert {row[0] for row in actual} == {doc.id for doc in expected}
```

**语法与数据变化：** 实际ID集合与当前租户预期完全相等。

**为什么与边界：** 同时发现越权额外行和错误漏行。

<a id="L55"></a>
### 第 55 行

```python
                checks.append(f"{tenant}: non-superuser tenant isolation PASS")
```

**语法与数据变化：** 事务结束后记录该租户通过。

**为什么与边界：** 每租户独立一条检查。

<a id="L56"></a>
### 第 56 行

```python
            try:
```

**语法与数据变化：** 开始跨租户INSERT负例。

**为什么与边界：** 用try/except/else区分预期拒绝与误放行。

<a id="L57"></a>
### 第 57 行

```python
                with conn.transaction():
```

**语法与数据变化：** 为拒绝操作开独立事务。

**为什么与边界：** 错误将回滚，不污染后续实验连接状态。

<a id="L58"></a>
### 第 58 行

```python
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
```

**语法与数据变化：** 再次切换受限角色。

**为什么与边界：** 前一事务的SET LOCAL已经恢复，不能假设仍受限。

<a id="L59"></a>
### 第 59 行

```python
                    conn.execute("SELECT set_config('app.tenant_id', 'alpha', true)")
```

**语法与数据变化：** 当前租户为alpha。

**为什么与边界：** 下面故意写beta，形成策略冲突。

<a id="L60"></a>
### 第 60 行

```python
                    conn.execute("INSERT INTO documents VALUES ('beta','forbidden','v1','blocked')")
```

**语法与数据变化：** 尝试插入beta行。

**为什么与边界：** 拥有INSERT表权限，真正被测的是WITH CHECK租户条件。

<a id="L61"></a>
### 第 61 行

```python
            except psycopg.errors.InsufficientPrivilege:
```

**语法与数据变化：** 只接受InsufficientPrivilege作为预期拒绝。

**为什么与边界：** 其他语法/连接错误不能被当成安全检查通过。

<a id="L62"></a>
### 第 62 行

```python
                checks.append("cross-tenant INSERT rejected PASS")
```

**语法与数据变化：** 记跨租户插入被拒绝。

**为什么与边界：** 在捕获到具体异常后才写PASS。

<a id="L63"></a>
### 第 63 行

```python
            else:
```

**语法与数据变化：** 若try没有异常则进入else。

**为什么与边界：** 防止函数静默允许写入仍继续报告成功。

<a id="L64"></a>
### 第 64 行

```python
                raise AssertionError("RLS write check failed")
```

**语法与数据变化：** 主动抛AssertionError指出RLS写检查失败。

**为什么与边界：** 不是用print警告后继续当通过。

<a id="L65"></a>
### 第 65 行

```python
            try:
```

**语法与数据变化：** 开始跨租户UPDATE负例。

**为什么与边界：** INSERT拒绝不能自动证明UPDATE也受保护。

<a id="L66"></a>
### 第 66 行

```python
                with conn.transaction():
```

**语法与数据变化：** 独立事务隔离这次失败。

**为什么与边界：** 失败时数据库会回滚该事务。

<a id="L67"></a>
### 第 67 行

```python
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
```

**语法与数据变化：** 切换受限角色。

**为什么与边界：** 不以高权限所有者测试策略。

<a id="L68"></a>
### 第 68 行

```python
                    conn.execute("SELECT set_config('app.tenant_id', 'alpha', true)")
```

**语法与数据变化：** 把当前租户设alpha。

**为什么与边界：** 可读到原alpha的Webhook行，避免WHERE根本没匹配而假成功。

<a id="L69"></a>
### 第 69 行

```python
                    conn.execute("UPDATE documents SET tenant_id='beta' WHERE document_id='webhook-delivery'")
```

**语法与数据变化：** 尝试把该行tenant_id改为beta。

**为什么与边界：** USING允许读旧行，WITH CHECK必须拒绝新行越界。

<a id="L70"></a>
### 第 70 行

```python
            except psycopg.errors.InsufficientPrivilege:
```

**语法与数据变化：** 捕获精确权限异常。

**为什么与边界：** 其他故障应继续报错，不掩饰。

<a id="L71"></a>
### 第 71 行

```python
                checks.append("cross-tenant UPDATE rejected PASS")
```

**语法与数据变化：** 记录更新拒绝通过。

**为什么与边界：** 此测试针对documents，不是tickets表。

<a id="L72"></a>
### 第 72 行

```python
            else:
```

**语法与数据变化：** 如果没有异常，进入else。

**为什么与边界：** UPDATE0行也不会抛权限错误，所以这里不会误当成功保护。

<a id="L73"></a>
### 第 73 行

```python
                raise AssertionError("RLS update check failed")
```

**语法与数据变化：** 明确报RLS更新失败。

**为什么与边界：** 需要审查数据与策略，不能靠修改预期消除失败。

<a id="L74"></a>
### 第 74 行

```python
            with conn.transaction():
```

**语法与数据变化：** 开新事务检查身份清空。

**为什么与边界：** 不在此事务设置tenant。

<a id="L75"></a>
### 第 75 行

```python
                conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
```

**语法与数据变化：** 仍使用受限角色。

**为什么与边界：** 无tenant且超管读取全表不具备验证意义。

<a id="L76"></a>
### 第 76 行

```python
                setting = conn.execute("SELECT current_setting('app.tenant_id',true)").fetchone()[0]
```

**语法与数据变化：** missing_ok=true读取可能不存在的tenant配置。

**为什么与边界：** 连接曾设置过事务局部GUC，恢复后可能表现为空串而非None。

<a id="L77"></a>
### 第 77 行

```python
                assert setting in (None, "")
```

**语法与数据变化：** 接受None或空串，拒绝残留alpha/beta。

**为什么与边界：** 避免连接复用泄漏上一请求租户。

<a id="L78"></a>
### 第 78 行

```python
                assert conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
```

**语法与数据变化：** 无身份应看到零行。

**为什么与边界：** 缺身份不能默认全库可见。

<a id="L79"></a>
### 第 79 行

```python
            checks.append("transaction-local identity reset; no identity sees zero rows PASS")
```

**语法与数据变化：** 记录事务身份重置及默认拒绝通过。

**为什么与边界：** 不等于应用连接池所有实际路径都已验证。

<a id="L80"></a>
### 第 80 行

```python
            # Keep only a tiny nonsensitive receipt to verify a server restart, not copied document bodies.
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Keep only a tiny nonsensitive receipt to verify a server restart, not copied document bodies. 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L81"></a>
### 第 81 行

```python
            conn.execute("CREATE SCHEMA IF NOT EXISTS evidencedesk_lab_state")
```

**语法与数据变化：** 创建长期保留的小回执schema，不包含文档正文。

**为什么与边界：** 这不是临时course_ schema，后面不删除它。

<a id="L82"></a>
### 第 82 行

```python
            conn.execute("CREATE TABLE IF NOT EXISTS evidencedesk_lab_state.runs (id text PRIMARY KEY, checked_at timestamptz DEFAULT now())")
```

**语法与数据变化：** 建回执表，含唯一ID与数据库时间。

**为什么与边界：** IF NOT EXISTS支持重复实验，不保存客户文本。

<a id="L83"></a>
### 第 83 行

```python
            conn.execute("INSERT INTO evidencedesk_lab_state.runs(id) VALUES(%s)", (uuid4().hex,))
```

**语法与数据变化：** 参数绑定新的随机回执ID插入。

**为什么与边界：** autocommit使回执保留，用于后续重启读取。

<a id="L84"></a>
### 第 84 行

```python
        finally:
```

**语法与数据变化：** 无论实验成功失败进入清理。

**为什么与边界：** finally不是完全无失败保证，还需权限与数据库连接正常。

<a id="L85"></a>
### 第 85 行

```python
            conn.execute("RESET search_path")
```

**语法与数据变化：** 恢复默认search_path。

**为什么与边界：** 避免清理后会话继续指向已删除schema。

<a id="L86"></a>
### 第 86 行

```python
            conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
```

**语法与数据变化：** 只DROP本次随机schema并CASCADE清理内部对象。

**为什么与边界：** CASCADE有破坏性，严禁改成业务schema；本工具范围必须固定。

<a id="L87"></a>
### 第 87 行

```python
            conn.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
```

**语法与数据变化：** 删除本次随机角色。

**为什么与边界：** 不清理其他用户；前面清理失败时此行可能到不了。

<a id="L88"></a>
### 第 88 行

```python
    result = {"postgres": version, "transport": "private Unix socket; TCP disabled", "documents_imported": len(sample)+len(public),
```

**语法与数据变化：** 开始输出真实版本、传输方式和导入数量。

**为什么与边界：** 没有把“用了PG”混同云端托管服务已部署。

<a id="L89"></a>
### 第 89 行

```python
              "synthetic_documents": len(sample), "public_licensed_documents": len(public), "checks": checks,
```

**语法与数据变化：** 分开虚构与授权公开数量，并附检查列表。

**为什么与边界：** 数据来源不同，不应合并后冒充真实企业客户资料。

<a id="L90"></a>
### 第 90 行

```python
              "scope": "documents RLS only; app authentication, tickets RLS and managed cloud DB not certified"}
```

**语法与数据变化：** 明确只验documents RLS，未认证应用、tickets和云库。

**为什么与边界：** 范围声明必须随结果展示。

<a id="L91"></a>
### 第 91 行

```python
    path = ROOT / "artifacts/postgres-validation.json"
```

**语法与数据变化：** 指定忽略目录的实验报告路径。

**为什么与边界：** 当前依赖本地实验产物父目录已存在。

<a id="L92"></a>
### 第 92 行

```python
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
```

**语法与数据变化：** 写JSON报告，覆盖同名旧结果。

**为什么与边界：** 正式历史比较应另存版本，本行未做追加存档。

<a id="L93"></a>
### 第 93 行

```python
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

**语法与数据变化：** 打印同一结果供终端查看。

**为什么与边界：** 仅在整段执行到此时才有报告，不能由源码推断本轮已通过。

<a id="L94"></a>
### 第 94 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L95"></a>
### 第 95 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L96"></a>
### 第 96 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L97"></a>
### 第 97 行

```python
    parser = argparse.ArgumentParser()
```

**语法与数据变化：** 入口创建命令行解析器。

**为什么与边界：** 导入此模块不会跑数据库实验。

<a id="L98"></a>
### 第 98 行

```python
    parser.add_argument("--check-persisted", action="store_true")
```

**语法与数据变化：** store_true注册持久回执检查开关。

**为什么与边界：** 无开关默认执行完整有副作用的run，运行前务必确认环境。

<a id="L99"></a>
### 第 99 行

```python
    args = parser.parse_args()
```

**语法与数据变化：** 解析参数。

**为什么与边界：** 拼错开关会用法错误而非悄悄执行。

<a id="L100"></a>
### 第 100 行

```python
    persisted() if args.check_persisted else run()
```

**语法与数据变化：** 条件表达式只调用persisted或run之一。

**为什么与边界：** persisted不重启服务；没有开关不是dry-run。

## 跟一遍数据与验证边界

alpha只见样例、beta只见公开文档；跨租户INSERT/UPDATE应拒绝；事务结束后身份清空。回执有值本身不能证明本次确已重启，要记录停启过程。

## 只练一个关键点（不是新的学习验收记录）

1. 先阅读run中的创建、写入、finally删除三类语句，核对目标是自有本地socket。
2. 实验条件齐备后才运行；如验证持久性，要实际停启服务器再check-persisted并保留过程。
3. **复盘：** 单独看到persisted_run_count>0能证明刚刚重启过吗？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
