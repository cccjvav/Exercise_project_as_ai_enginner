# 2A · 分块、来源与幂等更新

[全部课程](../course/index.md) · [上一课](01e-evaluation.md) · [下一课](02b-pdf-tokens.md)

- **学习进度：** 进行中；学习者于 2026-09-17 确认进入阶段 2。先理解不重叠字符分块，尚无本课问答或实操验收。
- **前置理解：** 阶段 1；理解文件身份与评测
- **验证状态：** 字符分块与内存快照已测试；不是生产持久化索引。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 当前起步：把长文切成可定位的小段（待完成）

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

概念检查（待回答）：同样的字符串改为 size=3、overlap=0，会得到几块？每块内容是什么？先预测即可，不将未回答题提前归档为已掌握。

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
