# 1B · 从脚本到可靠文档加载器

[全部课程](../course/index.md) · [上一课](01a-read-document.md) · [下一课](01c-lexical-search.md)

- **学习进度：** 已完成。本课基础目标依据聊天中的概念回答、纠错后的变式及运行反馈验收；不是整个阶段 1 已通过。详细记录见文末。
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


## 分步跟做补充：真实加载器的错误路径（已完成，保留步骤供复习）

目前正常目录加载已跑通。本练习验证加载器会拒绝不合约定的文件；不需要先安装 pytest，也不要修改原始三份手册。

1. 在仓库根目录下，用编辑器创建文件 `artifacts/lesson-1b/broken.md`。如果父目录不存在，先创建 `artifacts` 和 `lesson-1b`。这个专用练习目录里只放本次文件。
2. 写入以下内容并保存：

```markdown
## 测试标题
这是一份测试正文。
```

3. 确认仍在之前已安装本项目的 Python 环境、终端仍位于仓库根目录，运行：

```bash
python -c "from pathlib import Path; from evidencedesk.documents import load_documents; print(load_documents(Path('artifacts/lesson-1b')))"
```

`python -c` 表示执行后面引号里的 Python 代码；这里的分号只是将导入和调用放在同一条命令里。

**练习预期（完成反馈另见 1B-Q7）：** 抛出 `ValueError: broken.md: 第一行必须是 # 标题`。`## ` 不匹配我们要求的精确前缀 `# `。注意：Markdown 的二级标题语法本身合法，只是不满足本加载器规定的“文件第一行必须是一级标题”。

4. 只把 `broken.md` 第一行改为 `# 测试标题`，保存，重新运行同一条命令。不要修改加载函数去放宽检查。
5. 此时预期不报错，打印包含一个 `Document` 的列表，其中 ID 是 `broken`、标题是 `测试标题`、正文是 `这是一份测试正文。`、来源是 `broken.md`。

本轮已反馈两次结果符合预期，标准解析见 1B-Q7。复习时可重新运行。目标是验证“错误输入被拒绝，修正输入后通过”，不是把所有报错都当成程序坏了。`artifacts/` 已被 Git 忽略，不会把这些临时练习资料当成正式语料提交。

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


### 1B-Q4：空白正文与有效正文的对照实操

**题目：** 在临时脚本 `scratch_validate.py` 中运行下面的完整示例，再把第三个列表元素 `"   "` 改成 `"密钥应保存在服务端。"`，比较两次结果。

```python
lines = ["# 密钥指南", "", "   "]

title = lines[0][2:].strip()
text = "\n".join(lines[1:]).strip()

print("标题：", repr(title))
print("正文：", repr(text))

if not title or not text:
    raise ValueError("标题和正文不能为空")
```

**学习者反馈：** “跟你描述的一样。”

**判断：** 根据学习者反馈，两种输入的运行结果符合预期，本次对照实操通过；不据此宣称整个加载器已验收。

**标准答案：第一次（只有空白正文）**

```text
标题： '密钥指南'
正文： ''
```

随后抛出 `ValueError: 标题和正文不能为空`。原因是 `lines[1:]` 为 `["", "   "]`，连接后得到 `"\n   "`，`.strip()` 去掉两端空白，正文变为 `""`。标题不为空，但正文为空，因此 `not title or not text` 为 `True`。

**标准答案：第二次（有实际正文）**

修改后的输入是：

```python
lines = ["# 密钥指南", "", "密钥应保存在服务端。"]
```

输出：

```text
标题： '密钥指南'
正文： '密钥应保存在服务端。'
```

此时标题和正文都非空，条件为 `False`，不会抛出上述异常。

**复习要点：**

- `repr()` 把字符串的表示形式打印出来，便于看清 `''`、空格和转义字符；它不会修改原字符串，也不承担校验职责。
- `or` 表示任意一个条件成立就进入错误分支；空白清理之后，标题与正文都必须有实际内容。
- 第一种输入报错，是校验成功拦截了无效文档，不是操作失败；第二种输入不报错，说明这项非空校验通过，不等于文档事实已被验证。


### 1B-Q5：直接构造 Document 会自动检查非空吗？

**题目：** 下面的数据类没有自行定义校验逻辑。如果跳过 `load_documents()`，直接传入空标题、空正文，会自动抛出“标题和正文不能为空”，还是成功创建对象？

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    source: str

doc = Document(
    id="x",
    title="",
    text="",
    source="x.md",
)
```

**学习者回答：** “会创建对象吧，这个定义本身并没有做相关限制，而是只有在加载时限制好像。”

**判断：** 正确，指出了当前实现中非空校验所在的位置。

**标准答案：** 会成功创建对象。`@dataclass` 根据字段生成初始化等方法，但当前 `Document` 没有检查字段值是否为空；`title: str` 等类型提示也不会自动执行字符串类型或非空检查。`frozen=True` 限制创建后的常规字段赋值，不会把空字符串变成非法初始值。

非空检查实际在 `load_documents()` 中：

```python
if not title or not text:
    raise ValueError(f"{source}: 标题和正文不能为空")
