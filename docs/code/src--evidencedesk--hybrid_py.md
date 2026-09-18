# BM25、RRF 与父文档展开：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/hybrid.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把词频检索、跨检索器排名融合和父文档映射拆开，便于一次只改变一个策略。

### 输入、输出与调用关系

BM25接收分词后的查询列表和文档ID→词列表；RRF接收多个有序ID列表；父展开接收子ID与映射。

### 运行与风险边界

`python -m examples.hybrid_rankings` 与 `python -m examples.retrieval_variants` 是离线机制例子。

输入词已由调用者准备；英语 split 不能冒充中文语义分词。fixture 排名不证明真实嵌入效果，父文档回填仍需权限校验。

## 完整源码

<!-- source: src/evidencedesk/hybrid.py -->
```python
#: 教学版 BM25：先让公式可见，后续数据变大再换成熟索引实现。
import math
from collections import Counter, defaultdict

#: 查询分词由调用者负责；这里接收 token 列表，不把英语 split 冒充中文分词。
def bm25(query: list[str], corpus: dict[str, list[str]], k1: float = 1.5, b: float = 0.75):
    if not k1 > 0 or not 0 <= b <= 1:
        raise ValueError("要求 k1>0，0<=b<=1")
    if not corpus:
        return []
    n = len(corpus)
    average = sum(map(len, corpus.values())) / n
    if not average:
        return []
    #: df 是含词文档数；IDF 让稀有词更有区分力，不等于词越少越正确。
    df = Counter(term for terms in corpus.values() for term in set(terms))
    scores = []
    for doc_id, terms in corpus.items():
        tf = Counter(terms)
        score = 0.0
        for term in set(query):
            if not tf[term]:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            denominator = tf[term] + k1 * (1 - b + b * len(terms) / average)
            score += idf * tf[term] * (k1 + 1) / denominator
        if score > 0:
            scores.append((doc_id, score))
    return sorted(scores, key=lambda item: (-item[1], item[0]))

#: RRF 用排名融合而非相加不同量纲的原始分数；同一列表内去重防刷分。
def rrf(rankings: list[list[str]], c: int = 60):
    if c <= 0:
        raise ValueError("c 必须大于 0")
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(dict.fromkeys(ranking), 1):
            scores[doc_id] += 1 / (c + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))

#: 父子检索取回父级上下文并保留首次出现顺序；父文档仍需重新检查访问权限。
def expand_parents(child_ids: list[str], parent_by_child: dict[str, str]):
    return list(dict.fromkeys(parent_by_child[child_id] for child_id in child_ids))
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 教学版 BM25：先让公式可见，后续数据变大再换成熟索引实现。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：教学版 BM25：先让公式可见，后续数据变大再换成熟索引实现。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import math
```

**语法与数据变化：** 导入 `math` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库数学函数。log 表示自然对数，sqrt 表示平方根；公式仍要自己处理空输入、零分母及参数范围。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
from collections import Counter, defaultdict
```

**语法与数据变化：** 从 `collections` 导入 `Counter, defaultdict`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Counter 统计频次，defaultdict 给首次访问的键提供默认值。它们改变计数/累积方式，不会自动完成文本分词。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L5"></a>
### 第 5 行

```python
#: 查询分词由调用者负责；这里接收 token 列表，不把英语 split 冒充中文分词。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：查询分词由调用者负责；这里接收 token 列表，不把英语 split 冒充中文分词。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L6"></a>
### 第 6 行

```python
def bm25(query: list[str], corpus: dict[str, list[str]], k1: float = 1.5, b: float = 0.75):
```

**语法与数据变化：** 定义教学版BM25；k1默认1.5控制词频饱和，b默认0.75控制长度归一。

**为什么与边界：** corpus 的值必须是词列表；不在此隐式分词，便于将词处理与公式独立评测。

<a id="L7"></a>
### 第 7 行

```python
    if not k1 > 0 or not 0 <= b <= 1:
```

**语法与数据变化：** 要求k1>0且b位于[0,1]。

**为什么与边界：** 这不是严格数值schema，传不兼容类型仍可能TypeError；不要把该条件当成对所有非法值的完整校验。

<a id="L8"></a>
### 第 8 行

```python
        raise ValueError("要求 k1>0，0<=b<=1")
```

**语法与数据变化：** 参数范围违规时抛ValueError。

**为什么与边界：** 不应悄悄改回默认值，否则对照实验实际参数不透明。

<a id="L9"></a>
### 第 9 行

```python
    if not corpus:
```

**语法与数据变化：** 空语料会使平均长度分母为0，先分支处理。

**为什么与边界：** 没有语料与所有文档得零分不是同一内部原因，但本函数都可能返回空候选。

