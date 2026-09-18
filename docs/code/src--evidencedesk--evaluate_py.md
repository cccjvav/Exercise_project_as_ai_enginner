# 固定题集评测与指标分组：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/evaluate.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

对同一语料和固定题集记录逐题结果及汇总指标，避免只展示成功示例。

### 输入、输出与调用关系

rows 是已解析的题目字典列表；documents 是语料；返回含 k/recall/mrr/空返回率/details 的字典。

### 运行与风险边界

`python -m evidencedesk.evaluate --k 1`；固定九题回归使用 `--questions data/regression/phase1-v1.jsonl --k 3`。

当前调用词检索器，不自动接入向量管道；公开开发题不是冻结留出集。读取或 JSON 格式错误未像 search CLI 那样统一包装为 parser.error。

## 完整源码

<!-- source: src/evidencedesk/evaluate.py -->
```python
#: mean 做宏平均；评测依赖检索，但不能把金标准输入给检索器。
import argparse
import json
from pathlib import Path
from statistics import mean
from .documents import load_documents
from .search import search

#: 即使评测集为空也要校验 k；None 在 JSON 中会变成 null，表示无定义。
def evaluate(rows: list[dict], documents: list, k: int) -> dict:
    if type(k) is not int or k <= 0:
        raise ValueError("k 必须是正整数")
    recalls, ranks, empty_returns, details = [], [], [], []
    known = {doc.id for doc in documents}
    seen = set()
    for row in rows:
        gold = set(row["relevant_document_ids"])
        if row["id"] in seen or not gold <= known or bool(gold) != row["answerable"]:
            raise ValueError(f"{row['id']}: 重复 ID、未知文档或标注不一致")
        seen.add(row["id"])
        #: 检索只接收 question；reference_facts 不参与检索，防止答案泄漏。
        hits = search(row["question"], documents, k)
        retrieved = [hit.document_id for hit in hits]
        recall = len(gold & set(retrieved)) / len(gold) if gold else None
        if gold:
            recalls.append(recall)
            rank = next((i for i, doc_id in enumerate(retrieved, 1) if doc_id in gold), None)
            ranks.append(1 / rank if rank else 0)
        else:
            empty_returns.append(not retrieved)
        #: 保存逐题结果比只看均值更容易定位失败。
        details.append({"id": row["id"], "retrieved": retrieved,
                        "scores": [hit.score for hit in hits], "recall": recall})
    return {"k": k, "recall": mean(recalls) if recalls else None,
            "mrr": mean(ranks) if ranks else None,
            "unanswerable_empty_rate": mean(empty_returns) if empty_returns else None,
            "details": details}

#: JSONL 每行一个对象；从根目录运行，切换 k 时保留相同数据与代码版本。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=Path("data/questions.jsonl"))
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--k", type=int, default=1)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.questions.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(evaluate(rows, load_documents(args.data_dir), args.k), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: mean 做宏平均；评测依赖检索，但不能把金标准输入给检索器。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：mean 做宏平均；评测依赖检索，但不能把金标准输入给检索器。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import argparse
```

**语法与数据变化：** 导入 `argparse` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库命令行解析器。它把终端字符串按参数规则转换，type=int 是实际调用整数转换，而不是类型注解。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

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
from statistics import mean
```

**语法与数据变化：** 从 `statistics` 导入 `mean`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库统计函数。这里 mean 按参与元素数求算术平均；空列表不应直接求均值，下面代码必须单独处理。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from .documents import load_documents
```

**语法与数据变化：** 从 `.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from .search import search
```

**语法与数据变化：** 从 `.search` 导入 `search`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** search用固定领域词覆盖率返回排序的SearchHit候选；不是模型生成或语义检索。权限过滤应在调用之前完成。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L9"></a>
### 第 9 行