```

只有执行到这段加载逻辑，才会由它主动抛出该异常。直接调用 `Document(...)` 不会自动调用 `load_documents()`，所以会绕过这项检查。

| 代码或概念 | 当前职责 | 不会自动做的事情 |
|---|---|---|
| `Document` 的四个字段 | 把 ID、标题、正文、来源组织成一个对象 | 不检查标题和正文是否有实际内容 |
| `title: str` 等类型提示 | 表达预期类型，供阅读和静态检查使用 | 不自动执行运行时类型或非空校验 |
| `@dataclass` 生成的初始化方法 | 接收并设置字段；当前无默认值的字段是必填参数 | 不理解“合法知识库文档”的业务规则 |
| `frozen=True` | 阻止创建后的常规字段重新赋值 | 不验证初始值非空，不是安全隔离机制 |
| `load_documents()` 内的显式 `if` | 在加载入口验证格式及标题/正文非空 | 不会拦截完全绕过加载入口的对象构造 |

**复习要点：** 数据结构与业务校验不是一回事。若将来要求所有构造入口都遵守同一规则，需要设计统一的校验入口或在对象初始化时明确添加校验，不能仅依赖类型提示或 `frozen=True`。本轮只理解现有设计，不提前修改课程实现。


### 1B-Q6：运行真正的多文档加载示例

**任务：** 在仓库根目录、安装了本项目的 Python 环境中运行：

```bash
python -m examples.load_manuals
```

**学习者反馈：** “我得到的输出跟你的预期相符。”

**判断：** 根据学习者反馈，正常目录加载实操符合预期。反馈未逐行贴出具体输出，因此不将其写成导师独立复核了学习者本机环境；尚未验证该学习者对错误输入的运行结果。

**标准结果：** 原始 `data/sample/` 中有三份有效 Markdown 文档，输出共三行。每行由 `print(doc.id, doc.title, len(doc.text))` 打印以下信息：

| 顺序 | ID | 标题 | 最后一项 |
|---|---|---|---|
| 1 | `api-key-policy` | API 密钥管理与签名校验 | 该文档正文的字符数 |
| 2 | `incident-escalation` | 故障工单与升级流程 | 该文档正文的字符数 |
| 3 | `webhook-delivery` | Webhook 投递与重试 | 该文档正文的字符数 |

字符数由本地实际正文计算；修改正文会改变该数值，不能把它当固定文档身份。`len(doc.text)` 也不等于文件字节数或模型 token 数。

**标准解析：** `Path("data/sample")` 指向当前工作目录下的数据目录；`load_documents()` 逐份读取、校验，构造 `Document` 并返回列表。调用处的 `for` 依次取得每个文档对象，打印三个字段。加载器使用 `sorted(data_dir.glob("*.md"))` 提供稳定的文件名顺序，而不是依赖文件系统碰巧返回的顺序。

**复习要点：** `doc` 是单份文档对象，返回值是文档列表；正常输入能跑通，只证明正常路径符合预期，接下来还需验证实际加载函数的错误路径。


### 1B-Q7：真实加载器能拒绝错误输入，并接受修正后的输入吗？

**任务：** 在独立练习目录 `artifacts/lesson-1b/` 中创建 `broken.md`，先以 `## 测试标题` 开头调用 `load_documents()`，再仅把第一行改为 `# 测试标题`，重新调用。

**学习者反馈：** “符合预期。”

**判断：** 根据学习者对两次对照运行的反馈，本次错误路径实操通过。未收到逐行原始输出，因此记录为学习者运行反馈，不冒充导师独立检查了学习者本机文件。

**标准答案：第一次应拒绝输入。**

```text
ValueError: broken.md: 第一行必须是 # 标题
```

第一行 `"## 测试标题"` 的开头是两个井号，而不是本加载器要求的井号加空格 `"# "`，因此 `startswith("# ")` 返回 `False`，加载函数主动抛出带来源文件名的异常。

这不是说 Markdown 二级标题语法非法；只是这份课程语料约定第一行必须是一级标题。无效输入被拒绝，是校验按预期工作。

**标准答案：修正后应成功加载。**

第一行改为 `"# 测试标题"` 后，前缀检查通过；提取出的标题、正文均非空，函数构造并返回一个文档列表：

```text
[Document(id='broken', title='测试标题', text='这是一份测试正文。', source='broken.md')]
```

**复习要点：**

- 修正的是输入文件，而不是删掉校验或修改程序来强行消除异常。
- 错误发生在构造 `Document` 之前；这与 1B-Q5 中“直接构造对象可以绕过加载入口检查”一致。
- 这组对照验证了实际加载函数的一个重要错误路径，不代表所有异常、安全或编码场景都已由学习者测试。

### 1B 小课验收小结

**结论：本课基础学习目标通过，可以进入同一阶段内的 1C。**

验收依据：

1. 正确理解空列表与 `or` 短路。
2. 纯空白标题题首次误答，经讲解后答对有效标题变式；保留纠错记录。
3. 标题/正文非空对照实操反馈符合预期。
4. 正确区分 `Document` 数据结构与加载入口的业务校验。
5. 正常目录加载，以及实际加载器的错误/修正输入对照均反馈符合预期。

这是对本课已讨论内容的学习验收，不是整个阶段 1 完成，也不等于生产系统已通过验收。后续 1D 还会将这些行为落实到自动化测试中。
