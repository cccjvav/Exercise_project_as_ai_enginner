# 2A · 分块、来源与幂等更新

> **1A细度源码精讲（2026-09-19补充）：** [examples/chunk_versions.py](../code/examples--chunk_versions_py.md) · [src/evidencedesk/ingest.py](../code/src--evidencedesk--ingest_py.md) · [tests/test_core.py](../code/tests--test_core_py.md) · [tools/fetch_public_manuals.py](../code/tools--fetch_public_manuals_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](01e-evaluation.md) · [下一课](02b-pdf-tokens.md)

- **学习进度：** 进行中；学习者于 2026-09-17 确认进入阶段 2。不重叠分块、重叠窗口与步长预测均已答对；重叠重复量实验已反馈通过，取舍解释方向正确并获术语补充；父文档归属题已作答，导师补充了 parent_id 与块 id 的区别；真实手册上的默认参数分块预测与定位实操已通过（2A-Q5，2026-09-24）；块 `id` 与 `version` 哈希、幂等更新、本课闭卷小实现尚未验收。
- **前置理解：** 阶段 1；理解文件身份与评测
- **验证状态：** 字符分块与内存快照已测试；不是生产持久化索引。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 把长文切成可定位的小段（预测已完成，见 2A-Q1）

阶段 1 的 q06、q09 没有因为过关而消失，已列入[跨阶段回归跟踪](../course/regression-cases.md)。本课先解决长文组织、来源和更新，不宣称分块就能理解同义词或判断收费依据；当前 chunks 也尚未自动接入 search。

先只看不重叠分块，不同时展开哈希、版本与更新逻辑。下面直接调用已有函数，无需安装新依赖：

```python
from evidencedesk.documents import Document
from evidencedesk.ingest import chunks


doc = Document(
    id="demo", title="分块示例", text="ABCDEFGHIJ", source="demo.md"
)
for chunk in chunks(doc, size=4, overlap=0):
    print(chunk["start"], chunk["end"], chunk["text"])
```

输出：

```text
0 4 ABCD
4 8 EFGH
8 10 IJ
```

- 这是手工构造的 Document，不需要创建或读取 demo.md 文件；source 只是本例的示意字段。
- `size=4` 表示每块最多 4 个 Python 字符，不是 4 字节或 4 tokens。
- `overlap=0` 表示相邻块暂不重叠，重叠的作用下一步再讲。
- 函数返回字典列表，循环每次取出一个块。
- start/end 为半开区间：包括 start，不包括 end。text[4:8] 对应 EFGH；最后不足 4 个字符也保留。
- 此处只打印定位与正文；实际函数还保留父文档、来源和版本信息，后面逐步展开。

概念检查已完成：学习者正确预测 size=3、overlap=0 时的四块及起止位置，见 2A-Q1。此处记录预测，不声称学习者已运行本课分块代码。

## 相邻块为什么需要重叠？（预测已完成，见 2A-Q2）

固定边界可能把一句话的条件和结论切到不同块中；检索时只拿到其中一块，可能缺少必要上下文。重叠会在相邻块中重复保留一段边界附近的内容，降低这种风险，但不保证句子或语义一定完整，也不是重叠越大越好。

**步长 = size - overlap**。size 是每块最多包含的字符数，步长是下一个块的起点向前移动的字符数。

例如 size=4、overlap=1，每次起点前进 3 个字符。完整示例：

```python
from evidencedesk.documents import Document
from evidencedesk.ingest import chunks


doc = Document(
    id="demo", title="分块示例", text="ABCDEFGHIJ", source="demo.md"
)
for chunk in chunks(doc, size=4, overlap=1):
    print(chunk["start"], chunk["end"], chunk["text"])
```

输出：

```text
0 4 ABCD
3 7 DEFG
6 10 GHIJ
```

