# 评测、分块、融合、写工具与记忆的回归：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tests/test_core.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

逐项固定核心功能的输入输出与安全边界，尤其区分审批失败、幂等冲突和持久化。

### 输入、输出与调用关系

参数化测试与临时SQLite文件，直接调用内部函数；不需要模型服务。

### 运行与风险边界

`python -m pytest tests/test_core.py -q`，安装test依赖即可。

本地临时数据库不是PostgreSQL/RLS测试；Memory只在内存，测试通过不代表生产授权完备。

## 完整源码

<!-- source: tests/test_core.py -->
```python
import json
import sqlite3
from dataclasses import replace
from pathlib import Path
import pytest
from evidencedesk.documents import Document, load_documents
from evidencedesk.evaluate import evaluate
from evidencedesk.ingest import chunks, replace_document
from evidencedesk.hybrid import bm25, rrf, expand_parents
from evidencedesk.tickets import Approval, payload_hash, submit
from evidencedesk.memory import PreferenceMemory

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("k", [1, 3])
def test_baseline(k):
    rows = [json.loads(line) for line in (ROOT / "data/questions.jsonl").read_text().splitlines()]
    result = evaluate(rows, load_documents(ROOT / "data/sample"), k)
    assert result["recall"] == pytest.approx(5 / 6)
    assert result["mrr"] == pytest.approx(5 / 6)
    assert result["unanswerable_empty_rate"] == 1
    assert result["details"][5]["retrieved"] == []

def test_empty_metrics():
    assert evaluate([], [], 1)["recall"] is None
    row = {"id": "none", "question": "未知", "answerable": False, "relevant_document_ids": []}
    assert evaluate([row], [], 1)["mrr"] is None
    with pytest.raises(ValueError):
        evaluate([row, row], [], 1)

@pytest.mark.parametrize("size,overlap", [(0, 0), (20, 20), (20, -1), (True, 0), (1.2, 0)])
def test_invalid_chunks(size, overlap):
    with pytest.raises(ValueError):
        chunks(Document("x", "title", "body", "x.md"), size, overlap)

def test_chunk_coverage_and_versions():
    doc = Document("x", "title", "0123456789" * 40, "x.md")
    parts = chunks(doc, 120, 20)
    positions = set()
    for part in parts:
        assert part["text"] == doc.text[part["start"]:part["end"]]
        positions.update(range(part["start"], part["end"]))
    assert positions == set(range(len(doc.text)))
    index = replace_document({}, doc)
    assert replace_document(index, doc) == index
    changed = replace_document(index, replace(doc, text="short changed text"))
    assert set(index).isdisjoint(changed)
    assert len(changed) == 1

def test_hybrid():
    assert bm25(["a"], {"x": ["a", "a"], "y": ["b"]})[0][0] == "x"
    assert bm25(["a"], {"x": []}) == []
    assert bm25(["a"], {"empty": [], "match": ["a"]}, b=1)[0][0] == "match"
    assert rrf([["a", "a"], ["b", "a"]]) == rrf([["a"], ["b", "a"]])
    assert rrf([["a"], ["b", "a"]])[0][0] == "a"
    assert expand_parents(["a", "b"], {"a": "p", "b": "p"}) == ["p"]

def test_tickets():
    conn = sqlite3.connect(":memory:")
    payload = {"title": "Test", "priority": "P1"}
    approval = Approval("alpha", "alice", payload_hash(payload))
    with pytest.raises(PermissionError):
        submit(conn, "alpha", "alice", "id-1", payload, None)
    with pytest.raises(PermissionError):
        submit(conn, "beta", "alice", "id-1", payload, approval)
    first = submit(conn, "alpha", "alice", "id-1", payload, approval)
    assert first == submit(conn, "alpha", "alice", "id-1", payload, approval)
    edited = {**payload, "title": "changed"}
    with pytest.raises(PermissionError):
        submit(conn, "alpha", "alice", "id-1", edited, approval)
    with pytest.raises(ValueError):
        submit(conn, "alpha", "alice", "id-1", edited, Approval("alpha", "alice", payload_hash(edited)))
    assert conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 1
    conn.close()

def test_ticket_persistence(tmp_path):
    db = tmp_path / "tickets.db"
    payload = {"title": "Test", "priority": "P3"}
    approval = Approval("a", "u", payload_hash(payload))
    with sqlite3.connect(db) as conn:
        first = submit(conn, "a", "u", "r", payload, approval)
    with sqlite3.connect(db) as conn:
        assert submit(conn, "a", "u", "r", payload, approval) == first

def test_memory():
    memory = PreferenceMemory()
    with pytest.raises(PermissionError):
        memory.save("a", "u", "zh-CN", False, 0, 30)
    memory.save("a", "u", "zh-CN", True, 0, 30)
    assert memory.get("a", "u", 29) == "zh-CN"
    assert memory.get("b", "u", 1) is None
    assert memory.get("a", "other", 1) is None
    assert memory.get("a", "u", 30) is None
    memory.save("a", "u", "en", True, 40, 30)
    memory.forget("a", "u")
    assert memory.get("a", "u", 41) is None
    assert PreferenceMemory().records == {}
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L2"></a>
### 第 2 行

```python
import sqlite3
```

**语法与数据变化：** 导入 `sqlite3` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 SQLite 客户端。connect 打开数据库，execute 执行 SQL；内存连接仅活到该连接结束，文件连接可在关闭后保留数据。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
from dataclasses import replace
```

