# 固定词表检索与命令行入口：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/search.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

实现一个可解释、无模型费用的检索基线；返回候选证据而不是生成答案。

### 输入、输出与调用关系

tokens:字符串→集合；search:问题/Document列表/k→SearchHit列表；main:终端参数→JSON或参数错误。

### 运行与风险边界

`python -m evidencedesk.search --query "Webhook 重试" --k 1`。项目需在当前环境可导入。

关键词覆盖率不是概率，也不判断原文是否含答案。q06/q09 是保留的已知失败；当前模块不执行语义检索。

## 完整源码

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

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: asdict 用于将数据类变为 JSON 可编码的字典；相对导入要求以包方式运行。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：asdict 用于将数据类变为 JSON 可编码的字典；相对导入要求以包方式运行。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
from dataclasses import asdict, dataclass
```

**语法与数据变化：** 从 `dataclasses` 导入 `asdict, dataclass`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 数据类工具。dataclass 自动生成初始化及比较等方法，asdict 转字典，field 控制字段默认值；普通字段类型注解不自动验证输入。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from .documents import Document, load_documents
```

**语法与数据变化：** 从 `.documents` 导入 `Document, load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
#: 固定领域词表是教学基线，不是中文分词器或语义模型；集合去除重复词。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：固定领域词表是教学基线，不是中文分词器或语义模型；集合去除重复词。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L9"></a>
### 第 9 行

```python
TERMS = ("webhook", "重试", "签名", "密钥", "轮换", "工单", "升级", "故障")
```

**语法与数据变化：** 创建固定字符串元组 TERMS，列出八个领域词。

**为什么与边界：** 不是分词模型；只认识列出的子串，未列出的“再发”不会自动等同“重试”。

<a id="L10"></a>
### 第 10 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L11"></a>
### 第 11 行

```python
def tokens(text: str) -> set[str]:
```

**语法与数据变化：** 定义字符串到字符串集合的辅助函数，注解表达预期类型。

**为什么与边界：** 名字 tokens 不意味着模型 token 化，也没有统计词频。

<a id="L12"></a>
### 第 12 行

```python
    return {term for term in TERMS if term in text.casefold()}
```

**语法与数据变化：** 集合推导逐个检查词表项是否出现在 casefold 后的文本里，只收集命中的词。

**为什么与边界：** WEBHOOK 会归一化为 webhook；集合去重，重复提问不抬高词数。这是子串匹配，没有词边界或同义理解。

<a id="L13"></a>
### 第 13 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L14"></a>
### 第 14 行

```python
#: Hit 保留完整原文与来源；score 仅表示词覆盖率，不是回答正确概率。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Hit 保留完整原文与来源；score 仅表示词覆盖率，不是回答正确概率。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L15"></a>
### 第 15 行

```python
@dataclass(frozen=True)
```

**语法与数据变化：** 把 SearchHit 转为冻结数据类，生成初始化和字段比较。

**为什么与边界：** 冻结仅约束普通字段赋值；不会验证 score 范围或证据真假。

<a id="L16"></a>
### 第 16 行

```python
class SearchHit:
```

**语法与数据变化：** 定义候选结果结构，区别于输入 Document。

**为什么与边界：** 结果新增 score，但保留原文与来源，便于人工核对。

<a id="L17"></a>
### 第 17 行

```python
    document_id: str
```

**语法与数据变化：** document_id 指向原文档的 id。

**为什么与边界：** 不是新随机检索ID；评测用它与人工相关文档集合对照。

<a id="L18"></a>
### 第 18 行

```python
    title: str
```

**语法与数据变化：** title 复制输入文档标题。

**为什么与边界：** 用作展示，标题出现关键词也会参与下面的评分。

<a id="L19"></a>
### 第 19 行

```python
    score: float
```

**语法与数据变化：** score 是浮点数形式的查询词覆盖率。

**为什么与边界：** 1.0 只意味着领域词都出现，不代表 100% 可以回答问题。

<a id="L20"></a>
### 第 20 行

```python
    text: str
```

**语法与数据变化：** text 保留正文而非生成摘要。

**为什么与边界：** 候选结果没有自动补充收费等缺失事实。

<a id="L21"></a>
### 第 21 行

```python
    source: str
```

**语法与数据变化：** source 保留可回查的来源标识。

**为什么与边界：** 来源字段存在不等于引用语义已验证。

<a id="L22"></a>
### 第 22 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L23"></a>
### 第 23 行

