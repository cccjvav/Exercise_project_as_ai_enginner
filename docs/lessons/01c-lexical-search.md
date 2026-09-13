# 1C · 词覆盖检索与稳定排序

[全部课程](../course/index.md) · [上一课](01b-structured-loading.md) · [下一课](01d-cli-tests.md)

- **学习进度：** 进行中；领域词提取与集合去重题、查询词覆盖率计算题已答对。高分不等于证据充分的对照实操已反馈正确；按分数与唯一 ID 排序的顺序不变性题已答对；top-k 与其余检索边界尚未验收。
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


## 分步跟做补充：高覆盖率与证据充分性（已完成，保留步骤供复习）

这次直接使用仓库已有检索器，不修改词表或手册。保持之前的 Python 环境，在仓库根目录分别运行：

```bash
python -m evidencedesk.search --query "Webhook 重试多少次？" --k 1
python -m evidencedesk.search --query "Webhook 重试收费多少？" --k 1
```

- `--query` 指定问题；`--k 1` 最多返回一份候选文档，不是“生成一个答案”。
- 观察两次输出的 `document_id`、`score` 与原文 `text`。其他字段暂时不必修改。
- 按固定词表，两次都提取 `webhook` 和 `重试`，预期返回 `webhook-delivery`，分数均为 `1.0`。这是教学预期；本轮学习者已反馈相同结果，见 1C-Q3。
- 逐项检查原文能否分别支持“重试次数”和“重试收费”的回答。程序当前只返回候选原文，不会自动判定它是否足以回答。

本轮已收到两次分数及证据判断的反馈，标准解析见 1C-Q3。复习时可重新运行，只需对照摘要，不必贴完整 JSON。不要补写不存在的价格信息来让两个问题都可回答。

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


### 1C-Q2：文档覆盖全部查询词时，分数是多少？

**题目：** 给定下面的集合，按查询词覆盖率公式计算分数，并解释分子、分母：

```python
query_terms = {"webhook", "重试"}
doc_terms = {"webhook", "重试", "密钥", "轮换"}

matched_terms = query_terms & doc_terms
score = len(matched_terms) / len(query_terms)
```

**学习者回答：** “分数是1，因为分母与分子相同。”

**判断：** 正确。这里相同的是分子、分母的数值，均为 2，不是说查询集合与文档集合完全相同。

**标准答案：** `score = 2 / 2 = 1.0`。

| 项目 | 本题中的值 |
|---|---|
| 查询词集合 | `{"webhook", "重试"}`，共 2 个不同词 |
| 文档词集合 | `{"webhook", "重试", "密钥", "轮换"}`，共 4 个不同词 |
| 交集 `query_terms & doc_terms` | `{"webhook", "重试"}`，共 2 个词 |
| 分子 | 匹配到的查询词数：2 |
| 分母 | 查询词总数：2，而不是文档词数 4 |
| 分数 | `1.0` |

**复习要点：** 文档额外包含其他词，不会改变本公式的分母。这个分数是查询词覆盖率，不是 Jaccard 相似度，也不是答案正确概率。高分说明这些查询词出现了，不能仅凭它断定原文足以回答完整问题。


### 1C-Q3：两个问题都得 1 分，就都能回答吗？

**实操：** 分别查询“Webhook 重试多少次？”与“Webhook 重试收费多少？”，比较 `document_id`、`score` 和原文 `text`。

**学习者反馈：** “两次分数都为1，但是只有第一个问题能被回答，第二个问题提到的花费则并没有依据可以参考。”

**判断：** 正确。依据学习者的运行反馈与原文判断，评分边界对照实操通过；不将其等同于排序、全部检索用例或整个 1C 已验收。

**标准答案：** 两次都返回 `webhook-delivery`，分数均为 `1.0`，但只有第一个问题有明确回答依据。原文规定最多执行 3 次重试，不包含首次投递；原文没有给出重试收费规则，不能由这份资料确定费用。

| 问题 | 当前词表提取结果 | 分数 | 原文能支持什么 |
|---|---|---|---|
| Webhook 重试多少次？ | `{"webhook", "重试"}` | `1.0` | 最多 3 次重试，不包含首次投递 |
| Webhook 重试收费多少？ | `{"webhook", "重试"}` | `1.0` | 没有收费依据，不能推断价格或是否免费 |

**标准解析：** 当前固定词表没有表达“次数”和“收费”的区别，因此两个完整含义不同的问题被映射成了相同的查询词集合。文档覆盖这两个词，均得 `2 / 2 = 1.0`。这个计算只检查词出现与否，没有验证原文是否包含完整问题所需的事实。

**复习要点：**

- 区分“检索到词语相关的候选文档”和“证据足以支持回答”。
- `score = 1.0` 不是 100% 正确概率，也不是系统已经回答了问题。
- “资料没写收费”不能推导为“免费”，也不能推导为“收费”。正确表述是当前证据不足。
- 第一阶段检索器只返回候选原文；后续生成与证据充分性检查需要单独设计、测试，不能直接让最高分替代事实判断。


### 1C-Q4：打乱输入顺序，会改变前两名吗？

**题目：** 给定三个候选结果，只打乱它们在 `hits` 中的初始顺序，分数和 ID 都不改。按照以下规则排序并取前两项，结果是否变化？

```python
hits = [
    {"document_id": "doc-c", "score": 0.5},
    {"document_id": "doc-b", "score": 1.0},
    {"document_id": "doc-a", "score": 0.5},
]

def sort_key(hit):
    return (-hit["score"], hit["document_id"])

ranked = sorted(hits, key=sort_key)
top_hits = ranked[:2]
```

**学习者回答：** “不应该变化，因为初始顺序不影响最终排序。”

**判断：** 在本题规则和数据下正确；不能将结论推广成“任意排序都不受输入顺序影响”。

**标准答案：** 前两名仍是 `doc-b`（1.0）、`doc-a`（0.5）。先按分数降序，`doc-b` 排第一；`doc-a` 和 `doc-c` 同分，再按 ID 升序，`doc-a` 排在 `doc-c` 前。由于本题的 ID 各不相同，组合排序键能确定每份候选的位置。

**需要区分的两个概念：**

- **用完整规则获得可复现的结果：** 本题显式使用分数与唯一 ID，避免同分结果仅由输入顺序决定。
- **Python 排序的稳定性：** `sorted()` 对排序键完全相同的元素保留原来的相对顺序。因此，如果只按分数排序，同分的 `doc-a`、`doc-c` 的次序可能随输入顺序改变；如果分数和 ID 都相同，也不能仅靠这两个字段消除其他差异。

**复习要点：** 当前加载器按文件名生成文档 ID，同一目录中文档 ID 唯一，所以用 ID 打破同分平局能提供确定顺序。此规则不是认为字母靠前的文档语义上更相关，只是为了同分时可复现。