<a id="L10"></a>
### 第 10 行

```python
        return []
```

**语法与数据变化：** 直接返回空排名，不计算统计量。

**为什么与边界：** 不会产生虚构占位文档来补齐结果。

<a id="L11"></a>
### 第 11 行

```python
    n = len(corpus)
```

**语法与数据变化：** n 保存文档总数，不是词总数。

**为什么与边界：** 后面的df/IDF以文档为单位，分母不能换成token总数。

<a id="L12"></a>
### 第 12 行

```python
    average = sum(map(len, corpus.values())) / n
```

**语法与数据变化：** map(len,...)求各文档词数，sum后除以n得平均长度。

**为什么与边界：** 这里数输入token列表长度；重复词计入文档长度。

<a id="L13"></a>
### 第 13 行

```python
    if not average:
```

**语法与数据变化：** 若所有文档都空，平均长度为0。

**为什么与边界：** 后面归一化要除以平均长度，必须避开零分母。

<a id="L14"></a>
### 第 14 行

```python
        return []
```

**语法与数据变化：** 全部空文档时返回空排名。

**为什么与边界：** 不能把这种无信息语料评为任意正相似度。

<a id="L15"></a>
### 第 15 行

```python
    #: df 是含词文档数；IDF 让稀有词更有区分力，不等于词越少越正确。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：df 是含词文档数；IDF 让稀有词更有区分力，不等于词越少越正确。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L16"></a>
### 第 16 行

```python
    df = Counter(term for terms in corpus.values() for term in set(terms))
```

**语法与数据变化：** 每份文档先set去重，再跨文档Counter统计df。

**为什么与边界：** 同词在一篇里出现10次，df只加1；它是含词文档数，不是词频tf。

<a id="L17"></a>
### 第 17 行

```python
    scores = []
```

**语法与数据变化：** 创建(doc_id,score)结果列表。

**为什么与边界：** 每次函数调用独立累计，不缓存上一查询分数。

<a id="L18"></a>
### 第 18 行

```python
    for doc_id, terms in corpus.items():
```

**语法与数据变化：** 同时遍历文档ID和词列表。

**为什么与边界：** 输入字典的顺序不是最终排名依据，最后会按分数和ID排序。

<a id="L19"></a>
### 第 19 行

```python
        tf = Counter(terms)
```

**语法与数据变化：** Counter保留本篇中每个词的重复次数tf。

**为什么与边界：** 它与上一层去重后的df相互独立，是BM25不同的统计量。

<a id="L20"></a>
### 第 20 行

```python
        score = 0.0
```

**语法与数据变化：** 本篇分数从0.0开始，每个命中查询词贡献一次。

**为什么与边界：** 重设位置在文档循环内，避免分数跨文档累加。

<a id="L21"></a>
### 第 21 行

```python
        for term in set(query):
```

**语法与数据变化：** 查询词set去重后迭代。

**为什么与边界：** 此实现不把查询里重复词次数当作额外权重；这是一项明确简化。

<a id="L22"></a>
### 第 22 行

```python
            if not tf[term]:
```

**语法与数据变化：** Counter缺失词返回0，not 0 表示本篇未命中该查询词。

**为什么与边界：** 无需先判断键存在；不存在不应进入正贡献计算。

<a id="L23"></a>
### 第 23 行

```python
                continue
```

**语法与数据变化：** 跳过这个查询词，继续下一词。

**为什么与边界：** 不是丢弃整篇，其他查询词仍可贡献分数。

<a id="L24"></a>
### 第 24 行

```python
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
```

**语法与数据变化：** 计算平滑IDF：含该词的文档越少，通常贡献越大。

**为什么与边界：** +0.5和外层1稳定边界；稀有并不意味着事实正确，IDF只反映区分性。

<a id="L25"></a>
### 第 25 行

```python
            denominator = tf[term] + k1 * (1 - b + b * len(terms) / average)
```

**语法与数据变化：** 分母结合tf、k1和相对文档长度。

**为什么与边界：** b=0取消长度项影响；较长文档在其他条件相同时受到更多长度归一化。

<a id="L26"></a>
### 第 26 行

```python
            score += idf * tf[term] * (k1 + 1) / denominator
```

**语法与数据变化：** 把当前词的BM25贡献加到本篇score。

**为什么与边界：** tf在分子分母同时出现，所以贡献随频次增加会饱和，而不是无限线性上涨。

<a id="L27"></a>
### 第 27 行

```python
        if score > 0:
```

**语法与数据变化：** 只保留累计正分的文档。

**为什么与边界：** 没有匹配词不会因为文档存在就得到默认正分。

<a id="L28"></a>
### 第 28 行

```python
            scores.append((doc_id, score))
