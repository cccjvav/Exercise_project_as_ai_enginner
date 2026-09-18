# 加载器、排序与CLI的离线回归：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tests/test_search.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把1A–1D学到的契约写成可重复断言，避免只用一个正常样例判断程序正确。

### 输入、输出与调用关系

pytest提供临时路径与参数化输入；调用函数和真实Python子进程，失败时报告具体断言。

### 运行与风险边界

`python -m pytest tests/test_search.py -q`，需当前解释器装本项目及test依赖。

只写临时目录、不改真实手册；CLI子进程读取固定公开语料。通过不代表语义检索或生成答案已实现。

## 完整源码

<!-- source: tests/test_search.py -->
```python
#: tmp_path 由 pytest 提供，测试不修改真实语料；每个用例拥有独立临时目录。
import json
import subprocess
import sys
from pathlib import Path
import pytest
from evidencedesk.documents import Document, load_documents
from evidencedesk.search import search

ROOT = Path(__file__).resolve().parents[1]

#: 断言字段而不仅是数量；读取失败、格式错误和空目录应表现不同。
def test_loading(tmp_path):
    (tmp_path / "x.md").write_text("# 中文标题\n\n中文正文\n", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("not a document")
    assert load_documents(tmp_path) == [Document("x", "中文标题", "中文正文", "x.md")]

@pytest.mark.parametrize("content", ["", "无标题\n正文", "# \n正文", "# 标题\n\n"])
def test_invalid_document(tmp_path, content):
    (tmp_path / "bad.md").write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="bad.md"):
        load_documents(tmp_path)

def test_directory_errors(tmp_path):
    assert load_documents(tmp_path) == []
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "missing")
    file = tmp_path / "file"
    file.touch()
    with pytest.raises(NotADirectoryError):
        load_documents(file)

#: 通过人工可算的分数建立 oracle；打乱输入、重复查询词不应改结果。
def test_scores_order_and_no_mutation():
    docs = [Document("z", "Webhook", "重试", "z.md"), Document("a", "Webhook", "重试", "a.md"), Document("b", "重试", "说明", "b.md")]
    original = docs.copy()
    hits = search("WEBHOOK 重试 重试", docs, 10)
    assert [(h.document_id, h.score) for h in hits] == [("a", 1), ("z", 1), ("b", 0.5)]
    assert docs == original
    assert search("webhook 重试", list(reversed(docs)), 10) == hits

@pytest.mark.parametrize("k", [0, -1, True, False, 1.5, "1"])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        search("", [], k)

@pytest.mark.parametrize("query", ["", "   ", "消息没送到还会再发吗？"])
def test_no_terms(query):
    assert search(query, load_documents(ROOT / "data/sample")) == []

#: 子进程检查真实 CLI 行为，而不是只测试内部函数。
def test_cli():
    result = subprocess.run([sys.executable, "-m", "evidencedesk.search", "--query", "Webhook 重试"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)[0]["document_id"] == "webhook-delivery"
    bad = subprocess.run([sys.executable, "-m", "evidencedesk.search", "--query", "x", "--k", "0"], cwd=ROOT, capture_output=True, text=True)
    assert bad.returncode != 0 and not bad.stdout
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: tmp_path 由 pytest 提供，测试不修改真实语料；每个用例拥有独立临时目录。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：tmp_path 由 pytest 提供，测试不修改真实语料；每个用例拥有独立临时目录。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import subprocess
```

**语法与数据变化：** 导入 `subprocess` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库子进程接口。run 可等待外部命令并取得退出码、stdout、stderr；传参数列表与 shell 拼接不同，仍需控制实际调用的程序。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
import sys
```

**语法与数据变化：** 导入 `sys` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 当前 Python 进程信息；executable 可取得解释器路径，argv 是命令行参数，exit 可设置退出状态。它不是新建虚拟环境的工具。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
import pytest
```

**语法与数据变化：** 导入 `pytest` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 测试框架。装饰器展开用例，raises 检查预期异常，fixture 提供隔离资源；测试通过仅覆盖所写的条件。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from evidencedesk.documents import Document, load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `Document, load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
from evidencedesk.search import search
```