**语法与数据变化：** 导入dataclasses.replace以创建只改正文的新Document。

**为什么与边界：** 不是原地修改frozen对象，保持旧版本作比较。

<a id="L4"></a>
### 第 4 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
import pytest
```

**语法与数据变化：** 导入 `pytest` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 测试框架。装饰器展开用例，raises 检查预期异常，fixture 提供隔离资源；测试通过仅覆盖所写的条件。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from evidencedesk.documents import Document, load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `Document, load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from evidencedesk.evaluate import evaluate
```

**语法与数据变化：** 从 `evidencedesk.evaluate` 导入 `evaluate`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** evaluate按固定标注分组计算Recall、MRR与无答案空返回率，保留每题结果；gold不传给检索器。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
from evidencedesk.ingest import chunks, replace_document
```

**语法与数据变化：** 从 `evidencedesk.ingest` 导入 `chunks, replace_document`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** chunks生成含父ID、版本和字符偏移的块；replace_document返回替换该父文档后的新索引字典，不自动持久化。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

```python
from evidencedesk.hybrid import bm25, rrf, expand_parents
```

**语法与数据变化：** 从 `evidencedesk.hybrid` 导入 `bm25, rrf, expand_parents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** bm25按词频及文档频率评分；rrf按榜单位置融合；expand_parents将子ID映射到父ID并去重，三者都不是在线模型调用。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L10"></a>
### 第 10 行

```python
from evidencedesk.tickets import Approval, payload_hash, submit
```

**语法与数据变化：** 从 `evidencedesk.tickets` 导入 `Approval, payload_hash, submit`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Approval绑定身份与草稿摘要；payload_hash规范化内容；submit在可信审批成立后做SQLite幂等写入，未接真实工单系统。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L11"></a>
### 第 11 行

```python
from evidencedesk.memory import PreferenceMemory
```

**语法与数据变化：** 从 `evidencedesk.memory` 导入 `PreferenceMemory`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** PreferenceMemory按租户与用户保存有限语言偏好；明确同意、截止时间与删除由方法实施，存储仅在内存。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 从测试文件定位仓库根目录。

**为什么与边界：** 数据路径与调用目录解耦，但仍依赖固定样例存在。

<a id="L14"></a>
### 第 14 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L15"></a>
### 第 15 行

```python
@pytest.mark.parametrize("k", [1, 3])
```

**语法与数据变化：** 对k=1和k=3分别执行基线测试。

**为什么与边界：** 参数变化而指标相同反映此固定数据，不是“所有任务k都没用”。

<a id="L16"></a>
### 第 16 行

```python
def test_baseline(k):
```

**语法与数据变化：** 接收当前k，验证公开八题基线。

**为什么与边界：** 不是九题跨阶段回归集，样本人口需区分。

<a id="L17"></a>
### 第 17 行

```python
    rows = [json.loads(line) for line in (ROOT / "data/questions.jsonl").read_text().splitlines()]