```

**语法与数据变化：** 以元组保存文档ID与分数。

**为什么与边界：** 不是SearchHit对象，调用者需要知道返回结构差异。

<a id="L29"></a>
### 第 29 行

```python
    return sorted(scores, key=lambda item: (-item[1], item[0]))
```

**语法与数据变化：** 按负分数升序等价分数降序，同分按ID升序。

**为什么与边界：** BM25原始值和余弦分数尺度不同，不能据此直接把两者相加。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

```python
#: RRF 用排名融合而非相加不同量纲的原始分数；同一列表内去重防刷分。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：RRF 用排名融合而非相加不同量纲的原始分数；同一列表内去重防刷分。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L32"></a>
### 第 32 行

```python
def rrf(rankings: list[list[str]], c: int = 60):
```

**语法与数据变化：** 定义倒数排名融合，c默认60。

**为什么与边界：** 输入是排序后的ID列表，不是原始相似度；它让不同量纲的检索器可按排名融合。

<a id="L33"></a>
### 第 33 行

```python
    if c <= 0:
```

**语法与数据变化：** 要求平滑参数c大于0。

**为什么与边界：** 当前未严格限制精确整数类型；调用方仍需约定合法参数，注解不自动执行检查。

<a id="L34"></a>
### 第 34 行

```python
        raise ValueError("c 必须大于 0")
```

**语法与数据变化：** 非法c抛ValueError，避免不合理倒数权重。

**为什么与边界：** 报错应记录实验配置，不悄悄替换参数。

<a id="L35"></a>
### 第 35 行

```python
    scores = defaultdict(float)
```

**语法与数据变化：** defaultdict(float) 为新ID提供0.0的累积起点。

**为什么与边界：** 访问新键时会插入默认值；不是预先枚举全部语料。

<a id="L36"></a>
### 第 36 行

```python
    for ranking in rankings:
```

**语法与数据变化：** 逐个处理来自不同检索器/改写的排名表。

**为什么与边界：** 每一份榜单都会贡献权重，重复提交同榜本身仍可能改变融合，需要调用方控制来源。

<a id="L37"></a>
### 第 37 行

```python
        for rank, doc_id in enumerate(dict.fromkeys(ranking), 1):
```

**语法与数据变化：** dict.fromkeys 去除单榜重复ID并保留首次顺序，enumerate从1编号。

**为什么与边界：** 去重后再排位，避免同文档重复占位或刷分；不把跨榜出现当成重复错误。

<a id="L38"></a>
### 第 38 行

```python
            scores[doc_id] += 1 / (c + rank)
```

**语法与数据变化：** 按1/(c+rank)加入该ID总分。

**为什么与边界：** 越靠前贡献越大，多榜支持也会累计；融合分不是答案概率。

<a id="L39"></a>
### 第 39 行

```python
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
```

**语法与数据变化：** 按融合分降序、ID升序输出(ID,分数)列表。

**为什么与边界：** 调用方可再截取k；当前函数本身不限制返回数量。

<a id="L40"></a>
### 第 40 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L41"></a>
### 第 41 行

```python
#: 父子检索取回父级上下文并保留首次出现顺序；父文档仍需重新检查访问权限。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：父子检索取回父级上下文并保留首次出现顺序；父文档仍需重新检查访问权限。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L42"></a>
### 第 42 行

```python
def expand_parents(child_ids: list[str], parent_by_child: dict[str, str]):
```

**语法与数据变化：** 定义子块到父文档的展开接口。

**为什么与边界：** 这是映射操作，不会自动读取父文档内容，也不验证访问权限。

<a id="L43"></a>
### 第 43 行

```python
    return list(dict.fromkeys(parent_by_child[child_id] for child_id in child_ids))
```

**语法与数据变化：** 依次查子ID的父ID，用dict.fromkeys去重保留首次顺序，再转成列表。

**为什么与边界：** 多个子块可归同父文档；缺失映射会KeyError。回填父正文之前仍须做父级授权和上下文预算检查。

## 跟一遍数据与验证边界

RRF融合 [a,b] 与 [b,a] 时两者同分，按ID确定顺序；单榜 [a,a,b] 先去重复，a不靠重复项加分。BM25频次饱和不是出现次数无限线性增分。

## 只练一个关键点（不是新的学习验收记录）

1. 运行hybrid_rankings，用纸面表记每个ID在每榜的rank。
2. 手算一个1/(60+rank)贡献，再看重复ID仅单榜去重的测试。
3. **复盘：** 为什么不直接相加BM25分数和余弦分数？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