**语法与数据变化：** 从 `evidencedesk.search` 导入 `search`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** search用固定领域词覆盖率返回排序的SearchHit候选；不是模型生成或语义检索。权限过滤应在调用之前完成。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L10"></a>
### 第 10 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 以测试文件路径回到仓库根目录。

**为什么与边界：** 子进程和数据定位都用此固定路径，避免从别的终端目录运行时找不到语料。

<a id="L11"></a>
### 第 11 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L12"></a>
### 第 12 行

```python
#: 断言字段而不仅是数量；读取失败、格式错误和空目录应表现不同。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：断言字段而不仅是数量；读取失败、格式错误和空目录应表现不同。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L13"></a>
### 第 13 行

```python
def test_loading(tmp_path):
```

**语法与数据变化：** 定义pytest自动发现的测试，tmp_path按参数名注入。

**为什么与边界：** 不是自己传一个共享目录，每个用例有隔离的临时路径。

<a id="L14"></a>
### 第 14 行

```python
    (tmp_path / "x.md").write_text("# 中文标题\n\n中文正文\n", encoding="utf-8")
```

**语法与数据变化：** 写UTF-8临时Markdown，含标题、空行、正文和末尾换行。

**为什么与边界：** 同时覆盖中文编码与strip后的字段提取，不修改data/sample。

<a id="L15"></a>
### 第 15 行

```python
    (tmp_path / "ignore.txt").write_text("not a document")
```

**语法与数据变化：** 写一个txt干扰文件。

**为什么与边界：** 加载器只接收*.md，若错误读入所有文件，后面的精确列表断言会失败。

<a id="L16"></a>
### 第 16 行

```python
    assert load_documents(tmp_path) == [Document("x", "中文标题", "中文正文", "x.md")]
```

**语法与数据变化：** 对整个Document列表作相等比较。

**为什么与边界：** 检查ID、标题、正文、来源及忽略txt行为；仅断言len=1会漏字段错误。

<a id="L17"></a>
### 第 17 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L18"></a>
### 第 18 行

```python
@pytest.mark.parametrize("content", ["", "无标题\n正文", "# \n正文", "# 标题\n\n"])
```

**语法与数据变化：** 参数化四种坏内容：空文件、无标题标记、空标题、空正文。

**为什么与边界：** pytest分四次运行同一测试，使失败定位到具体输入。

<a id="L19"></a>
### 第 19 行

```python
def test_invalid_document(tmp_path, content):
```

**语法与数据变化：** 接收临时路径和当前content用例。

**为什么与边界：** content来自装饰器，不是读真实坏文件。

<a id="L20"></a>
### 第 20 行

```python
    (tmp_path / "bad.md").write_text(content, encoding="utf-8")
```

**语法与数据变化：** 把当前非法样例写到bad.md。

**为什么与边界：** 相同文件名在各独立临时目录内不会互相污染。

<a id="L21"></a>
### 第 21 行

```python
    with pytest.raises(ValueError, match="bad.md"):
```

**语法与数据变化：** 要求抛ValueError且错误文本包含bad.md。

**为什么与边界：** 若未抛、抛错类型不对或缺定位信息都会失败；match是正则，不是严格整串相等。

<a id="L22"></a>
### 第 22 行

```python
        load_documents(tmp_path)
```

**语法与数据变化：** 在raises上下文内执行加载，触发目标异常。

**为什么与边界：** 待测调用必须缩进在with里，否则无法验证这个异常契约。

<a id="L23"></a>
### 第 23 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L24"></a>
### 第 24 行

```python
def test_directory_errors(tmp_path):
```

**语法与数据变化：** 定义目录边界测试。

**为什么与边界：** 区分空目录、缺路径和给了文件三种情况，而不是全回退空列表。

<a id="L25"></a>
### 第 25 行

```python
    assert load_documents(tmp_path) == []
```

**语法与数据变化：** 真实存在但为空的tmp_path应返回[]。

**为什么与边界：** 这是合法“没有文档”，不应混同读取失败。

<a id="L26"></a>
### 第 26 行

```python
    with pytest.raises(FileNotFoundError):
