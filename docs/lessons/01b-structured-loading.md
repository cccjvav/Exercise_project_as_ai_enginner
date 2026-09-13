# 1B · 从脚本到可靠文档加载器

[全部课程](../course/index.md) · [上一课](01a-read-document.md) · [下一课](01c-lexical-search.md)

- **学习进度：** 进行中；已答对空列表与 `or` 短路题、带空白的有效标题变式；纯空白标题题经讲解纠错，整课尚未验收。
- **前置理解：** 1A：理解文件、字符串和行列表
- **验证状态：** 离线参考实现；已纳入 pytest。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

第一课假设文件格式一定正确。真实入库时，空文件、错误标题和目录路径都可能出现。我们要让错误发生在加载阶段，而不是在模型调用后才发现上下文为空。

## 2. 原理：在这个问题里理解技术

函数把输入路径变为结构化结果。dataclass 提供字段和初始化方法，类型提示表达约定但不自动校验文件内容；显式 if 才实现校验。frozen 防止字段被意外赋值，不代表对象拥有永久不变的企业身份。

先验证目录，再按文件名排序加载；第一行必须以 `# ` 开头，标题和正文都不能空。错误时携带相对来源便于定位。文件名改动会改 ID，这是教学约定，不是最终版本管理方案。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/documents.py`

完整源文件：[打开源码](../../src/evidencedesk/documents.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/documents.py -->
```python
#: Path 表达路径，dataclass 为字段生成初始化方法；此时不需要数据库或框架。
from pathlib import Path
from dataclasses import dataclass

#: frozen 防止误改字段；ID 标识文档，source 定位来源，二者用途不同。
@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    source: str

#: 入口先区分不存在与不是目录；这些是输入错误，不应伪装成零命中。
def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(data_dir)
    if not data_dir.is_dir():
        raise NotADirectoryError(data_dir)
    documents = []
    #: 只读第一层 Markdown 文件；排序让结果可复现，跳过名字以 .md 结尾的目录。
    for path in sorted(data_dir.glob("*.md")):
        if not path.is_file():
            continue
        source = path.relative_to(data_dir).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        #: 先判空再访问首行；startswith 真正校验前缀，而 removeprefix 本身不会报错。
        if not lines or not lines[0].startswith("# "):
            raise ValueError(f"{source}: 第一行必须是 # 标题")
        title = lines[0][2:].strip()
        text = "\n".join(lines[1:]).strip()
        if not title or not text:
            raise ValueError(f"{source}: 标题和正文不能为空")
        #: 每个文件变成一个结构化对象；空目录自然返回空列表。
        documents.append(Document(path.stem, title, text, source))
    return documents
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–4 | Path 表达路径，dataclass 为字段生成初始化方法；此时不需要数据库或框架。 |
| 5–12 | frozen 防止误改字段；ID 标识文档，source 定位来源，二者用途不同。 |
| 13–19 | 入口先区分不存在与不是目录；这些是输入错误，不应伪装成零命中。 |
| 20–25 | 只读第一层 Markdown 文件；排序让结果可复现，跳过名字以 .md 结尾的目录。 |
| 26–32 | 先判空再访问首行；startswith 真正校验前缀，而 removeprefix 本身不会报错。 |
| 33–35 | 每个文件变成一个结构化对象；空目录自然返回空列表。 |

### `examples/load_manuals.py`

