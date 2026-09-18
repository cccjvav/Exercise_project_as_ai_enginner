# 真实检索变体实验的外部依赖与数据流：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/live_variants.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

将离线fixture替换为实际嵌入、LLM改写和cross-encoder，但要求模型版本与实验条件可追溯。

### 输入、输出与调用关系

本地手册与问题→规范化向量、多查询排名、RRF和重排结果。

### 运行与风险边界

只在阶段4B、依赖与模型资源已确认时运行 `python -m examples.live_variants`。读取LOCAL_EMBEDDING_MODEL/REVISION、RERANK_MODEL/REVISION、CHAT_MODEL等配置；不是默认离线命令。

会下载模型、占内存并可能调用收费聊天API；本轮未运行。源码未实现完整自动指标对照或费用硬上限，fixture不能替代这些验证。

## 完整源码

<!-- source: examples/live_variants.py -->
```python
#: 4B 的真实模型对照扩展：需要下载本地模型、配置在线查询改写模型；未默认运行。
import os
from pathlib import Path
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_openai import ChatOpenAI
from evidencedesk.documents import load_documents
from evidencedesk.hybrid import rrf

#: 改写数量受限，包含原查询作保底；结构化格式不保证改写保持原意。
class Queries(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=2)

#: 显式模型名和 revision 使模型选择可追溯；下载前检查许可证、内存与网络费用。
def main():
    question = os.environ.get("QUESTION", "Webhook 失败后还会再发吗？")
    docs = load_documents(Path("data/sample"))
    embedding = SentenceTransformer(os.environ["LOCAL_EMBEDDING_MODEL"], revision=os.environ["LOCAL_EMBEDDING_REVISION"])
    reranker = CrossEncoder(os.environ["RERANK_MODEL"], revision=os.environ["RERANK_REVISION"])
    vectors = embedding.encode([doc.title + "\n" + doc.text for doc in docs], normalize_embeddings=True)
    model = ChatOpenAI(model=os.environ["CHAT_MODEL"], temperature=0, max_tokens=200, timeout=30, max_retries=1)
    rewrites = model.with_structured_output(Queries).invoke([
        ("system", "给出至多两条保留原意的检索问题，不增加原问题未提供的事实。"), ("human", question)])
    queries = list(dict.fromkeys([question] + rewrites.queries))
    #: 归一化向量点积等于余弦；前缀按具体模型卡配置，不能任意换。
    rankings = []
    for query in queries:
        vector = embedding.encode(os.environ.get("QUERY_PREFIX", "") + query, normalize_embeddings=True)
        scores = vectors @ vector
        ranking = sorted(range(len(docs)), key=lambda i: (-float(scores[i]), docs[i].id))[:3]
        rankings.append([docs[i].id for i in ranking])
    fused = [doc_id for doc_id, score in rrf(rankings)]
    by_id = {doc.id: doc for doc in docs}
    #: 先召回候选，再联合编码原始问题与每份候选正文；模型应输出每对单一相关性分数。
    scores = reranker.predict([(question, by_id[doc_id].text) for doc_id in fused])
    reranked = sorted(zip(fused, map(float, scores)), key=lambda item: (-item[1], item[0]))
    print({"queries_for_human_review": queries, "vector_rankings": rankings, "rrf": fused, "reranked": reranked})

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 4B 的真实模型对照扩展：需要下载本地模型、配置在线查询改写模型；未默认运行。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：4B 的真实模型对照扩展：需要下载本地模型、配置在线查询改写模型；未默认运行。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import os
```

**语法与数据变化：** 导入 `os` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库操作系统接口，用于环境变量、目录权限或进程环境。环境变量来自进程，不会因为代码中有名字就自动配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
from pydantic import BaseModel, Field
```

**语法与数据变化：** 从 `pydantic` 导入 `BaseModel, Field`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 运行时数据模型和字段约束。它与普通 Python 类型注解不同；校验 JSON 结构和字段类型不保证内容事实正确。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
```

**语法与数据变化：** 从 `sentence_transformers` 导入 `SentenceTransformer, CrossEncoder`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 本地嵌入与交叉编码模型库。实例化可能下载大模型并占用较多内存；模型名、revision、许可证和预算必须在运行前核对。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from langchain_openai import ChatOpenAI
```

**语法与数据变化：** 从 `langchain_openai` 导入 `ChatOpenAI`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** OpenAI 兼容的聊天/嵌入封装。模型名、密钥与端点由配置决定；调用可能外发文本并产生费用，不应在没确认预算时直接运行。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from evidencedesk.documents import load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
from evidencedesk.hybrid import rrf
```