```python
#: bool 在 Python 是 int 子类，故用 type 而非 isinstance 排除 True/False。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：bool 在 Python 是 int 子类，故用 type 而非 isinstance 排除 True/False。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L24"></a>
### 第 24 行

```python
def search(query: str, documents: list[Document], k: int = 3) -> list[SearchHit]:
```

**语法与数据变化：** 定义检索函数，k 默认3，documents 已是加载后的对象列表。

**为什么与边界：** 函数自身不读取文件，可用手工对象做单元测试；调用者承担加载和权限过滤。

<a id="L25"></a>
### 第 25 行

```python
    if type(k) is not int or k <= 0:
```

**语法与数据变化：** 要求精确 int 且大于0；or 两侧任何违规都拒绝。

**为什么与边界：** bool 是 int 子类，isinstance(True,int) 会为真，所以这里采用 type 精确比较。

<a id="L26"></a>
### 第 26 行

```python
        raise ValueError("k 必须是正整数，不接受布尔值")
```

**语法与数据变化：** 抛 ValueError 说明数量参数非法，拒绝继续计算。

**为什么与边界：** 不能把错误转换成 []，否则下游会误认为正常无命中。

<a id="L27"></a>
### 第 27 行

```python
    query_terms = tokens(query)
```

**语法与数据变化：** 先提取查询中的领域词，结果是去重集合。

**为什么与边界：** 这里没有用 reference_facts 或正确文档ID，避免评测答案泄漏。

<a id="L28"></a>
### 第 28 行

```python
    if not query_terms:
```

**语法与数据变化：** 检查集合是否为空。

**为什么与边界：** 若没有已知领域词，分母会为0，而且无法做此基线的匹配，应先处理。

<a id="L29"></a>
### 第 29 行

```python
        return []
```

**语法与数据变化：** 提前返回空列表，不进入文档评分或 top-k。

**为什么与边界：** 增大 k 无法改变这一分支；空结果只说明没有词表匹配，不证明知识库无答案。

<a id="L30"></a>
### 第 30 行

```python
    #: 交集计算覆盖词数；先处理空集合，才能避免除以零。search 不做文件 I/O。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：交集计算覆盖词数；先处理空集合，才能避免除以零。search 不做文件 I/O。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L31"></a>
### 第 31 行

```python
    hits = []
```

**语法与数据变化：** 建立候选列表，初始为空。

**为什么与边界：** 每次调用独立分配，不会沿用上一次查询的结果。

<a id="L32"></a>
### 第 32 行

```python
    for doc in documents:
```

**语法与数据变化：** 逐个绑定输入文档，原列表不被重排或修改。

**为什么与边界：** 权限若存在应在调用前过滤，不能搜完再让模型决定用户能否看。

<a id="L33"></a>
### 第 33 行

```python
        score = len(query_terms & tokens(doc.title + "\n" + doc.text)) / len(query_terms)
```

**语法与数据变化：** 标题和正文用换行连接后提取词；集合交集数量除以查询词数。

**为什么与边界：** 问题两词、文档仅含一词得到0.5；分母不是文档长度、返回数量或 Jaccard 并集。

<a id="L34"></a>
### 第 34 行

```python
        if score > 0:
```

**语法与数据变化：** 仅保留正分候选。

**为什么与边界：** 零分文档不用于凑满 k；请求 k=3 可以只得到一条或零条。

<a id="L35"></a>
### 第 35 行

```python
            hits.append(SearchHit(doc.id, doc.title, score, doc.text, doc.source))
```

**语法与数据变化：** 把原文档字段和分数装进 SearchHit，再追加到候选列表。

**为什么与边界：** 构造顺序对应数据类字段，不能把 source 和 text 互换；不在这里生成答案。

<a id="L36"></a>
### 第 36 行

```python
    #: 负号实现降序；同分时按 ID 升序。不原地排序输入，调用方数据不会改变。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：负号实现降序；同分时按 ID 升序。不原地排序输入，调用方数据不会改变。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L37"></a>
### 第 37 行

```python
    return sorted(hits, key=lambda hit: (-hit.score, hit.document_id))[:k]
```

**语法与数据变化：** sorted 生成新列表；负分值使高分先排，同分再比较文档ID；最后 [:k] 截取上限。

**为什么与边界：** 唯一ID打破平局使顺序可复现。排序稳定性本身只保证相同键保留输入顺序，不能代替显式次级键。

<a id="L38"></a>
### 第 38 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L39"></a>
### 第 39 行

```python
#: argparse 将终端字符串解析成类型化参数；默认数据目录相对于当前工作目录。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：argparse 将终端字符串解析成类型化参数；默认数据目录相对于当前工作目录。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L40"></a>
### 第 40 行

