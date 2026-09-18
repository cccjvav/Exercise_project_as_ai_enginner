# 可选依赖的本地集成测试：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tests/test_integrations.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

区分缺包跳过、真实本地库调用成功与外部模型未验证。

### 输入、输出与调用关系

探测可选模块，运行Qdrant/MCP子进程、LangGraph暂停恢复、PDF写读。

### 运行与风险边界

`python -m pytest tests/test_integrations.py -q -rs`；-rs显示跳过原因。需要对应可选依赖，PDF脚本也导入tiktoken。

不调用模型服务。Qdrant和MCP不是伪造返回；PDF编码表在本空页用例中会于加载前报错，因此本测试不证明token表下载成功。

## 完整源码

<!-- source: tests/test_integrations.py -->
```python
import importlib.util
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.skipif(importlib.util.find_spec("qdrant_client") is None, reason="optional vector extra")
def test_qdrant():
    result = subprocess.run([sys.executable, "-m", "examples.vector_geometry"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

@pytest.mark.skipif(importlib.util.find_spec("langgraph") is None, reason="optional workflow extra")
@pytest.mark.parametrize("decision,expected", [(True, "ready_for_authorized_tool"), (False, "rejected"), ("true", "rejected")])
def test_graph(decision, expected):
    from examples.approval_graph import build_graph
    from langgraph.types import Command
    graph = build_graph()
    config = {"configurable": {"thread_id": "test:actor:1"}}
    result = graph.invoke({"draft": "draft", "approved": False, "status": "draft"}, config)
    assert "__interrupt__" in result
    assert graph.invoke(Command(resume=decision), config)["status"] == expected

@pytest.mark.skipif(importlib.util.find_spec("mcp") is None, reason="optional MCP extra")
def test_mcp():
    result = subprocess.run([sys.executable, "-m", "examples.mcp_client"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "webhook-delivery" in result.stdout

@pytest.mark.skipif(importlib.util.find_spec("pypdf") is None, reason="optional ingest extra")
def test_pdf_fixture_and_empty_page(tmp_path):
    from pypdf import PdfReader, PdfWriter
    from examples.make_demo_pdf import main
    import os
    previous = Path.cwd()
    try:
        os.chdir(tmp_path)
        main()
        assert "Webhook retries: 3." in PdfReader("artifacts/demo.pdf").pages[0].extract_text()
    finally:
        os.chdir(previous)
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    target = tmp_path / "blank.pdf"
    with target.open("wb") as handle:
        writer.write(handle)
    result = subprocess.run([sys.executable, "-m", "examples.pdf_tokens", str(target)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0 and "无文本层" in result.stderr
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
import importlib.util
```

**语法与数据变化：** 导入 `importlib.util` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 模块发现接口。find_spec探测模块是否可找到，用于跳过缺少可选依赖的测试；找得到并不证明版本兼容或外部服务正常。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L2"></a>
### 第 2 行

```python
import subprocess
```

**语法与数据变化：** 导入 `subprocess` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库子进程接口。run 可等待外部命令并取得退出码、stdout、stderr；传参数列表与 shell 拼接不同，仍需控制实际调用的程序。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import sys
```

**语法与数据变化：** 导入 `sys` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 当前 Python 进程信息；executable 可取得解释器路径，argv 是命令行参数，exit 可设置退出状态。它不是新建虚拟环境的工具。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

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

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 从测试路径推导仓库根目录。

**为什么与边界：** 子进程cwd固定，避免相对语料路径漂移。

<a id="L8"></a>
### 第 8 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L9"></a>
### 第 9 行

```python
@pytest.mark.skipif(importlib.util.find_spec("qdrant_client") is None, reason="optional vector extra")
```

**语法与数据变化：** qdrant_client不可发现时跳过此测试并说明原因。

**为什么与边界：** skip不是pass，也不是模拟Qdrant已运行。

<a id="L10"></a>
### 第 10 行

```python
def test_qdrant():
```

**语法与数据变化：** 定义向量几何集成用例。

**为什么与边界：** 内部示例含自己的断言，测试在真实子进程检查退出。

<a id="L11"></a>
### 第 11 行

```python
    result = subprocess.run([sys.executable, "-m", "examples.vector_geometry"], cwd=ROOT, capture_output=True, text=True)
```

**语法与数据变化：** 当前解释器运行vector_geometry，捕获stdout/stderr。

**为什么与边界：** 调用真实本地内存Qdrant，但向量仍是手写fixture；这里未设timeout。

<a id="L12"></a>
### 第 12 行

```python
    assert result.returncode == 0, result.stderr