```

**语法与数据变化：** 读取原data/questions.jsonl，每行解码一个字典。

**为什么与边界：** 本行未显式encoding、也未滤空白行，依赖本环境UTF-8与题集格式；不应复制为通用容错读取器。

<a id="L18"></a>
### 第 18 行

```python
    result = evaluate(rows, load_documents(ROOT / "data/sample"), k)
```

**语法与数据变化：** 把行列表、真实样例文档和k交给评测器。

**为什么与边界：** 题目标注只供评测，不作为search输入。

<a id="L19"></a>
### 第 19 行

```python
    assert result["recall"] == pytest.approx(5 / 6)
```

**语法与数据变化：** 要求宏Recall约等于5/6。

**为什么与边界：** pytest.approx处理浮点误差，分母是六条可回答题，漏题贡献0。

<a id="L20"></a>
### 第 20 行

```python
    assert result["mrr"] == pytest.approx(5 / 6)
```

**语法与数据变化：** MRR也要求5/6。

**为什么与边界：** 说明五条命中首位、一条未命中；不能由Recall自动推导所有数据上MRR相等。

<a id="L21"></a>
### 第 21 行

```python
    assert result["unanswerable_empty_rate"] == 1
```

**语法与数据变化：** 原八题的无答案组空返回率为1。

**为什么与边界：** 新增q09后应变2/3，因此本断言不是“所有无答案问题都会空返回”。

<a id="L22"></a>
### 第 22 行

```python
    assert result["details"][5]["retrieved"] == []
```

**语法与数据变化：** 第六行题的retrieved应为空，锁定q06基线漏召回。

**为什么与边界：** 依赖题目顺序；没有按ID查找，修改题集顺序要同步理解测试，不可偷改算法掩盖它。

<a id="L23"></a>
### 第 23 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L24"></a>
### 第 24 行

```python
def test_empty_metrics():
```

**语法与数据变化：** 验证缺少指标人口与重复ID输入。

**为什么与边界：** None用于未定义，不应伪造成0或满分。

<a id="L25"></a>
### 第 25 行

```python
    assert evaluate([], [], 1)["recall"] is None
```

**语法与数据变化：** 无题无文档时Recall为None。

**为什么与边界：** 没有可回答题就没有Recall分母，不等同系统零分。

<a id="L26"></a>
### 第 26 行

```python
    row = {"id": "none", "question": "未知", "answerable": False, "relevant_document_ids": []}
```

**语法与数据变化：** 构造唯一无答案题，gold为空。

**为什么与边界：** 符合评测契约，用来隔离“缺可回答组”的行为。

<a id="L27"></a>
### 第 27 行

```python
    assert evaluate([row], [], 1)["mrr"] is None
```

**语法与数据变化：** 只含无答案题时MRR仍为None。

**为什么与边界：** 无答案题不能被混进可回答组均值。

<a id="L28"></a>
### 第 28 行

```python
    with pytest.raises(ValueError):
```

**语法与数据变化：** 要求重复输入行触发ValueError。

**为什么与边界：** 重复题ID会污染样本统计，应在计算前拒绝。

<a id="L29"></a>
### 第 29 行

```python
        evaluate([row, row], [], 1)
```

**语法与数据变化：** 把同一题放两次送入评测器。

**为什么与边界：** 不是两条独立样本，只是重复身份，故应报错。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

```python
@pytest.mark.parametrize("size,overlap", [(0, 0), (20, 20), (20, -1), (True, 0), (1.2, 0)])
```

**语法与数据变化：** 参数化无效size/overlap组合，含步长0、负重叠、bool和浮点。

**为什么与边界：** 覆盖值域和精确整数类型，避免range错误被推迟到内部。

<a id="L32"></a>
### 第 32 行

```python
def test_invalid_chunks(size, overlap):
```

**语法与数据变化：** 接收当前窗口参数对。

**为什么与边界：** 每个组合是独立用例，不能只看五组总共“没有崩溃”。

<a id="L33"></a>
### 第 33 行

```python
    with pytest.raises(ValueError):