完整源文件：[打开源码](../../examples/load_manuals.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/load_manuals.py -->
```python
#: 用包中可靠加载器替代第一课脚本的临时字段提取。
from pathlib import Path
from evidencedesk.documents import load_documents

#: 一行展示身份、标题与正文长度，不在终端重复打印所有手册。
def main():
    for doc in load_documents(Path("data/sample")):
        print(doc.id, doc.title, len(doc.text))

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–4 | 用包中可靠加载器替代第一课脚本的临时字段提取。 |
| 5–11 | 一行展示身份、标题与正文长度，不在终端重复打印所有手册。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pip install -e ".[dev]"
python -m examples.load_manuals
python -m pytest tests/test_search.py -q
```

### 只做这些关键改动

1. 打开 `tests/test_search.py`，找到 `test_invalid_document` 的参数列表。
2. 加入 `"## 二级标题\n正文"`；不用改真实手册。
3. 预测它会被接受还是抛错，再运行 `python -m pytest tests/test_search.py -q`。
4. 预期新增用例通过：因为它成功验证“非法一级标题必须报错”。通过不是指文件被接受。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

解释 `not lines or ...` 为什么不会访问空列表；指出“空目录返回 []”与“不存在目录报错”的区别。输出应有三份文档，顺序为 api-key-policy、incident-escalation、webhook-delivery。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果删除了格式校验，错误会在后续哪个阶段暴露？为什么早失败更便宜？

**产出：** 可复用 Document 与加载函数、一个新增边界用例及你的预测。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.python.org/3/library/dataclasses.html
- https://docs.pytest.org/en/stable/how-to/tmp_path.html

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。


## 已完成问答与标准答案

记录日期：2026-09-13。正确回答一题，只记录对应知识点通过，不自动视为整节 1B 已掌握。

### 1B-Q1：空列表会触发哪一种异常？

**题目：** 当 `lines = []` 时，下面的代码会发生什么？

```python
if not lines or not lines[0].startswith("# "):
    raise ValueError("第一行必须是 # 标题")

title = lines[0][2:].strip()
```

- **A：** 访问 `lines[0]`，触发 `IndexError`。
- **B：** 不访问 `lines[0]`，主动抛出 `ValueError`。

**学习者回答：** B。

**判断：** 正确。

**标准答案：** 空列表在布尔判断中是假值，所以 `not lines` 为 `True`。Python 的 `or` 从左向右求值，左侧为真时发生短路，不再计算右侧的 `lines[0]`。条件成立，进入 `if`，由 `raise` 主动抛出 `ValueError`。在这段代码中异常没有被捕获，因此后面的标题提取语句不会执行。

| 执行顺序 | 本题中的结果 |
|---|---|
| 判断 `not lines` | `True` |
| 是否计算 `not lines[0].startswith("# ")` | 否，`or` 短路 |
| 是否进入 `if` | 是 |
| 抛出的异常 | 主动抛出 `ValueError`，而非索引访问导致的 `IndexError` |
| 是否执行后面的 `title = ...` | 否 |

**复习要点：** 先检查列表为空，再访问首元素；检查顺序具有实际作用。这里的 `raise` 不是打印提示后继续执行。


### 1B-Q2：纯空白标题为什么仍然无效？（纠错记录）

**题目：** 给定 `lines = ["#   ", "正文内容"]`，执行以下代码，是 A：抛出“第一行必须是 # 标题”，B：抛出“标题不能为空”，还是 C：不报错、标题是三个空格？

```python
if not lines or not lines[0].startswith("# "):
    raise ValueError("第一行必须是 # 标题")

title = lines[0][2:].strip()

if not title:
    raise ValueError("标题不能为空")
```

**首次回答：** C。

**纠错结论：** 正确答案是 **B**。此题首次作答不正确，保留纠错过程，不追记为首次答对。

**标准解析：** `"#   "` 以 `"# "` 开头，格式检查通过。`[2:]` 去掉 `#` 和第一个空格后剩两个空格，`.strip()` 将剩余空格去掉，得到空字符串 `""`。因此 `not title` 为 `True`，主动抛出 `ValueError("标题不能为空")`。

**易错点：** 前缀合法不等于标题有效；`.strip()` 会去掉两端空白，不会把纯空白当作实际文字。

### 1B-Q3：带有实际文字的标题会怎样？（纠错后的变式）

**题目：** 换成 `lines = ["#   密钥指南   ", "正文内容"]`，执行同样代码后，`title` 是什么？会触发“标题不能为空”吗？

**学习者回答：** “标题会是密钥指南，不会触发错误。”

**判断：** 正确；这次核对的是有效标题的空白清理，不将它等同于整节加载器已掌握。

**标准答案：** `title` 为 `"密钥指南"`，不会触发错误。

| 操作 | 结果 |
|---|---|
| `lines[0].startswith("# ")` | `True`，格式检查通过 |
| `lines[0][2:]` | `"  密钥指南   "` |
| `.strip()` | `"密钥指南"` |
| `not title` | `False`，不进入抛错分支 |

**复习要点：** `[2:]` 去掉固定前缀，`.strip()` 清理两端空白，`if not title` 检查清理后的结果。`.strip()` 不删除文字之间的空格，例如 `"  API 密钥  ".strip()` 得到 `"API 密钥"`。