**语法与数据变化：** 从 `evidencedesk.hybrid` 导入 `rrf`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** bm25按词频及文档频率评分；rrf按榜单位置融合；expand_parents将子ID映射到父ID并去重，三者都不是在线模型调用。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L10"></a>
### 第 10 行

```python
#: 改写数量受限，包含原查询作保底；结构化格式不保证改写保持原意。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：改写数量受限，包含原查询作保底；结构化格式不保证改写保持原意。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L11"></a>
### 第 11 行

```python
class Queries(BaseModel):
```

**语法与数据变化：** 定义改写结果的Pydantic模型。

**为什么与边界：** 仅限制响应形状，不证明改写内容保留原意。

<a id="L12"></a>
### 第 12 行

```python
    queries: list[str] = Field(min_length=1, max_length=2)
```

**语法与数据变化：** queries是1–2个字符串的列表。

**为什么与边界：** 长度限制针对列表项数；不自动限制每条字符串长度或事实新增。

<a id="L13"></a>
### 第 13 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L14"></a>
### 第 14 行

```python
#: 显式模型名和 revision 使模型选择可追溯；下载前检查许可证、内存与网络费用。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：显式模型名和 revision 使模型选择可追溯；下载前检查许可证、内存与网络费用。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L15"></a>
### 第 15 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L16"></a>
### 第 16 行

```python
    question = os.environ.get("QUESTION", "Webhook 失败后还会再发吗？")
```

**语法与数据变化：** 从环境取问题，缺省一个Webhook换说法问题。

**为什么与边界：** 对照实验应固定实际问题；默认句子含Webhook，不能偷换成q06原句仍称同输入。

<a id="L17"></a>
### 第 17 行

```python
    docs = load_documents(Path("data/sample"))
```

**语法与数据变化：** 加载固定手册。

**为什么与边界：** 模型实验前应记录语料版本，避免同时换数据和策略而无法归因。

<a id="L18"></a>
### 第 18 行

```python
    embedding = SentenceTransformer(os.environ["LOCAL_EMBEDDING_MODEL"], revision=os.environ["LOCAL_EMBEDDING_REVISION"])
```

**语法与数据变化：** 实例化SentenceTransformer并固定revision。

**为什么与边界：** 可能联网下载且内存较大；配置缺失会KeyError，不应隐式选一个收费/未知模型替代。

<a id="L19"></a>
### 第 19 行

```python
    reranker = CrossEncoder(os.environ["RERANK_MODEL"], revision=os.environ["RERANK_REVISION"])
```

**语法与数据变化：** 实例化CrossEncoder及其revision。

**为什么与边界：** 它联合编码问题与段落，通常更重；它与双编码器不是同一个模型调用。

<a id="L20"></a>
### 第 20 行

```python
    vectors = embedding.encode([doc.title + "\n" + doc.text for doc in docs], normalize_embeddings=True)
```

**语法与数据变化：** 拼接标题/正文并编码成文档矩阵，要求归一化。

**为什么与边界：** 每行对应docs同位置文档；归一化后点积可表示余弦，但模型卡可能要求文档前缀，本例未自动处理所有模型规范。

<a id="L21"></a>
### 第 21 行

```python
    model = ChatOpenAI(model=os.environ["CHAT_MODEL"], temperature=0, max_tokens=200, timeout=30, max_retries=1)
```

**语法与数据变化：** 构造聊天模型，低温度、输出200、30秒超时和一次重试配置。

**为什么与边界：** 这些是单次调用限制，不是账户总预算；默认服务端点和Key按库配置，不应未授权运行。

<a id="L22"></a>
### 第 22 行

```python
    rewrites = model.with_structured_output(Queries).invoke([
```

**语法与数据变化：** 要求结构化Queries并发起实际invoke。

**为什么与边界：** 从这里开始有真实改写请求，不是仅构造客户端。

<a id="L23"></a>
### 第 23 行

```python
        ("system", "给出至多两条保留原意的检索问题，不增加原问题未提供的事实。"), ("human", question)])
```

**语法与数据变化：** 给出不增事实的系统指令和原问题，闭合请求。

**为什么与边界：** 指令不保证遵守，仍需人工核对改写是否添加“Webhook”等原题没有的信息。

<a id="L24"></a>
### 第 24 行

```python
    queries = list(dict.fromkeys([question] + rewrites.queries))
```

**语法与数据变化：** 将原问题置首，与改写合并后用dict.fromkeys去重保序。

**为什么与边界：** 保留原查询可避免全靠改写，但不保证融合不会降低原查询有效候选的排名。