```python
def main() -> None:
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L41"></a>
### 第 41 行

```python
    parser = argparse.ArgumentParser(description="返回候选证据，不生成答案")
```

**语法与数据变化：** 创建 argparse 解析器并提供用途描述。

**为什么与边界：** description 会出现在帮助信息，不实施检索或事实校验。

<a id="L42"></a>
### 第 42 行

```python
    parser.add_argument("--query", required=True)
```

**语法与数据变化：** 注册必填 --query 参数，默认保留字符串类型。

**为什么与边界：** 缺失时 argparse 报错；提供空字符串仍可能走 tokens 的空集合分支。

<a id="L43"></a>
### 第 43 行

```python
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
```

**语法与数据变化：** 注册数据目录，type=Path 实际把参数字符串转成 Path，默认相对路径 data/sample。

**为什么与边界：** 相对路径以当前工作目录解释，不是自动以源码位置解释。

<a id="L44"></a>
### 第 44 行

```python
    parser.add_argument("--k", type=int, default=3)
```

**语法与数据变化：** 注册 --k，用 int 转换字符串，缺省3。

**为什么与边界：** int("0") 合法，但不是正整数；范围仍由 search 校验，int("abc") 则在解析阶段失败。

<a id="L45"></a>
### 第 45 行

```python
    args = parser.parse_args()
```

**语法与数据变化：** 读取当前进程的命令行参数，返回 Namespace，字段通过 args.query 等访问。

**为什么与边界：** --help 会正常显示帮助并退出，非法格式会在进入业务 try 之前结束。

<a id="L46"></a>
### 第 46 行

```python
    #: 文件与参数错误写入 stderr 并以非零状态退出；成功输出只有可解析 JSON。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：文件与参数错误写入 stderr 并以非零状态退出；成功输出只有可解析 JSON。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L47"></a>
### 第 47 行

```python
    try:
```

**语法与数据变化：** 进入文件加载和检索的错误处理范围。

**为什么与边界：** 不是吞掉所有异常；仅下方明确列出的异常被转为参数错误。

<a id="L48"></a>
### 第 48 行

```python
        hits = search(args.query, load_documents(args.data_dir), args.k)
```

**语法与数据变化：** 先加载目录，再调用 search，最后把结果赋给 hits。

**为什么与边界：** Python 先计算实参；目录损坏可能先于 k 范围错误发生，不能断言非法 k 永远是第一个报错。

<a id="L49"></a>
### 第 49 行

```python
    except (OSError, ValueError) as exc:
```

**语法与数据变化：** 捕获文件类 OSError 及输入类 ValueError，把实例绑定 exc。

**为什么与边界：** TypeError 等不在列表内会继续向上抛；这不是通用故障兜底。

<a id="L50"></a>
### 第 50 行

```python
        parser.error(str(exc))
```

**语法与数据变化：** 将异常文本交给 parser.error，输出 usage/错误到 stderr，并以退出码2退出。

**为什么与边界：** 它不会像普通 print 一样继续到下面的 JSON 成功输出。

<a id="L51"></a>
### 第 51 行

```python
    print(json.dumps([asdict(hit) for hit in hits], ensure_ascii=False, indent=2))
```

**语法与数据变化：** asdict 将各个数据类转成字典，json.dumps 编码整个列表；保留中文、缩进2空格后 print。

**为什么与边界：** 只有成功路径到此；正常无命中输出 [] 且退出0，而不是错误。输出合法JSON也不证明候选支持答案。

<a id="L52"></a>
### 第 52 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L53"></a>
### 第 53 行

```python
#: 导入模块不会执行 CLI；运行 python -m evidencedesk.search 才进入 main。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：导入模块不会执行 CLI；运行 python -m evidencedesk.search 才进入 main。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L54"></a>
### 第 54 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L55"></a>
### 第 55 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

问题 WEBHOOK 重试 重试 得到 {webhook,重试}。含两词的文档 score=1，只含一词为0.5。词表外表达返回空；非法 k 必须在空问题/空语料时仍拒绝。

## 只练一个关键点（不是新的学习验收记录）

1. 运行本页查询，再把同一词重复一次，比较ID和score。
2. 用test_scores_order_and_no_mutation核对输入倒序与同分排序；保持语料和k不变。
3. **复盘：** 重复词不抬分、增大k不创造候选分别在哪一行保证？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