```

**语法与数据变化：** 要求明确ValueError。

**为什么与边界：** 这是分块接口契约，不能期待range自己偶然报错。

<a id="L34"></a>
### 第 34 行

```python
        chunks(Document("x", "title", "body", "x.md"), size, overlap)
```

**语法与数据变化：** 用短Document调用chunks，参数位置对应size、overlap。

**为什么与边界：** 正文合法，所以失败原因聚焦窗口参数。

<a id="L35"></a>
### 第 35 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L36"></a>
### 第 36 行

```python
def test_chunk_coverage_and_versions():
```

**语法与数据变化：** 验证字符覆盖、定位、重复导入与正文变更。

**为什么与边界：** 这些是可追溯分块的不同维度，不由一个块数断言代替。

<a id="L37"></a>
### 第 37 行

```python
    doc = Document("x", "title", "0123456789" * 40, "x.md")
```

**语法与数据变化：** 构造400字符可预测正文。

**为什么与边界：** 重复数字便于长度控制，但重复内容不能代替块位置身份。

<a id="L38"></a>
### 第 38 行

```python
    parts = chunks(doc, 120, 20)
```

**语法与数据变化：** size120、overlap20意味着步长100。

**为什么与边界：** 末块可能短于窗口，上限是字符数不是token数。

<a id="L39"></a>
### 第 39 行

```python
    positions = set()
```

**语法与数据变化：** 创建空集合累计被覆盖的字符位置。

**为什么与边界：** 集合去重，使重叠位置不会把覆盖统计虚增。

<a id="L40"></a>
### 第 40 行

```python
    for part in parts:
```

**语法与数据变化：** 遍历每个块字典。

**为什么与边界：** 每块的start/end相对原Document.text，不是磁盘字节偏移。

<a id="L41"></a>
### 第 41 行

```python
        assert part["text"] == doc.text[part["start"]:part["end"]]
```

**语法与数据变化：** 块text必须等于原文半开区间切片。

**为什么与边界：** 能发现元数据偏移与实际正文不一致，单看块长度发现不了。

<a id="L42"></a>
### 第 42 行

```python
        positions.update(range(part["start"], part["end"]))
```

**语法与数据变化：** 把start到end前一位的所有位置加入集合。

**为什么与边界：** range不含end，与Python切片约定一致。

<a id="L43"></a>
### 第 43 行

```python
    assert positions == set(range(len(doc.text)))
```

**语法与数据变化：** 覆盖集合必须恰好等于正文所有字符位置。

**为什么与边界：** 可发现漏字符或越界位置，但没有单独证明重复量最优。

<a id="L44"></a>
### 第 44 行

```python
    index = replace_document({}, doc)
```

**语法与数据变化：** 从空索引导入默认分块。

**为什么与边界：** 与上面指定参数例子分开，默认仍是120/20。

<a id="L45"></a>
### 第 45 行

```python
    assert replace_document(index, doc) == index
```

**语法与数据变化：** 相同文档重复导入后整个字典相等。

**为什么与边界：** 检查幂等内容及ID，不只是字典长度没增长。

<a id="L46"></a>
### 第 46 行

```python
    changed = replace_document(index, replace(doc, text="short changed text"))
```

**语法与数据变化：** 用replace构造短新正文并替换旧索引。

**为什么与边界：** 父ID保持，版本改变；原Document不变。

<a id="L47"></a>
### 第 47 行

```python
    assert set(index).isdisjoint(changed)
```

**语法与数据变化：** 新旧块ID集合不相交。

**为什么与边界：** 此索引仅含当前文档，所以全体旧块都应该移除；多文档索引不能照搬整集合断言。

<a id="L48"></a>
### 第 48 行

```python
    assert len(changed) == 1
```

**语法与数据变化：** 新短正文应只生成一块。

**为什么与边界：** 同时防止旧块残留和无必要尾块。

<a id="L49"></a>
### 第 49 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L50"></a>
### 第 50 行

```python
def test_hybrid():
```

**语法与数据变化：** 用可手算输入验证BM25、RRF和父级映射。

**为什么与边界：** 固定fixture测机制，不测真实语义模型效果。

<a id="L51"></a>
### 第 51 行

```python
    assert bm25(["a"], {"x": ["a", "a"], "y": ["b"]})[0][0] == "x"
