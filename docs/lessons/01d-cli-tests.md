# 1D · CLI、工程配置与测试

[全部课程](../course/index.md) · [上一课](01c-lexical-search.md) · [下一课](01e-evaluation.md)

- **学习进度：** 进行中；最小 pytest 用例与大小写归一化回归实操已反馈通过，且能解释防住的错误；异常测试机制题已答对，并补充了“预期异常”与“测试失败”的术语区分；非法 k 参数化实操及合法值反例预测已通过；布尔类型边界、CLI 解析与输出契约尚未验收。
- **前置理解：** 1C：理解 search 的输入输出
- **验证状态：** CLI 和 pytest 已运行；不需要模型密钥。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 当前跟做：让测试发现一次可控回归（已完成，保留步骤供复习）

这是本课的第一小步：把已经理解的“大小写归一化与词去重”写成自动检查，不要求从空白设计测试。

1. 在之前的 Python 虚拟环境、仓库根目录安装测试依赖：

```bash
python -m pip install -e ".[dev]"
```

`dev` 是 `pyproject.toml` 里的一组可选开发依赖，本项目包含 pytest；不会调用模型。

2. 新建 `tests/test_learning_tokens.py`，粘贴完整示例：

```python
from evidencedesk.search import tokens


def test_tokens_ignore_case_and_duplicates():
    actual = tokens("WEBHOOK 重试 重试")
    expected = {"webhook", "重试"}
    assert actual == expected
```

- 导入项目现有函数，不在测试中复制一份实现。
- `test_` 开头的函数可被 pytest 自动发现并执行；不需要自己在文件底部调用。
- `actual` 是程序真实返回，`expected` 是你根据已确认规则写下的预期。
- `assert` 表达“这里必须相等”；不相等就让测试失败，并展示差异。

3. 只运行这一个测试文件：

```bash
python -m pytest tests/test_learning_tokens.py -q
```

预期摘要包含 `1 passed`。`-q` 让输出简洁，不改变测试行为。

4. 故意制造一个容易恢复的回归：打开 `src/evidencedesk/search.py`，只在 `tokens()` 的返回行中，将 `text.casefold()` 临时改为 `text`。保存后重新运行同一条测试命令，预期 `1 failed`；`WEBHOOK` 不再转为小写，实际集合会漏掉 `webhook`。
5. 将这一处恢复为 `text.casefold()`，保存并再次运行，预期回到 `1 passed`。最后确认生产代码已经恢复。

这是为了观察测试如何发现回归，不是要求保留坏代码，也不是完整的“先写失败测试再实现功能”的 TDD 流程。不要改正确的 `expected` 去迁就错误实现。如果命令或导入报错，先定位环境问题，不把它和断言失败混为一谈。

学习者已反馈“通过→失败→恢复通过”符合预期，并正确说明防住的错误，见文末 1D-Q1。原有测试无需删除；新用例作为学习者按步骤添加的练习保留。此处记录本机操作反馈，不声称导师已读取学习者新建的测试文件或终端日志。

## 测试“应该抛出的异常”（概念题已完成，见 1D-Q2）

正常输入返回正确结果是一类契约；非法输入被明确拒绝也是契约。本项目要求 `k` 是正整数，`k=0` 应抛出 `ValueError`，而不是悄悄返回空列表。

先阅读完整的小测试，不急着修改源码或创建更多文件：

```python
import pytest
from evidencedesk.search import search


def test_search_rejects_zero_k():
    with pytest.raises(ValueError):
        search("Webhook", documents=[], k=0)
```

- `import pytest`：这里不只用 pytest 执行测试，还需要调用它提供的异常检查工具。
- `with pytest.raises(ValueError):`：要求缩进代码块执行时抛出 `ValueError`。预期异常会被这个上下文管理器接住，不作为未处理异常让测试失败。
- `search(...)`：调用真实检索函数。空文档列表避免读文件，让测试只关注 k 的校验；参数校验在文档遍历之前执行。
- 若没有抛异常，测试失败；若抛出的是不匹配的异常类型，也不能满足这个要求。

这不是忽略异常，而是验证“在指定条件下，指定异常必须出现”。它只检查异常类型，不检查错误消息或其他 k 值；那些需要另外的断言与用例。

## 一个测试检查多种非法输入（已完成，保留步骤供复习）

不修改生产源码，保留前面的测试文件。新建 `tests/test_learning_invalid_k.py`，粘贴完整示例：