- 起点依次为 0、3、6，而不是 0、4、8。
- 第一、二块共享 D；第二、三块共享 G。没有移动或改写原文，只是不同切片包含了相同位置的字符。
- 每块仍最多 4 个字符；overlap=1 不代表每块长度变为 5。
- 区间仍为左闭右开；最后一块已经覆盖到全文末尾，这份实现就停止，不再生成仅由已覆盖尾部组成的额外小块。
- 字符重叠不是模型理解能力，分块结果目前也未自动接入 search。已知 q06/q09 状态不因这个示例而改变。

概念检查已完成：学习者正确预测 size=4、overlap=2 时步长为 2，并给出四个块的完整区间与内容，见 2A-Q2。此处记录预测，不冒充已运行。

## 观察重叠带来的重复量（已完成，保留步骤供复习）

重叠可以保留部分边界上下文，但原文长度不变，不代表各块包含的字符总数不变。这次只观察这一取舍，不修改生产实现、检索器或评测集，也不把它当作 q06/q09 已改善的证据。

1. 在仓库根目录新建 `scratch_overlap.py`，粘贴完整代码：

```python
from evidencedesk.documents import Document
from evidencedesk.ingest import chunks


doc = Document(
    id="demo", title="分块示例", text="ABCDEFGHIJ", source="demo.md"
)
print("overlap 块数 块内字符总数")
for overlap in (0, 1, 2):
    parts = chunks(doc, size=4, overlap=overlap)
    total_chars = sum(len(part["text"]) for part in parts)
    print(overlap, len(parts), total_chars)
```

2. 使用原 Python 环境，在仓库根目录运行：

```bash
python scratch_overlap.py
```

3. 核对预期输出：

```text
overlap 块数 块内字符总数
0 3 10
1 3 12
2 4 16
```

逐行理解新增部分：

- `for overlap in (0, 1, 2)`：保持原文和 size 不变，只改变 overlap，形成对照。
- `parts` 是当前参数下的块列表；`len(parts)` 是块数。
- `len(part["text"])` 求单块长度，`sum(...)` 将各块长度相加；共享字符在每个包含它的块中都会被计入。
- `print(...)` 每行显示当前重叠量、块数、块内字符出现总数。原文仍只有 10 个字符。

这里统计的是字符，不是 token、实际耗时或费用；不能直接把 16/10 当作模型计费倍率。块数也不一定每次都增加，例如 overlap 从 0 改为 1 时本例仍为三块。

学习者已反馈三行符合预期，并指出过大重叠的重复与空间代价，见 2A-Q3。导师补充了“收益可能不抵代价”不等于“分块完全失去作用”的区别；来源与版本的下一步尚未验收。

## 每个块来自哪里？（父文档归属题已讨论，见 2A-Q4）

切成多个块之后，不能只保存正文，否则无法可靠判断它属于哪份文档、位于哪一段。同一段文字也可能在多份文档中重复出现。

先查看项目已保留的三个层面：`parent_id` 关联父文档，`source` 记录来源标识，`start/end` 定位该版本正文中的字符范围。块自身的 `id` 和 `version` 下一步再展开。

完整小示例，先阅读即可：

```python
from evidencedesk.documents import Document
from evidencedesk.ingest import chunks


doc = Document(
    id="demo", title="分块示例", text="ABCDEFGHIJ", source="demo.md"
)
part = chunks(doc, size=4, overlap=2)[1]

print(part["parent_id"], part["source"])
print(part["start"], part["end"], part["text"])
assert doc.text[part["start"]:part["end"]] == part["text"]
```

输出：

```text
demo demo.md
2 6 CDEF
```

- `[1]` 取列表的第二块，因为 Python 列表索引从 0 开始。
- `parent_id` 对应 `doc.id`，表示所属文档，不是块自身的唯一 ID。
- `source` 沿用 `doc.source`。这是手工对象里的示意文件名，没有打开或创建 demo.md，也不因此证明外部文件真实存在。
- `start=2, end=6` 表示 `doc.text[2:6]`；偏移针对加载后的正文字符串，不是整个 Markdown 文件的字节位置或 PDF 页码。
- 最后的 assert 验证这段切片确实等于块正文。断言通过本身不打印额外一行。
- 原文若更新，单靠旧的 source/start/end 不足以保证仍定位到原来的证据；后续会加入版本概念。