```python
#: 即使评测集为空也要校验 k；None 在 JSON 中会变成 null，表示无定义。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：即使评测集为空也要校验 k；None 在 JSON 中会变成 null，表示无定义。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L10"></a>
### 第 10 行

```python
def evaluate(rows: list[dict], documents: list, k: int) -> dict:
```

**语法与数据变化：** 定义 evaluate，接收字典题集、文档列表和 k，返回报告字典。

**为什么与边界：** 参数注解未严格约束每个字典字段；下面只验证一部分标注契约，缺键仍可能抛 KeyError。

<a id="L11"></a>
### 第 11 行

```python
    if type(k) is not int or k <= 0:
```

**语法与数据变化：** 即使题集为空也先拒绝非法 k；精确 int 排除布尔值。

**为什么与边界：** 若把校验只放在 search，空题集时不会调用 search，就可能错误接受 k=0。

<a id="L12"></a>
### 第 12 行

```python
        raise ValueError("k 必须是正整数")
```

**语法与数据变化：** 抛 ValueError 终止评测，避免给非法配置生成看似正常的报告。

**为什么与边界：** 错误不是一个零分评测结果。

<a id="L13"></a>
### 第 13 行

```python
    recalls, ranks, empty_returns, details = [], [], [], []
```

**语法与数据变化：** 用四个不同列表分别积累单题Recall、RR、无答案空返回标志和逐题详情。

**为什么与边界：** 逗号解包不是四个名称指向同一个列表，不会互相污染。

<a id="L14"></a>
### 第 14 行

```python
    known = {doc.id for doc in documents}
```

**语法与数据变化：** 从真实语料对象建立所有合法文档ID的集合。

**为什么与边界：** 标注若指向不存在文档，要报输入问题，而不是把检索器记成失败。

<a id="L15"></a>
### 第 15 行

```python
    seen = set()
```

**语法与数据变化：** seen 记录已处理题目ID，用集合高效查重。

**为什么与边界：** 重复题会改变统计权重，因此不能默默重复计分。

<a id="L16"></a>
### 第 16 行

```python
    for row in rows:
```

**语法与数据变化：** 依次读取每一道题，不按检索结果预先过滤失败题。

**为什么与边界：** 题集组成必须固定，否则指标不能公平比较。

<a id="L17"></a>
### 第 17 行

```python
        gold = set(row["relevant_document_ids"])
```

**语法与数据变化：** 把该题的相关文档ID转成集合 gold，去重后用于交集。

**为什么与边界：** gold 来自人工标注，不是检索器分数；此字段不会传给 search。

<a id="L18"></a>
### 第 18 行

```python
        if row["id"] in seen or not gold <= known or bool(gold) != row["answerable"]:
```

**语法与数据变化：** 拒绝重复题ID、gold 不属于语料全集，或 gold 是否非空与 answerable 不一致。

**为什么与边界：** 这里不是完整JSON schema：比如不严格验证 answerable 的 bool 类型、题目文本类型等，调用方仍需可信数据。

<a id="L19"></a>
### 第 19 行

```python
            raise ValueError(f"{row['id']}: 重复 ID、未知文档或标注不一致")
```

**语法与数据变化：** 标注不一致时抛错并指出题ID。

**为什么与边界：** 不能为了得到分数而丢弃坏行，应该修正数据并记录版本。

<a id="L20"></a>
### 第 20 行

```python
        seen.add(row["id"])
```

**语法与数据变化：** 当前题ID加入 seen，供下一题判重。

**为什么与边界：** 必须先通过校验再加入；此集合仅在当前评测调用中存在。

<a id="L21"></a>
### 第 21 行

```python
        #: 检索只接收 question；reference_facts 不参与检索，防止答案泄漏。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：检索只接收 question；reference_facts 不参与检索，防止答案泄漏。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L22"></a>
### 第 22 行

```python
        hits = search(row["question"], documents, k)
```

**语法与数据变化：** 只把 question、语料、k 交给检索器。

