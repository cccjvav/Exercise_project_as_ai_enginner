# 1D · CLI、工程配置与测试

[全部课程](../course/index.md) · [上一课](01c-lexical-search.md) · [下一课](01e-evaluation.md)

- **前置理解：** 1C：理解 search 的输入输出
- **验证状态：** CLI 和 pytest 已运行；不需要模型密钥。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

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