<a id="L25"></a>
### 第 25 行

```python
    #: 归一化向量点积等于余弦；前缀按具体模型卡配置，不能任意换。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：归一化向量点积等于余弦；前缀按具体模型卡配置，不能任意换。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L26"></a>
### 第 26 行

```python
    rankings = []
```

**语法与数据变化：** 为每条查询准备一个排名列表容器。

**为什么与边界：** 这里累计排名而非向量或文本，随后交给RRF。

<a id="L27"></a>
### 第 27 行

```python
    for query in queries:
```

**语法与数据变化：** 依次处理原查询与每条独特改写。

**为什么与边界：** 当前循环串行编码，不能把它描述成自动并发或无额外成本。

<a id="L28"></a>
### 第 28 行

```python
        vector = embedding.encode(os.environ.get("QUERY_PREFIX", "") + query, normalize_embeddings=True)
```

**语法与数据变化：** 可加模型卡要求的QUERY_PREFIX，再归一化编码查询。

**为什么与边界：** 只改查询前缀不保证整个文档/查询协议已正确配置，模型选择必须成套核对。

<a id="L29"></a>
### 第 29 行

```python
        scores = vectors @ vector
```

**语法与数据变化：** 用矩阵@向量求各文档点积。

**为什么与边界：** 依赖维度匹配和归一化；不归一时它不再等同余弦相似度。

<a id="L30"></a>
### 第 30 行

```python
        ranking = sorted(range(len(docs)), key=lambda i: (-float(scores[i]), docs[i].id))[:3]
```

**语法与数据变化：** 按每个位置对应分数降序、文档ID升序，取前3个索引。

**为什么与边界：** 固定k=3写在实现里，不是从CLI参数读入；实验报告必须记录此限制。

<a id="L31"></a>
### 第 31 行

```python
        rankings.append([docs[i].id for i in ranking])
```

**语法与数据变化：** 把索引转换成文档ID序列并加入rankings。

**为什么与边界：** 索引只在当前docs顺序下有效，持久引用应使用ID。

<a id="L32"></a>
### 第 32 行

```python
    fused = [doc_id for doc_id, score in rrf(rankings)]
```

**语法与数据变化：** RRF融合所有榜单，取ID顺序。

**为什么与边界：** RRF只能合并已有候选，不能补回所有查询都没召回的文档。

<a id="L33"></a>
### 第 33 行

```python
    by_id = {doc.id: doc for doc in docs}
```

**语法与数据变化：** 建立ID到Document的查找字典。

**为什么与边界：** 若ID重复会覆盖，数据加载与题集约束应确保身份唯一。

<a id="L34"></a>
### 第 34 行

```python
    #: 先召回候选，再联合编码原始问题与每份候选正文；模型应输出每对单一相关性分数。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：先召回候选，再联合编码原始问题与每份候选正文；模型应输出每对单一相关性分数。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L35"></a>
### 第 35 行

```python
    scores = reranker.predict([(question, by_id[doc_id].text) for doc_id in fused])
```

**语法与数据变化：** 把原始问题与每份候选正文配对，调用重排模型。

**为什么与边界：** 不用改写问题作为最终判据；仍假定模型为每对输出一个标量，需与所选模型接口一致。

<a id="L36"></a>
### 第 36 行

```python
    reranked = sorted(zip(fused, map(float, scores)), key=lambda item: (-item[1], item[0]))
```

**语法与数据变化：** 将候选ID与float分数zip，再按分数降序、ID升序排序。

**为什么与边界：** zip会截到短者，若模型输出长度异常本例未显式拒绝，生产实验需补长度校验。

<a id="L37"></a>
### 第 37 行

```python
    print({"queries_for_human_review": queries, "vector_rankings": rankings, "rrf": fused, "reranked": reranked})
```

**语法与数据变化：** 打印改写、向量榜、融合与重排供人工复查。

**为什么与边界：** 没有直接计算Recall/MRR或答案质量；打印真实分数也不等于已经证明改进。

<a id="L38"></a>
### 第 38 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L39"></a>
### 第 39 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L40"></a>
### 第 40 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

同样问题先保留原查询，再最多两条改写。若改写额外假定产品或收费事实，必须人工发现，结构化列表本身不会阻止语义漂移。

## 只练一个关键点（不是新的学习验收记录）

1. 先列出两个本地模型名/revision及在线改写调用点，不下载、不invoke。
2. 把将来对照表写好：固定原问题、语料、模型版本、k、指标、成本；保留q06原句。
3. **复盘：** 为什么不能悄悄给q06补Webhook上下文后称原问题解决？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