**为什么与边界：** reference_facts 和 gold 留在评测侧，防止用答案引导检索而夸大效果。

<a id="L23"></a>
### 第 23 行

```python
        retrieved = [hit.document_id for hit in hits]
```

**语法与数据变化：** 从命中对象提取文档ID列表，保持排序。

**为什么与边界：** 排名计算需要列表顺序，不能先整体转成集合丢失位置。

<a id="L24"></a>
### 第 24 行

```python
        recall = len(gold & set(retrieved)) / len(gold) if gold else None
```

**语法与数据变化：** gold 非空时计算 |gold∩retrieved|/|gold|，否则设 None。

**为什么与边界：** Recall分母是相关文档数，不是k；无答案题分母为0，不能伪造0或1替代未定义。

<a id="L25"></a>
### 第 25 行

```python
        if gold:
```

**语法与数据变化：** gold 非空进入可回答组。

**为什么与边界：** 分组由人工标注决定，不取决于是否检索成功。

<a id="L26"></a>
### 第 26 行

```python
            recalls.append(recall)
```

**语法与数据变化：** 把本题Recall加入可回答组列表，包括0。

**为什么与边界：** 漏检题不能删除，否则均值产生成功样本偏差。

<a id="L27"></a>
### 第 27 行

```python
            rank = next((i for i, doc_id in enumerate(retrieved, 1) if doc_id in gold), None)
```

**语法与数据变化：** enumerate 从1编号，生成器筛选相关ID；next 只取第一个，没找到返回None。

**为什么与边界：** 这是“第一份相关结果”的排名，不是所有相关排名之和；从0开始会导致倒数无定义。

<a id="L28"></a>
### 第 28 行

```python
            ranks.append(1 / rank if rank else 0)
```

**语法与数据变化：** 有排名则记录1/rank，未找到记0。

**为什么与边界：** 这些0仍参与MRR平均。这里 rank 真值判断依赖排名从1开始。

<a id="L29"></a>
### 第 29 行

```python
        else:
```

**语法与数据变化：** else 对应 gold 为空，即无答案题。

**为什么与边界：** 不是说所有检索返回空的题都进入这一组。

<a id="L30"></a>
### 第 30 行

```python
            empty_returns.append(not retrieved)
```

**语法与数据变化：** not retrieved 在空列表时为True，否则False，追加到无答案组。

**为什么与边界：** mean 会把True/False当作1/0求平均；这是空返回率，不是生成拒答准确率。

<a id="L31"></a>
### 第 31 行

```python
        #: 保存逐题结果比只看均值更容易定位失败。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：保存逐题结果比只看均值更容易定位失败。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L32"></a>
### 第 32 行

```python
        details.append({"id": row["id"], "retrieved": retrieved,
```

**语法与数据变化：** 开始追加逐题字典，保留题ID与有序返回ID列表。

**为什么与边界：** 这行与下一行是同一个 append 调用；详情用于从均值回到失败个案。

<a id="L33"></a>
### 第 33 行

```python
                        "scores": [hit.score for hit in hits], "recall": recall})
```

**语法与数据变化：** 补充每个候选的词覆盖分数和本题Recall，再闭合调用。

**为什么与边界：** scores 是检索器分数，recall 是人工金标准指标，二者不能互换；None 最后会编码为 null。

<a id="L34"></a>
### 第 34 行

```python
    return {"k": k, "recall": mean(recalls) if recalls else None,
```

**语法与数据变化：** 报告先记录k与可回答Recall宏平均，列表为空则给None。

**为什么与边界：** 宏平均先逐题算再平均，相关文档数量不同的题也各占一份；不能直接合并分子分母充当它。

<a id="L35"></a>
### 第 35 行

```python
            "mrr": mean(ranks) if ranks else None,
```

**语法与数据变化：** ranks 列表保存RR，mean 得到MRR；没有可回答题时给None。

**为什么与边界：** 变量名虽叫 ranks，元素实际上已是倒数排名，这一点读公式时要分清。

<a id="L36"></a>
### 第 36 行

```python
            "unanswerable_empty_rate": mean(empty_returns) if empty_returns else None,
```

**语法与数据变化：** 对无答案题的布尔标志求均值，没有此类题时给None。

**为什么与边界：** 空返回率1可能来自永远返回空的坏检索器，必须联合看可回答题指标。

<a id="L37"></a>
### 第 37 行

```python
            "details": details}