```

**语法与数据变化：** x有查询词a两次，y没有，要求首名ID为x。

**为什么与边界：** [0][0]分别取第一条排名和其中ID，不是得分。

<a id="L52"></a>
### 第 52 行

```python
    assert bm25(["a"], {"x": []}) == []
```

**语法与数据变化：** 语料所有文档为空时BM25应返回[]。

**为什么与边界：** 保护平均长度为0的分支，避免除零或伪命中。

<a id="L53"></a>
### 第 53 行

```python
    assert bm25(["a"], {"empty": [], "match": ["a"]}, b=1)[0][0] == "match"
```

**语法与数据变化：** 存在空文档且b=1时仍应得到match。

**为什么与边界：** 覆盖长度归一化极端参数，空文档应跳过，不因0分母破坏有词文档。

<a id="L54"></a>
### 第 54 行

```python
    assert rrf([["a", "a"], ["b", "a"]]) == rrf([["a"], ["b", "a"]])
```

**语法与数据变化：** 单榜重复a不应额外贡献分数。

**为什么与边界：** 比较两次RRF完整输出，保护榜内去重，同时允许跨榜累计。

<a id="L55"></a>
### 第 55 行

```python
    assert rrf([["a"], ["b", "a"]])[0][0] == "a"
```

**语法与数据变化：** a得到两榜支持后应排第一。

**为什么与边界：** 验证融合机制，不证明所有真实任务都优于单路检索。

<a id="L56"></a>
### 第 56 行

```python
    assert expand_parents(["a", "b"], {"a": "p", "b": "p"}) == ["p"]
```

**语法与数据变化：** 两子块同父应只返回一个p。

**为什么与边界：** 防止上下文重复膨胀；还没涉及读取父正文或权限。

<a id="L57"></a>
### 第 57 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L58"></a>
### 第 58 行

```python
def test_tickets():
```

**语法与数据变化：** 验证审批拒绝、内容绑定、幂等及唯一记录数。

**为什么与边界：** 测试对象是SQLite教学实现，不是外部工单平台。

<a id="L59"></a>
### 第 59 行

```python
    conn = sqlite3.connect(":memory:")
```

**语法与数据变化：** 创建独立内存连接。

**为什么与边界：** 每个测试从空数据开始，不依赖其他用例留下记录。

<a id="L60"></a>
### 第 60 行

```python
    payload = {"title": "Test", "priority": "P1"}
```

**语法与数据变化：** 构造合法Test/P1草稿。

**为什么与边界：** 非法字段不在这个用例覆盖范围内。

<a id="L61"></a>
### 第 61 行

```python
    approval = Approval("alpha", "alice", payload_hash(payload))
```

**语法与数据变化：** 审批绑定alpha、alice和当前payload摘要。

**为什么与边界：** 同意的是具体内容，不是未来任何草稿。

<a id="L62"></a>
### 第 62 行

```python
    with pytest.raises(PermissionError):
```

**语法与数据变化：** 要求缺少审批触发PermissionError。

**为什么与边界：** 与普通参数ValueError不同，拒绝属于授权前置条件。

<a id="L63"></a>
### 第 63 行

```python
        submit(conn, "alpha", "alice", "id-1", payload, None)
```

**语法与数据变化：** 传None审批执行待测提交。

**为什么与边界：** 如果函数误允许写，raises本身会令测试失败，优于仅try/except打印。

<a id="L64"></a>
### 第 64 行

```python
    with pytest.raises(PermissionError):
```

**语法与数据变化：** 要求下一次跨租户审批复用也被拒绝。

**为什么与边界：** 同用户名不能突破tenant边界。

<a id="L65"></a>
### 第 65 行

```python
        submit(conn, "beta", "alice", "id-1", payload, approval)
```

**语法与数据变化：** 把alpha审批用于beta请求，制造明确身份不匹配。

**为什么与边界：** 失败必须发生在写入之前。

<a id="L66"></a>
### 第 66 行

```python
    first = submit(conn, "alpha", "alice", "id-1", payload, approval)