```python
import pytest
from evidencedesk.search import search


@pytest.mark.parametrize("bad_k", [0, -1, True])
def test_search_rejects_invalid_k(bad_k):
    with pytest.raises(ValueError):
        search("Webhook", documents=[], k=bad_k)
```

- `@pytest.mark.parametrize(...)` 是装饰器形式的 pytest 配置；这里让下面的测试分别使用三个参数值运行，不必先掌握装饰器的内部实现。
- `"bad_k"` 指定要注入的参数名，对应函数形参 `bad_k`。
- `[0, -1, True]` 给出三组输入，分别产生一个测试用例；不是把整个列表传给一次 search 调用。
- 每次调用均要求 `ValueError`：0 和负数不是正整数，布尔值 True 在本项目也不能替代数量 1。

在原虚拟环境、仓库根目录运行：

```bash
python -m pytest tests/test_learning_invalid_k.py -q
```

预期摘要含 `3 passed`，表示三种非法输入都按约定被拒绝，而不是被函数接受。这里仅运行新文件，不会把前一个学习测试算入这次摘要。

学习者已反馈三种非法输入的运行结果符合预期，并正确预测将 `True` 换成 `1` 会出现一个失败用例，见 1D-Q3。替换后的结果属于概念预测，不声称学习者已额外运行。复习时无需修改生产源码。

## 补充解释：为什么单独防布尔值？（导师讲解，未单独验收）

Python 的 `bool` 是 `int` 的子类：

```python
print(isinstance(True, int))  # True
print(type(True) is int)     # False
```

所以项目使用 `type(k) is not int`，明确拒绝布尔值；若只写 `not isinstance(k, int) or k <= 0`，`True` 会漏过校验，因为它参与比较时等价于 1。仅测试 `False` 又可能掩盖这个问题，因为 `False <= 0` 会成立。这里讨论的是 Python 直接调用 `search()`；终端中的 `--k True` 传入的是字符串，不会自动变成布尔值。

## 下一小步：命令行解析与业务校验的分工（待完成）

CLI 是命令行接口。终端参数最初是字符串，`argparse` 是 Python 标准库中的参数解析工具。下面的独立例子只演示项目中 k 的解析设置，不读取手册：

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--k", type=int, default=3)
args = parser.parse_args(["--k", "0"])

print(args.k)
print(type(args.k))
```

输出：

```text
0
<class 'int'>
```

- `ArgumentParser()` 创建参数解析器。
- `add_argument(...)` 声明接受 `--k`；`type=int` 用整数转换器处理参数值，未提供时使用默认值 3。
- 本例给 `parse_args()` 显式传入字符串列表，模拟终端参数，便于直接阅读复现。项目实际的 `parse_args()` 不传列表，从当前进程的命令行读取参数。
- `args` 保存解析结果，通过 `args.k` 取值。字符串 `"0"` 已经被转换为整数 `0`。

下一题只需判断：设置 `type=int` 是否已经保证 k 是正整数？为什么业务函数仍保留自己的校验？这是待回答的概念题，不提前归档为已掌握。

## 1. 问题：现在为什么需要它？

函数能在编辑器里跑，不等于别人能在干净环境里复现。输入非法、标准输出夹杂调试文字、测试依赖本机路径，都可能破坏使用体验。

## 2. 原理：在这个问题里理解技术

pyproject 声明包位置和可选依赖；editable install 将 src 包注册到当前解释器。`python -m` 保证通过包导入，不推荐直接执行 src 下文件。argparse 负责解析终端参数，应用逻辑仍由 search 负责。

测试应断言可观察契约而不是内部实现细节：同分排序、非法 k、UTF-8、JSON 和退出码。tmp_path 隔离测试数据；subprocess 验证完整 CLI。测试先失败再修复，证明它确实能发现目标错误。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `pyproject.toml`

完整源文件：[打开源码](../../pyproject.toml)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: pyproject.toml -->
```toml
#: 构建后端告诉 pip 如何打包；setuptools>=68 是构建依赖，不是业务代码导入。
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

#: 项目身份与最低解释器版本；空 dependencies 保持核心离线标准库无额外运行依赖。
[project]
name = "evidencedesk"
version = "0.1.0"
description = "Evidence-first AI engineering guided course labs"
requires-python = ">=3.11"
dependencies = []