概念题已作答：按问题所指的 parent_id 理解，学习者判断相同的方向正确。导师补充了同一父文档才是依据、块自身 id 在本例不同的区别，见 2A-Q4；不将原答中笼统的 id 自动解读为已完整区分两种标识。

## 在真实手册上定位一个块（实操已完成，见 2A-Q5）

前四题都用手工构造的 `ABCDEFGHIJ`。这一步换成仓库里的真实手册，并第一次使用 `chunks` 的默认参数 `size=120, overlap=20`，做同样的定位验证。

在仓库根目录新建 `scratch_locate.py`：

```python
from pathlib import Path
from evidencedesk.documents import load_documents
from evidencedesk.ingest import chunks

doc = load_documents(Path("data/sample"))[0]
print(doc.id, len(doc.text))

parts = chunks(doc)
print(len(parts), [(p["start"], p["end"]) for p in parts])

part = parts[1]
print(part["parent_id"], part["source"], part["start"], part["end"])
assert doc.text[part["start"]:part["end"]] == part["text"]
```

运行 `python scratch_locate.py`，预期输出：

```text
api-key-policy 243
3 [(0, 120), (100, 220), (200, 243)]
api-key-policy api-key-policy.md 100 220
```

- `load_documents(...)[0]`：阶段 1 的加载器按文件名排序，所以 `[0]` 是 `api-key-policy`，不是 webhook。
- `len(doc.text)`：正文长度 243，是去掉标题行和首尾空白后的字符数，小于文件字节数。
- `chunks(doc)`：没有传参数，使用函数定义中的默认值 `size=120, overlap=20`，步长 100；起点 0、100、200，第三块的 end 已到 243，停止。
- 最后三行与 2A-Q4 的例子相同，只是对象换成了真实文档；断言通过不打印额外一行。
- 默认参数是教学实现的选择，不是最佳分块大小；正文只有 243 字符时每份手册只切 3 块，这正是 2C 要扩充语料的原因之一。块仍未接入 search。

学习者先按公式预测出步长 100、三块及全部区间，再运行确认一致且断言无误，见 2A-Q5。

## 1. 问题：现在为什么需要它？

长文不能整篇塞进每次请求；更新手册时也不能让旧规则继续被检索。我们需要可定位的块、可辨认的版本和可重复的更新操作。

## 2. 原理：在这个问题里理解技术

窗口大小 size 决定局部上下文，overlap 保留边界附近信息，步长=size-overlap。字符数不等于 token 数；分块过小会切断条件和结论，过大则降低检索精度并浪费上下文。

哈希标识正文版本，块 ID 绑定文档、正文版本、分块参数和起点。相同输入重跑不重复，更新时替换父文档全部旧块。这是内存快照演示，不是数据库原子发布；标题/ACL/来源版本还未纳入哈希，生产应单独记录元数据版本。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/ingest.py`

完整源文件：[打开源码](../../src/evidencedesk/ingest.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/ingest.py -->
```python
#: 哈希记录内容版本；JSON 编码复合身份避免拼接歧义。
import hashlib
import json
from .documents import Document

#: 本实现按字符分块，绝非 token 分块；步长必须正，否则可能死循环。
def chunks(doc: Document, size: int = 120, overlap: int = 20) -> list[dict]:
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("要求整数且 0 <= overlap < size")
    version = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
    result = []
    #: 半开区间 [start,end) 可直接定位 Python 字符串；版本变化时全部块 ID 变化。
    for start in range(0, len(doc.text), size - overlap):
        end = min(start + size, len(doc.text))
        identity = json.dumps([doc.id, version, size, overlap, start], ensure_ascii=False)
        chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        result.append({"id": chunk_id, "parent_id": doc.id, "version": version,
                       "source": doc.source, "start": start, "end": end, "text": doc.text[start:end]})
        if end == len(doc.text):
            break
    return result