```

**语法与数据变化：** 要求退出0，失败时把stderr作为断言说明。

**为什么与边界：** 可暴露依赖版本/API错误，不只看控制台有输出。

<a id="L13"></a>
### 第 13 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L14"></a>
### 第 14 行

```python
@pytest.mark.skipif(importlib.util.find_spec("langgraph") is None, reason="optional workflow extra")
```

**语法与数据变化：** 缺LangGraph就跳过该参数化测试。

**为什么与边界：** 模块可找到也未必兼容，实际执行仍可能失败。

<a id="L15"></a>
### 第 15 行

```python
@pytest.mark.parametrize("decision,expected", [(True, "ready_for_authorized_tool"), (False, "rejected"), ("true", "rejected")])
```

**语法与数据变化：** True→ready、False→rejected、字符串true→rejected三组输入。

**为什么与边界：** 保护“明确布尔同意”而非truthy字符串放行。

<a id="L16"></a>
### 第 16 行

```python
def test_graph(decision, expected):
```

**语法与数据变化：** 接收当前决定和期望状态。

**为什么与边界：** 参数化会分别运行三次图流程。

<a id="L17"></a>
### 第 17 行

```python
    from examples.approval_graph import build_graph
```

**语法与数据变化：** 在测试体内导入build_graph。

**为什么与边界：** 延迟到skip判定后，避免缺可选包时收集整个测试文件就失败。

<a id="L18"></a>
### 第 18 行

```python
    from langgraph.types import Command
```

**语法与数据变化：** 导入恢复命令Command。

**为什么与边界：** 它只承载恢复值，不验证是谁批准。

<a id="L19"></a>
### 第 19 行

```python
    graph = build_graph()
```

**语法与数据变化：** 构造新的图和内存检查点。

**为什么与边界：** 每个参数用例相互独立，避免复用先前审批状态。

<a id="L20"></a>
### 第 20 行

```python
    config = {"configurable": {"thread_id": "test:actor:1"}}
```

**语法与数据变化：** 设置固定测试thread_id。

**为什么与边界：** 仅测试关联流程，不代表用户认证已实现。

<a id="L21"></a>
### 第 21 行

```python
    result = graph.invoke({"draft": "draft", "approved": False, "status": "draft"}, config)
```

**语法与数据变化：** 用未批准初始状态启动图。

**为什么与边界：** 下一断言确认真正停在中断点，而不是已经路由完成。

<a id="L22"></a>
### 第 22 行

```python
    assert "__interrupt__" in result
```

**语法与数据变化：** 要求返回包含__interrupt__。

**为什么与边界：** 保护人工等待边界，若review未暂停应失败。

<a id="L23"></a>
### 第 23 行

```python
    assert graph.invoke(Command(resume=decision), config)["status"] == expected
```

**语法与数据变化：** 同配置恢复并比较目标状态。

**为什么与边界：** 既验证检查点恢复，也验证严格布尔判断，不是仅调用route函数。

<a id="L24"></a>
### 第 24 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L25"></a>
### 第 25 行

```python
@pytest.mark.skipif(importlib.util.find_spec("mcp") is None, reason="optional MCP extra")
```

**语法与数据变化：** 缺MCP依赖则标跳过。

**为什么与边界：** 不默默替换成普通函数调用冒充协议测试。

<a id="L26"></a>
### 第 26 行

```python
def test_mcp():
```

**语法与数据变化：** 定义stdio客户端/服务端集成用例。

**为什么与边界：** 不需要LLM或HTTP公开端口。

<a id="L27"></a>
### 第 27 行

```python
    result = subprocess.run([sys.executable, "-m", "examples.mcp_client"], cwd=ROOT, capture_output=True, text=True, timeout=30)
```

**语法与数据变化：** 执行MCP客户端子进程并设30秒超时。

**为什么与边界：** 避免协议卡住无限等待；超时会成为真实测试失败。

<a id="L28"></a>
### 第 28 行

```python
    assert result.returncode == 0, result.stderr
```

**语法与数据变化：** 客户端应退出0，否则展示stderr。

**为什么与边界：** 协议/工具错误不能当作正常空结果。

<a id="L29"></a>
### 第 29 行

```python
    assert "webhook-delivery" in result.stdout
```

**语法与数据变化：** stdout要包含Webhook文档ID。

**为什么与边界：** 在程序无错误之外，进一步检查有预期工具输出；仍不是完整内容事实核验。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

```python
@pytest.mark.skipif(importlib.util.find_spec("pypdf") is None, reason="optional ingest extra")
```

**语法与数据变化：** 缺pypdf就跳过PDF测试。

**为什么与边界：** 本标记未检查tiktoken，但pdf_tokens顶层导入它，因此运行还需完整ingest依赖。

<a id="L32"></a>
### 第 32 行

```python
def test_pdf_fixture_and_empty_page(tmp_path):
```

**语法与数据变化：** tmp_path隔离生成文件与空PDF。

**为什么与边界：** 避免测试覆盖仓库已有artifacts/demo.pdf。

<a id="L33"></a>
### 第 33 行

```python
    from pypdf import PdfReader, PdfWriter