#: 按课选装 extras；允许范围不是实测锁，精确快照另见 requirements-tested.lock.txt。
[project.optional-dependencies]
dev = ["pytest>=8,<9"]
web = ["fastapi>=0.115,<1", "uvicorn>=0.30,<1", "httpx>=0.27,<1"]
vector = ["qdrant-client>=1.12,<2"]
ingest = ["pypdf>=5,<7", "tiktoken>=0.8,<1"]
llm = ["langchain-openai>=1,<2", "langchain-core>=1,<2"]
workflow = ["langgraph>=1,<2"]
advanced = ["deepagents>=0.3,<1", "mcp>=1,<2"]

#: src 布局让安装与包导入显式，避免项目根目录偶然掩盖安装问题。
[tool.setuptools.packages.find]
where = ["src"]

#: 默认仅收集 tests 中用例，不把教程示例当测试脚本执行。
[tool.pytest.ini_options]
testpaths = ["tests"]
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–5 | 构建后端告诉 pip 如何打包；setuptools>=68 是构建依赖，不是业务代码导入。 |
| 6–13 | 项目身份与最低解释器版本；空 dependencies 保持核心离线标准库无额外运行依赖。 |
| 14–23 | 按课选装 extras；允许范围不是实测锁，精确快照另见 requirements-tested.lock.txt。 |
| 24–27 | src 布局让安装与包导入显式，避免项目根目录偶然掩盖安装问题。 |
| 28–30 | 默认仅收集 tests 中用例，不把教程示例当测试脚本执行。 |

### `tests/test_search.py`