```

**语法与数据变化：** 把逐题详情放入报告并结束字典返回。

**为什么与边界：** 不在这里写磁盘，CLI 会负责将此对象序列化。

<a id="L38"></a>
### 第 38 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L39"></a>
### 第 39 行

```python
#: JSONL 每行一个对象；从根目录运行，切换 k 时保留相同数据与代码版本。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：JSONL 每行一个对象；从根目录运行，切换 k 时保留相同数据与代码版本。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L40"></a>
### 第 40 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L41"></a>
### 第 41 行

```python
    parser = argparse.ArgumentParser()
```

**语法与数据变化：** 创建命令行参数解析器。

**为什么与边界：** 此评测入口与search入口各自解析自己的参数，不共享同一个 Namespace。

<a id="L42"></a>
### 第 42 行

```python
    parser.add_argument("--questions", type=Path, default=Path("data/questions.jsonl"))
```

**语法与数据变化：** 设置题集路径及默认 JSONL 文件，type=Path 做实际转换。

**为什么与边界：** JSONL 每行一个对象，不是一个顶层JSON数组。

<a id="L43"></a>
### 第 43 行

```python
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
```

**语法与数据变化：** 设置语料目录，默认仍是 data/sample。

**为什么与边界：** 比较不同k时保持这个目录和题集不变，才有可比性。

<a id="L44"></a>
### 第 44 行

```python
    parser.add_argument("--k", type=int, default=1)
```

**语法与数据变化：** 注册整数k，默认1。

**为什么与边界：** 解析整数不保证为正；evaluate 函数仍执行业务范围检查。

<a id="L45"></a>
### 第 45 行

```python
    args = parser.parse_args()
```

**语法与数据变化：** 解析终端参数，得到题集路径、目录和k。

**为什么与边界：** 调用入口时省略必选配置可能使用默认文件，需记录实际参数避免误比。

<a id="L46"></a>
### 第 46 行

```python
    rows = [json.loads(line) for line in args.questions.read_text(encoding="utf-8").splitlines() if line.strip()]
```

**语法与数据变化：** UTF-8读取全部题集，拆行、过滤空白行，对每行 json.loads。

**为什么与边界：** 内容损坏会抛解析错误，重复ID由evaluate检测；这里只适合小型开发题集，不是流式大数据加载。

<a id="L47"></a>
### 第 47 行

```python
    print(json.dumps(evaluate(rows, load_documents(args.data_dir), args.k), ensure_ascii=False, indent=2))
```

**语法与数据变化：** 先加载文档，再评测，再把结果编码为保留中文的缩进JSON并打印。

**为什么与边界：** 代码只输出报告，不产生答案；没有捕获所有异常，也不应因stdout可打印就称评测质量良好。

<a id="L48"></a>
### 第 48 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L49"></a>
### 第 49 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L50"></a>
### 第 50 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

原八题含6道可回答、2道无答案，k=1/3 的参考 Recall/MRR=5/6。加q09后可回答指标不变，无答案空返回率=2/3；改变题集不等于算法退步。

## 只练一个关键点（不是新的学习验收记录）

1. 分别运行原八题与data/regression/phase1-v1.jsonl九题，保持k=3。
2. 并排核对题目条数、可回答指标和无答案空返回率；q06/q09详情保留。
3. **复盘：** 题集人口改变与检索算法改变怎样区分？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
