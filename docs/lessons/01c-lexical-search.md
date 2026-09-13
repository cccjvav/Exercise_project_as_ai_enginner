# 1C · 词覆盖检索与稳定排序

[全部课程](../course/index.md) · [上一课](01b-structured-loading.md) · [下一课](01d-cli-tests.md)

- **学习进度：** 进行中；领域词提取的大小写归一化与集合去重题已答对。评分、排序和检索实操尚未验收。
- **前置理解：** 1B：能读取 Document 列表
- **验证状态：** 离线参考实现；已纳入 pytest。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

支持人员输入“Webhook 重试”，我们需要得到候选原文和来源，先不让模型生成任何答案。否则无法区分“依据没找对”和“回答编造了”。

## 2. 原理：在这个问题里理解技术

查询词集合 Q 与文档词集合 D 的交集大小，除以 |Q|，得到覆盖率。集合天然去重；casefold 统一大小写；空 Q 直接返回空列表，避免除零。固定词表是刻意弱的对照组。

只保留正分结果，按 (-score, document_id) 排序，前 k 条形成候选。负号改变排序方向，ID 打破平局。score=1 只代表词都出现，不代表答案存在。源码后半部分 CLI 在 1D 展开，本课先聚焦 tokens/search。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/search.py`

完整源文件：[打开源码](../../src/evidencedesk/search.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: src/evidencedesk/search.py -->
```python
#: asdict 用于将数据类变为 JSON 可编码的字典；相对导入要求以包方式运行。
import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from .documents import Document, load_documents

#: 固定领域词表是教学基线，不是中文分词器或语义模型；集合去除重复词。
TERMS = ("webhook", "重试", "签名", "密钥", "轮换", "工单", "升级", "故障")

def tokens(text: str) -> set[str]:
    return {term for term in TERMS if term in text.casefold()}

#: Hit 保留完整原文与来源；score 仅表示词覆盖率，不是回答正确概率。
@dataclass(frozen=True)
class SearchHit:
    document_id: str
    title: str
    score: float
    text: str
    source: str

#: bool 在 Python 是 int 子类，故用 type 而非 isinstance 排除 True/False。
def search(query: str, documents: list[Document], k: int = 3) -> list[SearchHit]:
    if type(k) is not int or k <= 0:
        raise ValueError("k 必须是正整数，不接受布尔值")
    query_terms = tokens(query)
    if not query_terms:
        return []
    #: 交集计算覆盖词数；先处理空集合，才能避免除以零。search 不做文件 I/O。
    hits = []
    for doc in documents:
        score = len(query_terms & tokens(doc.title + "\n" + doc.text)) / len(query_terms)
        if score > 0:
            hits.append(SearchHit(doc.id, doc.title, score, doc.text, doc.source))
    #: 负号实现降序；同分时按 ID 升序。不原地排序输入，调用方数据不会改变。
    return sorted(hits, key=lambda hit: (-hit.score, hit.document_id))[:k]

#: argparse 将终端字符串解析成类型化参数；默认数据目录相对于当前工作目录。
def main() -> None:
    parser = argparse.ArgumentParser(description="返回候选证据，不生成答案")
    parser.add_argument("--query", required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()
    #: 文件与参数错误写入 stderr 并以非零状态退出；成功输出只有可解析 JSON。
    try:
        hits = search(args.query, load_documents(args.data_dir), args.k)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps([asdict(hit) for hit in hits], ensure_ascii=False, indent=2))

#: 导入模块不会执行 CLI；运行 python -m evidencedesk.search 才进入 main。
if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–7 | asdict 用于将数据类变为 JSON 可编码的字典；相对导入要求以包方式运行。 |
| 8–13 | 固定领域词表是教学基线，不是中文分词器或语义模型；集合去除重复词。 |
| 14–22 | Hit 保留完整原文与来源；score 仅表示词覆盖率，不是回答正确概率。 |
| 23–29 | bool 在 Python 是 int 子类，故用 type 而非 isinstance 排除 True/False。 |
| 30–35 | 交集计算覆盖词数；先处理空集合，才能避免除以零。search 不做文件 I/O。 |
| 36–38 | 负号实现降序；同分时按 ID 升序。不原地排序输入，调用方数据不会改变。 |
| 39–45 | argparse 将终端字符串解析成类型化参数；默认数据目录相对于当前工作目录。 |
| 46–52 | 文件与参数错误写入 stderr 并以非零状态退出；成功输出只有可解析 JSON。 |
| 53–55 | 导入模块不会执行 CLI；运行 python -m evidencedesk.search 才进入 main。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m evidencedesk.search --query "Webhook 重试多少次？" --k 1
python -m evidencedesk.search --query "消息没送到还会再发吗？" --k 3
```

### 只做这些关键改动

1. 不改词表，先运行上面两条命令。
2. 将第一条问题中的“重试”重复三次，再运行；预期分数仍为 1。
3. 将第二条 k 改成 10；预期仍为 []，因为没有任何查询词。
4. 再问“Webhook 年付折扣是多少？”；会命中文档，但文档没有价格依据。记录这一反例。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

给定 Q={webhook,重试}，文档仅含重试时手算分数 0.5。解释增大 k 为何不能解决零候选；不要把固定算法失败修成针对题目的 if 答案映射。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 关键词出现与证据支持回答之间差了什么？下一步应该改善召回，还是立即加入生成模型？

**产出：** 可运行检索器、三种失败/边界观察、分数的准确解释。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
- https://docs.python.org/3/howto/sorting.html

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。


## 已完成问答与标准答案

记录日期：2026-09-13。这里只归档已讨论并正确作答的题；单题通过不代表整节 1C 已完成。

### 1C-Q1：重复的查询词会被保留几次？

**题目：** 使用以下固定领域词提取逻辑，若问题是 `"WEBHOOK 重试 重试 重试"`，`sorted(tokens(query))` 会输出什么？

```python
TERMS = (
    "webhook", "重试", "签名", "密钥",
    "轮换", "工单", "升级", "故障",
)

def tokens(text: str) -> set[str]:
    return {
        term
        for term in TERMS
        if term in text.casefold()
    }

query = "WEBHOOK 重试 重试 重试"
print(sorted(tokens(query)))
```

**学习者回答：** “应该是 `['webhook', '重试']`。”

**判断：** 正确。

**标准答案：**

```text
['webhook', '重试']
```

**标准解析：**

1. `casefold()` 将 `WEBHOOK` 归一化为 `webhook`，从而能匹配小写词表项。
2. 函数遍历的是固定词表，检查每个词是否作为子串出现，而不是扫描并统计文本中的每一次出现。
3. 返回值是集合，相同词只保留一份。因此重复三次“重试”不产生三个元素。
4. `sorted()` 将集合转换为稳定排序的列表，便于显示；集合本身不提供可依赖的显示顺序。

**复习要点：** 这个词覆盖基线只关心词是否出现，不使用出现次数。重复关键词不会增加查询词集合的大小，也不应据此提高覆盖率分数。它不是完整中文分词器，也不是语义模型。