完整源文件：[打开源码](../../tests/test_search.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

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

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–11 | tmp_path 由 pytest 提供，测试不修改真实语料；每个用例拥有独立临时目录。 |
| 12–32 | 断言字段而不仅是数量；读取失败、格式错误和空目录应表现不同。 |
| 33–50 | 通过人工可算的分数建立 oracle；打乱输入、重复查询词不应改结果。 |
| 51–57 | 子进程检查真实 CLI 行为，而不是只测试内部函数。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pytest tests/test_search.py -q
python -m evidencedesk.search --query "Webhook" --k 0
```

### 只做这些关键改动

1. 打开 `src/evidencedesk/search.py`，暂时将排序键 `(-hit.score, hit.document_id)` 改为 `(hit.score, hit.document_id)`。
2. 运行 `python -m pytest tests/test_search.py -q`，预期排序测试失败。
3. 阅读 expected/actual，恢复负号，再运行，预期通过。
4. 对比 --k 0 的非零退出码与空命中的正常退出码。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

能指出测试防住的是“把弱匹配排在前面”，而非仅说红变绿。解释 `True` 为什么需专门排除，以及错误为什么不打印在 stdout。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果测试只断言 len(hits)>0，会漏掉什么错误？为什么不把所有测试都连在线模型？

**产出：** 最小可安装 Python 包、CLI 契约、一次红→绿测试记录。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://packaging.python.org/en/latest/tutorials/packaging-projects/
- https://docs.python.org/3/library/argparse.html

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。


## 已完成问答与标准答案

记录日期：2026-09-13。仅归档已完成的回答与反馈，不将一个用例通过等同于整个 1D 或阶段 1 已验收。

### 1D-Q1：测试能防住哪一种回归？

**题目与操作：** 新建 `tests/test_learning_tokens.py`，断言 `tokens("WEBHOOK 重试 重试") == {"webhook", "重试"}`；运行测试，临时去掉实现中的 `.casefold()` 后重跑，再恢复正确实现并重跑。反馈三次结果，并解释防住的错误。

**学习者反馈：** “是，结果符合预期。我认为这个测试防止了因为大小写对不上而不算匹配上了的错误。”

**判断：** 正确。根据学习者反馈，三次运行符合“通过→失败→恢复通过”，且已经指出本次回归的具体影响。

**标准结果：**

| 实现状态 | `tokens("WEBHOOK 重试 重试")` 的值 | 测试摘要 |
|---|---|---|
| 原始实现：使用 `text.casefold()` | `{"webhook", "重试"}` | `1 passed` |
| 临时错误：改成 `text` | `{"重试"}` | `1 failed` |
| 恢复 `text.casefold()` | `{"webhook", "重试"}` | `1 passed` |

**标准解析：** 词表使用小写 `webhook`。删除 `.casefold()` 后，子串判断区分大小写，无法在大写 `WEBHOOK` 中找到小写词表项；中文“重试”仍能命中。实际集合因此缺少 `webhook`，与正确的期望集合不等，`assert` 失败。恢复大小写归一化后，正确行为恢复，测试重新通过。

**该测试保护的行为：** 大小写写法不同但应识别为同一个领域词时，不应发生漏匹配。本次可控变更证明测试能发现这一特定回归，并不证明所有输入、所有检索功能都没有错误。

**复习要点：**

- 回归是修改代码后破坏已经正确的行为；自动测试可以在运行时发现它，不能阻止人编辑出错误代码。
- 修复应恢复约定行为，不应改正确的 `expected` 去迁就错误实现。
- 本次故意破坏的是大小写归一化；不要把单次变更结果当成所有去重边界的测试证明。
- 学习者已报告完成恢复；导师本轮未独立读取其本机测试文件或三次完整日志。保留练习用例，生产实现应保持 `.casefold()`。


### 1D-Q2：预期异常没有发生，测试会怎样？

**题目：** 以下测试要求 `search()` 拒绝 `k=0`。如果误删参数校验，导致调用不报错而是正常返回 `[]`，测试会通过还是失败？为什么？

```python
import pytest
from evidencedesk.search import search


def test_search_rejects_zero_k():
    with pytest.raises(ValueError):
        search("Webhook", documents=[], k=0)
```

**学习者回答：** “会失败，因为测试关注的是一个失败的结果，然而结果并不是失败的。”

**判断：** 测试结果判断正确，已理解“不出现预期异常不满足测试要求”。导师补充术语澄清：这里要求的是特定异常，不是笼统要求“程序失败”；不把学习者原句改写成已经精确使用了异常术语。

**标准答案：** 测试失败，因为 `pytest.raises(ValueError)` 要求缩进代码块抛出 `ValueError`（或其子类），而 `[]` 是正常返回值，没有抛出预期异常。pytest 会以类似 `DID NOT RAISE <class 'ValueError'>` 的说明报告失败。

**三个层次要分开：**

| 情况 | 函数行为 | 是否符合本测试要求 |
|---|---|---|
| 非法 k 引发预期的 `ValueError` | 参数被明确拒绝 | 是，测试通过 |
| 非法 k 被静默接受，返回 `[]` | 正常返回，但违反约定 | 否，测试失败 |
| 抛出不匹配的异常，例如 `TypeError` | 抛了异常，但类型不符合约定 | 否，测试失败 |

**复习要点：** 异常不一定代表实现有缺陷，拒绝非法输入可以是正确行为。反过来，函数没有报错也不保证行为正确。测试检查的是约定是否得到满足，而不是简单地“有没有报错”。

**记录范围：** 这是已完成的概念预测，不冒充学习者已删除参数校验并运行该测试；生产源码无需为这道预测题改变。


### 1D-Q3：参数化异常测试中放入合法输入，会怎样？

**题目与实操：** 使用 `@pytest.mark.parametrize("bad_k", [0, -1, True])` 和 `pytest.raises(ValueError)`，运行 `tests/test_learning_invalid_k.py`；再预测只把列表中的 `True` 改成 `1`，测试是否全部通过，解释原因。

**学习者反馈：** “结果符合预期，如果把true换成1，测试会有一个失败，因为函数会返回正确结果而不是一个valueerror。”

**判断：** 正确。已反馈原始三个用例符合 `3 passed` 的预期，并正确预测合法输入不会抛出预期异常。原话中的 `true`、`valueerror` 在 Python 示例中分别写作 `True`、`ValueError`。

**标准答案：**

| 参数列表 | 每个用例共同要求 | 预期汇总 | 记录依据 |
|---|---|---|---|
| `[0, -1, True]` | 调用时抛出 `ValueError` | `3 passed` | 学习者已反馈实际运行符合预期 |
| `[0, -1, 1]` | 调用时抛出 `ValueError` | `2 passed, 1 failed` | 学习者已正确预测；未反馈实际执行替换版本 |

**标准解析：** `0` 和 `-1` 仍然违反正整数约束，函数抛出 `ValueError`，对应测试通过。`1` 是合法的正整数，能通过校验；本例 `documents=[]`，函数正常返回 `[]`。它没有抛出异常，因此要求 `ValueError` 的那个用例失败。

**复习要点：**

- 一个带三个参数值的测试函数会产生三个独立用例，不是一次调用传入整个列表。
- 参数化只是复用测试逻辑，不会自动为不同输入推断不同预期。
- 非法输入应拒绝，合法输入应正常处理。若要测试合法 k，应另写正常返回值断言，而不是把它混入统一要求抛异常的参数列表。
- `[]` 在这里是空文档列表下的正确返回，不是异常，也不能据此断言某个非空知识库没有资料。

**记录范围：** 基于学习者运行摘要反馈和概念预测，不声称已读取其本机测试文件或完整日志；本题通过不代表整个 1D 已完成。