```

**语法与数据变化：** 测试体内导入PDF读写类。

**为什么与边界：** 延迟可选依赖加载直到确认非skip。

<a id="L34"></a>
### 第 34 行

```python
    from examples.make_demo_pdf import main
```

**语法与数据变化：** 导入真实生成样例函数main。

**为什么与边界：** 不是手写假的提取结果，随后会实际生成PDF字节。

<a id="L35"></a>
### 第 35 行

```python
    import os
```

**语法与数据变化：** 导入 `os` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库操作系统接口，用于环境变量、目录权限或进程环境。环境变量来自进程，不会因为代码中有名字就自动配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L36"></a>
### 第 36 行

```python
    previous = Path.cwd()
```

**语法与数据变化：** 记录当前工作目录以便恢复。

**为什么与边界：** os.chdir是进程全局状态，异常路径也必须清理。

<a id="L37"></a>
### 第 37 行

```python
    try:
```

**语法与数据变化：** 用try/finally保护临时目录切换。

**为什么与边界：** 只有正常路径切回来是不够的，断言失败也需要恢复。

<a id="L38"></a>
### 第 38 行

```python
        os.chdir(tmp_path)
```

**语法与数据变化：** 切换到测试临时目录。

**为什么与边界：** 生成器使用相对artifacts路径，所以产物会落在此隔离目录。

<a id="L39"></a>
### 第 39 行

```python
        main()
```

**语法与数据变化：** 运行PDF生成函数。

**为什么与边界：** 会创建artifacts/demo.pdf，确实是文件写入。

<a id="L40"></a>
### 第 40 行

```python
        assert "Webhook retries: 3." in PdfReader("artifacts/demo.pdf").pages[0].extract_text()
```

**语法与数据变化：** 实际打开PDF、取第一页、提取文本并核对句子。

**为什么与边界：** 验证有可提取文字，不是仅确认文件存在或页数为1。

<a id="L41"></a>
### 第 41 行

```python
    finally:
```

**语法与数据变化：** 无论前面成功或异常都进入finally。

**为什么与边界：** 避免测试污染后续用例的cwd。

<a id="L42"></a>
### 第 42 行

```python
        os.chdir(previous)
```

**语法与数据变化：** 恢复原目录。

**为什么与边界：** 是环境清理，不是撤销已写出的临时文件。

<a id="L43"></a>
### 第 43 行

```python
    writer = PdfWriter()
```

**语法与数据变化：** 创建另一个PDF writer用于空页反例。

**为什么与边界：** 不复用有文字样例，确保失败原因是无文本层。

<a id="L44"></a>
### 第 44 行

```python
    writer.add_blank_page(width=100, height=100)
```

**语法与数据变化：** 加入100×100空白页，没有字体和内容流。

**为什么与边界：** 这张页合法但没有目标文本。

<a id="L45"></a>
### 第 45 行

```python
    target = tmp_path / "blank.pdf"
```

**语法与数据变化：** 指定临时blank.pdf路径。

**为什么与边界：** 路径与已生成demo.pdf不同，避免误读有文字文件。

<a id="L46"></a>
### 第 46 行

```python
    with target.open("wb") as handle:
```

**语法与数据变化：** 以wb打开文件，with负责关闭句柄。

**为什么与边界：** 该上下文是文件IO，与sqlite事务上下文的关闭语义不同。

<a id="L47"></a>
### 第 47 行

```python
        writer.write(handle)
```

**语法与数据变化：** 将空页PDF序列化到磁盘。

**为什么与边界：** 之后子进程读取的是真实文件而非内存mock。

<a id="L48"></a>
### 第 48 行

```python
    result = subprocess.run([sys.executable, "-m", "examples.pdf_tokens", str(target)], cwd=ROOT, capture_output=True, text=True)
```

**语法与数据变化：** 运行pdf_tokens处理空页，并捕获输出。

**为什么与边界：** 脚本应在发现空text后抛错，发生在编码表加载前。

<a id="L49"></a>
### 第 49 行

```python
    assert result.returncode != 0 and "无文本层" in result.stderr
```

**语法与数据变化：** 要求非零退出且stderr包含无文本层提示。

**为什么与边界：** 排除因其他原因碰巧失败；若仅缺tiktoken，错误信息不匹配仍应失败。

## 跟一遍数据与验证边界

如果仅装test依赖，四类测试可能skip；不能把0失败说成所有集成都通过。图中True通过，False和字符串true均拒绝。

## 只练一个关键点（不是新的学习验收记录）

1. 用-q -rs运行本文件，逐项记pass或skip及原因。
2. 对应真实库/子进程路径标注验证范围；PDF空页通过不代表token表已下载。
3. **复盘：** 依赖未装跳过为什么不是集成成功？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