```

**语法与数据变化：** 要求下一调用抛FileNotFoundError。

**为什么与边界：** 目标路径不存在时应明确失败，不能默默解释为无证据。

<a id="L27"></a>
### 第 27 行

```python
        load_documents(tmp_path / "missing")
```

**语法与数据变化：** 加载未创建的missing子路径。

**为什么与边界：** 构造Path不会建目录，因此它确实不存在。

<a id="L28"></a>
### 第 28 行

```python
    file = tmp_path / "file"
```

**语法与数据变化：** 创建一个待用的普通文件路径对象。

**为什么与边界：** 此行只拼路径，下一行才写文件。

<a id="L29"></a>
### 第 29 行

```python
    file.touch()
```

**语法与数据变化：** touch建立空文件。

**为什么与边界：** 故意提供“存在但不是目录”的反例。

<a id="L30"></a>
### 第 30 行

```python
    with pytest.raises(NotADirectoryError):
```

**语法与数据变化：** 要求NotADirectoryError。

**为什么与边界：** 保护目录类型检查而非内容格式检查。

<a id="L31"></a>
### 第 31 行

```python
        load_documents(file)
```

**语法与数据变化：** 把普通文件传给目录加载器。

**为什么与边界：** 失败应发生在遍历之前，而不是碰巧返回空列表。

<a id="L32"></a>
### 第 32 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L33"></a>
### 第 33 行

```python
#: 通过人工可算的分数建立 oracle；打乱输入、重复查询词不应改结果。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：通过人工可算的分数建立 oracle；打乱输入、重复查询词不应改结果。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L34"></a>
### 第 34 行

```python
def test_scores_order_and_no_mutation():
```

**语法与数据变化：** 定义排序、分数与输入不变性复合回归。

**为什么与边界：** 每条assert检查不同契约，失败应定位哪层语义被破坏。

<a id="L35"></a>
### 第 35 行

```python
    docs = [Document("z", "Webhook", "重试", "z.md"), Document("a", "Webhook", "重试", "a.md"), Document("b", "重试", "说明", "b.md")]
```

**语法与数据变化：** 手写z/a两份完全命中文档和b一份半命中文档，刻意不按ID排序。

**为什么与边界：** 可独立手算预期，不从被测函数再计算“期望值”形成自证循环。

<a id="L36"></a>
### 第 36 行

```python
    original = docs.copy()
```

**语法与数据变化：** 复制外层列表保留原顺序。

**为什么与边界：** 这是浅拷贝，足以查列表重排；Document冻结字段不在本测试中原地修改。

<a id="L37"></a>
### 第 37 行

```python
    hits = search("WEBHOOK 重试 重试", docs, 10)
```

**语法与数据变化：** 查询用大写WEBHOOK与重复重试，k大于候选数。

**为什么与边界：** 一次覆盖大小写归一、去重、k不补造候选。

<a id="L38"></a>
### 第 38 行

```python
    assert [(h.document_id, h.score) for h in hits] == [("a", 1), ("z", 1), ("b", 0.5)]
```

**语法与数据变化：** 投影(ID,score)与精确预期比较。

**为什么与边界：** 两满分按ID a/z排序，半分b在后；重复词不能导致分母错误。

<a id="L39"></a>
### 第 39 行

```python
    assert docs == original
```

**语法与数据变化：** 确认输入列表仍等于原副本。

**为什么与边界：** 发现实现直接对传入docs原地sort的副作用。

<a id="L40"></a>
### 第 40 行

```python
    assert search("webhook 重试", list(reversed(docs)), 10) == hits
```

**语法与数据变化：** 倒序输入再检索应得到同样Hit列表。

**为什么与边界：** 验证排名不依赖输入顺序，而非仅当前顺序碰巧正确。

<a id="L41"></a>
### 第 41 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L42"></a>
### 第 42 行

```python
@pytest.mark.parametrize("k", [0, -1, True, False, 1.5, "1"])
```

**语法与数据变化：** 六种非法k包含布尔、浮点和数字字符串。

**为什么与边界：** bool是int子类，普通isinstance(k,int)可能误放行，测试要求精确整数契约。

<a id="L43"></a>
### 第 43 行

```python
def test_invalid_k(k):
```

**语法与数据变化：** 每次接收一个非法k。