#: 先剔除该父文档旧块，再合入新块；返回新字典，校验失败也不破坏旧索引。
def replace_document(index: dict[str, dict], doc: Document, size: int = 120) -> dict[str, dict]:
    updated = {key: value for key, value in index.items() if value["parent_id"] != doc.id}
    updated.update({chunk["id"]: chunk for chunk in chunks(doc, size)})
    return updated
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–5 | 哈希记录内容版本；JSON 编码复合身份避免拼接歧义。 |
| 6–11 | 本实现按字符分块，绝非 token 分块；步长必须正，否则可能死循环。 |
| 12–22 | 半开区间 [start,end) 可直接定位 Python 字符串；版本变化时全部块 ID 变化。 |
| 23–27 | 先剔除该父文档旧块，再合入新块；返回新字典，校验失败也不破坏旧索引。 |

### `examples/chunk_versions.py`

完整源文件：[打开源码](../../examples/chunk_versions.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/chunk_versions.py -->
```python
#: replace 为 frozen 数据类创建修改后的副本，而不是原地写入。
from pathlib import Path
from dataclasses import replace
from evidencedesk.documents import load_documents
from evidencedesk.ingest import chunks, replace_document

#: 同样输入重复导入得到同一结果，这是幂等；不是“没有异常”就算幂等。
def main():
    doc = load_documents(Path("data/sample"))[0]
    index = replace_document({}, doc)
    assert replace_document(index, doc) == index
    #: 增加内容会换版本；确认新快照没有旧块，避免过期内容继续被搜到。
    changed = replace(doc, text=doc.text + "\n练习：增加一条说明。")
    new_index = replace_document(index, changed)
    assert set(index).isdisjoint(new_index)
    print({"initial_chunks": len(chunks(doc)), "updated_chunks": len(new_index), "old_chunks_removed": True})

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–6 | replace 为 frozen 数据类创建修改后的副本，而不是原地写入。 |
| 7–11 | 同样输入重复导入得到同一结果，这是幂等；不是“没有异常”就算幂等。 |
| 12–19 | 增加内容会换版本；确认新快照没有旧块，避免过期内容继续被搜到。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m examples.chunk_versions
python -m pytest tests/test_core.py -q
```

### 只做这些关键改动

1. 打开 `examples/chunk_versions.py`，将 print 中 `len(chunks(doc))` 改为 `len(chunks(doc, size=80, overlap=20))`，运行同一命令，比较打印的初始块数。
2. 在 main 的 print 前加入两行：`part = chunks(doc, 80, 20)[0]` 和 `print(part["text"] == doc.text[part["start"]:part["end"]])`；保持 4 空格缩进，运行应显示 True。
3. 按示例追加一句话并重建索引；确认旧 ID 集合与新集合无交集。
4. 将刚加入语句中的 `chunks(doc, 80, 20)` 改为 `chunks(doc, 80, 80)`，预期 ValueError 而非挂死；然后恢复原示例。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

测试覆盖所有字符、最后一块不重复、非法参数、幂等与旧块清理。说明增大 overlap 为什么通常增加冗余，而不是保证检索质量更好。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 如果向量库更新中途失败，如何避免半新半旧？提出“新版本完整写入→切换活动版本→回收旧版本”的方案，并说明仍需事务或一致性机制。

**产出：** 带字符偏移和来源的块、更新语义、分块对照记录。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.python.org/3/library/hashlib.html
- https://docs.langchain.com/oss/python/integrations/splitters/index

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。


## 已完成问答与标准答案

只归档已完成的回答，区分预测和运行反馈，不将单题通过视为整课或阶段 2 完成。

### 2A-Q1：不重叠、每块三个字符时怎样分块？

记录日期：2026-09-17。

**题目：** 文本为 `ABCDEFGHIJ`，调用项目的 chunks 函数，设置 size=3、overlap=0，预测块数、起止位置和内容。

**学习者回答：** “会得到四块”，并给出：

```text
0 3 ABC
3 6 DEF
6 9 GHI
9 10 J
```

**判断：** 正确；块数、全部区间和内容均符合实现。

**标准答案：** 四块，分别为 `[0,3)` 的 ABC、`[3,6)` 的 DEF、`[6,9)` 的 GHI 和 `[9,10)` 的 J。

**标准解析：** overlap=0，所以步长为 size=3，起点依次是 0、3、6、9。终点用 `min(start + size, len(text))` 限制在全文长度 10 内；字符串切片不包含终点。因此前三块各有三个字符，最后不足三个字符的 J 仍被保留，没有补齐或丢弃。

**复习要点：**

- size 是每块字符数上限，不要求每块都恰好一样长。
- start/end 可以定位原文切片；它们不是块编号，也不是字节偏移或 token 编号。
- 本题按 Python 字符串切片解释 ASCII 示例，尚未讨论 token 化、复杂 Unicode 或重叠。

**记录范围：** 本题作答时只记录正确预测，没有实际运行反馈；导师的参考核对不能替代学员实操。后续固定 size=4 的重复量实验另见 2A-Q3，不冒充本题 size=3 的运行记录。


### 2A-Q2：重叠两个字符时怎样移动窗口？

记录日期：2026-09-18。

**题目：** 文本为 `ABCDEFGHIJ`，设置 size=4、overlap=2，预测步长以及全部块的起止位置和内容。

**学习者回答：** “步长为2，会输出下列内容”，并给出：

```text
0 4 ABCD
2 6 CDEF
4 8 EFGH
6 10 GHIJ
```

**判断：** 正确。步长、四个区间、内容以及到末尾停止的结果都符合当前实现。

**标准答案：** 步长 `size - overlap = 4 - 2 = 2`。四个块分别为 `[0,4)` 的 ABCD、`[2,6)` 的 CDEF、`[4,8)` 的 EFGH、`[6,10)` 的 GHIJ。

**标准解析：** 起点每次前进 2 个字符，块大小上限仍为 4；相邻块依次共享 CD、EF、GH。最后一块的 end 已等于全文长度 10，函数执行停止逻辑，因此不会继续生成 `[8,10)` 的 IJ。

**复习要点：** overlap 是相邻块重复保留的字符数，不是起点移动量；起点移动量是 size-overlap。重叠没有修改原文，只让部分原文位置被多个切片包含。

**记录范围：** 本题作答时记录的是预测；后续重复量实验见 2A-Q3。导师独立验证不能替代学习者实操，字符重复量也不等于已测得真实检索质量或模型费用。


### 2A-Q3：为什么重叠不是越大越好？

记录日期：2026-09-18。

**题目与实操：** 执行 `scratch_overlap.py`，固定十字符文本与 size=4，分别取 overlap=0、1、2，比较块数与块内字符总数，并解释取舍。

**学习者反馈：** “三行符合预期，至于为什么不能简单认为overlap越大越好，我觉得这更多的是因为如果overlap太大，那么分块反而就没有意义了，并且消耗的空间也会增大。”

**判断：** 运行反馈符合预期，指出重复与空间代价的方向正确。导师补充修正“分块没有意义”的绝对表述：较大的合法重叠不取消块长约束，只是让相邻块更相似，收益可能不抵新增重复量；不将这一补充冒充学员原句。

**按反馈记录的结果：**

| overlap | 块数 | 各块字符数之和 |
|---|---|---|
| 0 | 3 | 10 |
| 1 | 3 | 12 |
| 2 | 4 | 16 |

**标准解析：** 原文仍为十个字符。重叠越大，步长越小，部分原文位置被更多切片覆盖；重复内容可能增加存储和后续重复处理的负担。它也可能帮助保留边界上下文，因此不能简单认为越小越好或越大越好，需要根据内容、检索质量与成本对照选择。

**术语与证据边界：**

- “分块完全无意义”过于绝对；例如合法的高重叠下，每块仍不超过 size，并没有自动还原成整篇文档。
- 本实验实测的是字符重复量，不是实际字节存储、耗时、token 或费用；空间增加属于重复数据可能带来的负担分析，不能把 16/10 宣称为已测得的计费倍率。
- 重叠不保证完整保留语义，也不能代替语义检索或证据充分性检查。
- 合法参数要求 `0 <= overlap < size`。若 overlap 等于或大于 size，当前函数直接抛出 ValueError；不是先进入一个无限循环再观察效果。

**记录范围：** 学习者反馈运行摘要与解释，导师未独立读取其本机脚本或完整终端日志。2A 的来源、版本与更新仍待学习，q06/q09 的修复状态没有因本实验改变。


### 2A-Q4：同一份文档的各块，parent_id 是否相同？

记录日期：2026-09-18。

**题目：** 同一份 doc 拆出的四个块，它们的 parent_id 应该相同还是不同？为什么？

**学习者回答：** “他们的id相同，因为来源相同。”

**判断：** 按原题所问的 parent_id 理解，判断相同的方向正确。原答使用了笼统的 id，导师补充术语区分，不声称原答已经精确区分了父文档 ID 与块 ID。

**标准答案：** 四个块来自同一个 Document，因此 `parent_id` 均取该对象的 `doc.id`，在示例中都是 `demo`。块自己的 `id` 则用于区分块，在这四个块中各不相同。

**原因需要说准确：** 依据是“属于同一份父文档”，不是单凭 source 字符串相同。代码直接把 `doc.id` 写入 parent_id，并不是从 source 计算 parent_id；手工构造的不同文档可以具有相同 source 而使用不同 doc.id。

**复习对照：**

| 字段 | 回答什么问题 |
|---|---|
| `parent_id` | 这个块属于哪份文档？ |
| `id` | 这是哪一个块？ |
| `source` | 文档的来源标识是什么？ |

**记录范围：** 已讨论父文档归属判断，字段区分由导师补充；未提交本轮来源定位脚本的运行结果，也未开始块 ID 哈希与版本机制的验收。


### 2A-Q5：真实手册用默认参数会切出几块？定位断言是否成立？

记录日期：2026-09-24。

**题目与实操：** 新建 `scratch_locate.py`，用 `load_documents` 读取 `data/sample` 的第一份手册（`api-key-policy`，正文 243 个字符），以 `chunks(doc)` 的默认参数 `size=120, overlap=20` 切块。先预测步长、块数与每块 `(start, end)`，再运行核对第二行输出，并确认 `assert doc.text[start:end] == text` 不报错。

**学习者回答：** "根据公式，步长为100，243个字符的文档在这个分块设置下会切出三块，分别是(0,120), (100,220), (200,243)。运行结果也与预测的一致，并且没有报错。"

**判断：** 完全正确。步长、块数、三个区间均与实现一致；运行反馈与预期输出相符，定位断言成立。

**标准答案：** 步长 `120 − 20 = 100`；三块，分别为 `[0,120)`、`[100,220)`、`[200,243)`；`parts[1]` 的 `parent_id` 为 `api-key-policy`，`source` 为 `api-key-policy.md`，切片 `doc.text[100:220]` 与块正文相同。

**标准解析：** `range(0, 243, 100)` 产生起点 0、100、200；每块 end 取 `min(start + 120, 243)`，得到 120、220、243。第三块的 end 等于全文长度，触发停止规则。相邻块共享 20 个字符（位置 100–119、200–219）。默认参数来自函数签名，调用时不传就生效。

**复习要点：**

- 同一公式在手工样例和真实文档上都成立；变化的只是文本长度与参数。
- `len(doc.text)` 是加载后正文的字符数，不是文件字节数，也不是 token 数。
- 手册正文只有 243 字符、默认参数只切 3 块，说明现有语料对分块和检索实验都太小；这是 [2C](02c-corpus-holdout.md) 要解决的问题，不是本题的错误。
- 块仍未接入 `search`，q06/q09 状态不变。

**记录范围：** 依据学习者的预测与运行反馈记录；导师在参考环境独立复核了相同输出，但未读取学习者本机终端日志。块 `id` 与 `version` 哈希、`replace_document` 幂等更新尚未验收。