```

**语法与数据变化：** 合法审批和身份完成首次提交，保存first ID。

**为什么与边界：** 随后重试应返回数据库已存在身份。

<a id="L67"></a>
### 第 67 行

```python
    assert first == submit(conn, "alpha", "alice", "id-1", payload, approval)
```

**语法与数据变化：** 相同key/内容重试必须等于first。

**为什么与边界：** 发现每次都新建UUID并回传的错误幂等实现。

<a id="L68"></a>
### 第 68 行

```python
    edited = {**payload, "title": "changed"}
```

**语法与数据变化：** 字典展开复制payload，再覆盖title生成edited。

**为什么与边界：** 原草稿保留，便于区分旧审批对应内容与新内容。

<a id="L69"></a>
### 第 69 行

```python
    with pytest.raises(PermissionError):
```

**语法与数据变化：** 要求旧审批不能授权新草稿。

**为什么与边界：** 防止审批与执行之间内容被替换。

<a id="L70"></a>
### 第 70 行

```python
        submit(conn, "alpha", "alice", "id-1", edited, approval)
```

**语法与数据变化：** 使用edited却仍传旧approval，触发摘要不符。

**为什么与边界：** 这是权限错误，不是下面同key冲突的用例。

<a id="L71"></a>
### 第 71 行

```python
    with pytest.raises(ValueError):
```

**语法与数据变化：** 要求已重新批准的不同内容复用旧key时ValueError。

**为什么与边界：** 审批通过不意味着可以把同请求ID悄悄绑定另一业务操作。

<a id="L72"></a>
### 第 72 行

```python
        submit(conn, "alpha", "alice", "id-1", edited, Approval("alpha", "alice", payload_hash(edited)))
```

**语法与数据变化：** 为edited生成匹配的新审批，但仍使用id-1。

**为什么与边界：** 让测试越过审批层到达幂等冲突检查，分层验证拒绝原因。

<a id="L73"></a>
### 第 73 行

```python
    assert conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 1
```

**语法与数据变化：** 直接查库要求仍只有一行。

**为什么与边界：** 防止前面虽然返回同ID/报错，却已经偷偷插入重复记录。

<a id="L74"></a>
### 第 74 行

```python
    conn.close()
```

**语法与数据变化：** 关闭连接，清理内存数据库。

**为什么与边界：** 实际文件持久化交给下一个测试。

<a id="L75"></a>
### 第 75 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L76"></a>
### 第 76 行

```python
def test_ticket_persistence(tmp_path):
```

**语法与数据变化：** 使用pytest临时路径验证文件数据库跨连接读取。

**为什么与边界：** 不是重启整个进程或测试机器灾备。

<a id="L77"></a>
### 第 77 行

```python
    db = tmp_path / "tickets.db"
```

**语法与数据变化：** 创建临时数据库路径对象。

**为什么与边界：** 连接时才创建文件，测试结束由tmp_path管理产物。

<a id="L78"></a>
### 第 78 行

```python
    payload = {"title": "Test", "priority": "P3"}
```

**语法与数据变化：** 换合法P3草稿覆盖另一允许优先级。

**为什么与边界：** 不证明所有未知优先级都被拒绝，需另写负例。

<a id="L79"></a>
### 第 79 行

```python
    approval = Approval("a", "u", payload_hash(payload))
```

**语法与数据变化：** 审批绑定a/u和该P3内容。

**为什么与边界：** 用短标识减少噪声，仍遵守相同身份约束。

<a id="L80"></a>
### 第 80 行

```python
    with sqlite3.connect(db) as conn:
```

**语法与数据变化：** 打开文件SQLite连接并进入事务上下文。

**为什么与边界：** sqlite3的with管理提交/回滚，不保证退出时close，不能把它解释为文件自动关闭管理器。

<a id="L81"></a>
### 第 81 行

```python
        first = submit(conn, "a", "u", "r", payload, approval)
```

**语法与数据变化：** 首次提交并保留ID。

**为什么与边界：** 文件内容成为下一连接的读取对象。

<a id="L82"></a>
### 第 82 行

```python
    with sqlite3.connect(db) as conn:
```

**语法与数据变化：** 再次新建连接到同一个文件。

**为什么与边界：** 验证跨连接可见性，不依赖同一个内存连接的缓存。

<a id="L83"></a>
### 第 83 行

```python
        assert submit(conn, "a", "u", "r", payload, approval) == first
```

**语法与数据变化：** 同请求应返回原ID。

**为什么与边界：** 说明持久记录参与幂等判断；不证明进程重启/并发/网络故障都已覆盖。

<a id="L84"></a>
### 第 84 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L85"></a>
### 第 85 行

```python
def test_memory():
```

**语法与数据变化：** 覆盖偏好同意、租户/用户隔离、到期边界和删除。

**为什么与边界：** 各断言对应独立隐私契约。

<a id="L86"></a>
### 第 86 行

```python
    memory = PreferenceMemory()
```

**语法与数据变化：** 创建新PreferenceMemory。

**为什么与边界：** 存储仅此对象内存，没有加载数据库记录。

<a id="L87"></a>
### 第 87 行

```python
    with pytest.raises(PermissionError):
```

**语法与数据变化：** 未同意保存应抛PermissionError。

**为什么与边界：** 不能默认收集用户偏好再事后请求同意。

<a id="L88"></a>
### 第 88 行

```python
        memory.save("a", "u", "zh-CN", False, 0, 30)
```

**语法与数据变化：** False同意、合法语言和TTL，聚焦同意保护。

**为什么与边界：** 失败不应被非法语言等其他原因误触发。

<a id="L89"></a>
### 第 89 行

```python
    memory.save("a", "u", "zh-CN", True, 0, 30)
```

**语法与数据变化：** 明确True后保存，时间0、TTL30。

**为什么与边界：** 建立有效记录供读取边界检查。

<a id="L90"></a>
### 第 90 行

```python
    assert memory.get("a", "u", 29) == "zh-CN"
```

**语法与数据变化：** 29时尚未到期，应读取zh-CN。

**为什么与边界：** 精确比较防止错误语言通过“非空”检查。

<a id="L91"></a>
### 第 91 行

```python
    assert memory.get("b", "u", 1) is None
```

**语法与数据变化：** 相同用户、不同租户不可读。

**为什么与边界：** 验证联合身份第一维。

<a id="L92"></a>
### 第 92 行

```python
    assert memory.get("a", "other", 1) is None
```

**语法与数据变化：** 相同租户、不同用户也不可读。

**为什么与边界：** 独立验证第二维，而非同时换两个维度模糊归因。

<a id="L93"></a>
### 第 93 行

```python
    assert memory.get("a", "u", 30) is None
```

**语法与数据变化：** 恰好30要求过期。

**为什么与边界：** 捕获>=误写>的边界错误。

<a id="L94"></a>
### 第 94 行

```python
    memory.save("a", "u", "en", True, 40, 30)
```

**语法与数据变化：** 40时重新保存en，生成新有效期。

**为什么与边界：** 旧记录过期不应永久禁止用户重新同意。

<a id="L95"></a>
### 第 95 行

```python
    memory.forget("a", "u")
```

**语法与数据变化：** 明确调用forget删除。

**为什么与边界：** 与自然过期分开测试撤回行为。

<a id="L96"></a>
### 第 96 行

```python
    assert memory.get("a", "u", 41) is None
```

**语法与数据变化：** 41未到期却读不到，证明删除接口生效。

**为什么与边界：** 不是靠TTL碰巧到期才返回None。

<a id="L97"></a>
### 第 97 行

```python
    assert PreferenceMemory().records == {}
```

**语法与数据变化：** 另一新实例必须拥有空records。

**为什么与边界：** 防止类级共享可变默认字典造成跨实例泄漏。

## 跟一遍数据与验证边界

修改>=到>会让过期边界失败；漏掉payload摘要绑定会让审批变更测试失败；重复请求新建记录会让数量断言失败。

## 只练一个关键点（不是新的学习验收记录）

1. 按-k分别运行baseline、chunk、tickets、memory，观察每组覆盖目标。
2. 只选择一个边界做纸面变异预测，再对照对应assert；不要一口气修改多个模块。
3. **复盘：** 为什么指标人口None、审批PermissionError、幂等ValueError不能混用？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