**为什么与边界：** 参数化让每个边界独立报告，不只测试0一种情况。

<a id="L44"></a>
### 第 44 行

```python
    with pytest.raises(ValueError):
```

**语法与数据变化：** 要求ValueError。

**为什么与边界：** 错误应属于公开输入契约，不应泄漏偶然TypeError等实现细节。

<a id="L45"></a>
### 第 45 行

```python
        search("", [], k)
```

**语法与数据变化：** 即便空问题和空语料也要先拒绝非法k。

**为什么与边界：** 保护验证顺序，避免提前return []掩盖错误参数。

<a id="L46"></a>
### 第 46 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L47"></a>
### 第 47 行

```python
@pytest.mark.parametrize("query", ["", "   ", "消息没送到还会再发吗？"])
```

**语法与数据变化：** 三种不提取关键词的输入，包括q06原句。

**为什么与边界：** 这里记录词法局限，不宣称这三题知识库都没有答案。

<a id="L48"></a>
### 第 48 行

```python
def test_no_terms(query):
```

**语法与数据变化：** 参数query注入每个无词输入。

**为什么与边界：** 同一断言用于检查当前词典行为。

<a id="L49"></a>
### 第 49 行

```python
    assert search(query, load_documents(ROOT / "data/sample")) == []
```

**语法与数据变化：** 从固定语料加载并要求空候选。

**为什么与边界：** q06是已知漏召回，不是“安全拒答问题已解决”；更换算法后应有受控更新的回归目标。

<a id="L50"></a>
### 第 50 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L51"></a>
### 第 51 行

```python
#: 子进程检查真实 CLI 行为，而不是只测试内部函数。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：子进程检查真实 CLI 行为，而不是只测试内部函数。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L52"></a>
### 第 52 行

```python
def test_cli():
```

**语法与数据变化：** 定义真实命令行边界测试。

**为什么与边界：** 与直接调用search不同，覆盖模块入口、参数解析和JSON序列化。

<a id="L53"></a>
### 第 53 行

```python
    result = subprocess.run([sys.executable, "-m", "evidencedesk.search", "--query", "Webhook 重试"], cwd=ROOT, capture_output=True, text=True)
```

**语法与数据变化：** 用当前解释器运行模块，设置根目录并捕获文本输出。

**为什么与边界：** 参数列表不经过shell拆分；capture_output把stdout/stderr留给断言。

<a id="L54"></a>
### 第 54 行

```python
    assert result.returncode == 0
```

**语法与数据变化：** 成功请求退出码必须0。

**为什么与边界：** 终端有文字但非零退出不能当成功。

<a id="L55"></a>
### 第 55 行

```python
    assert json.loads(result.stdout)[0]["document_id"] == "webhook-delivery"
```

**语法与数据变化：** 解析stdout JSON并检查首条业务文档ID。

**为什么与边界：** 若输出混入调试print或给错文档，此处失败。

<a id="L56"></a>
### 第 56 行

```python
    bad = subprocess.run([sys.executable, "-m", "evidencedesk.search", "--query", "x", "--k", "0"], cwd=ROOT, capture_output=True, text=True)
```

**语法与数据变化：** 另起进程传--k 0非法参数。

**为什么与边界：** 这测的是CLI错误路径，不是只测试内部ValueError。

<a id="L57"></a>
### 第 57 行

```python
    assert bad.returncode != 0 and not bad.stdout
```

**语法与数据变化：** 要求非零退出且stdout为空。

**为什么与边界：** 避免把错误混入成功JSON通道；本断言未精确核对stderr内容，不能声称覆盖所有错误文案。

## 跟一遍数据与验证边界

分数用手算oracle：a/z各覆盖两词得1，b只覆盖重试得0.5；输入倒序后结果仍按分数、ID排序。

## 只练一个关键点（不是新的学习验收记录）

1. 只运行 python -m pytest tests/test_search.py -k invalid_k -q，观察参数化用例数。
2. 如做变异实验，先备份search.py，只把精确int判断改为isinstance，运行同组测试，再立即恢复并重跑；不得留下变异提交。
3. **复盘：** 失败的是哪种Python子类边界，而不是哪条检索题？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
