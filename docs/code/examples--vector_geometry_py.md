# 二维向量、余弦与检索前过滤：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/vector_geometry.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用能手算的向量区分几何检索机制和真实语义模型效果。

### 输入、输出与调用关系

在Qdrant内存集合放三点，按alpha过滤后取最多两点并检查结果。

### 运行与风险边界

安装本课vector依赖后运行 `python -m examples.vector_geometry`，不需模型API。

真实Qdrant本地调用，向量却是手写fixture；不能据此声称已经用embedding解决q06。内存集合不跨进程持久化。

## 完整源码

<!-- source: examples/vector_geometry.py -->
```python
#: 使用真实 Qdrant 本地内存模式，但向量是手写的，仅解释几何和过滤。
from qdrant_client import QdrantClient, models

#: collection 规定维数与距离函数，查询向量必须同维，真实模型还必须同版本。
def main():
    client = QdrantClient(":memory:")
    client.create_collection("geometry", vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE))
    client.upsert("geometry", points=[
        models.PointStruct(id=1, vector=[1.0, 0.0], payload={"topic": "重试", "tenant": "alpha"}),
        models.PointStruct(id=2, vector=[0.0, 1.0], payload={"topic": "密钥", "tenant": "alpha"}),
        models.PointStruct(id=3, vector=[0.9, 0.1], payload={"topic": "私有", "tenant": "beta"}),
    ])
    #: 过滤发生在检索候选阶段；第三点再相似，也不能跨租户进入结果。
    scope = models.Filter(must=[models.FieldCondition(key="tenant", match=models.MatchValue(value="alpha"))])
    points = client.query_points("geometry", query=[0.9, 0.1], query_filter=scope, limit=2).points
    print([(point.id, round(point.score, 4)) for point in points])
    assert points[0].id == 1 and all(point.payload["tenant"] == "alpha" for point in points)
    client.close()

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 使用真实 Qdrant 本地内存模式，但向量是手写的，仅解释几何和过滤。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：使用真实 Qdrant 本地内存模式，但向量是手写的，仅解释几何和过滤。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
from qdrant_client import QdrantClient, models
```

**语法与数据变化：** 从 `qdrant_client` 导入 `QdrantClient, models`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 向量数据库客户端及数据模型。这里本地 :memory: 用于实验；向量内容与模型语义质量仍由输入决定。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L4"></a>
### 第 4 行

```python
#: collection 规定维数与距离函数，查询向量必须同维，真实模型还必须同版本。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：collection 规定维数与距离函数，查询向量必须同维，真实模型还必须同版本。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L5"></a>
### 第 5 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L6"></a>
### 第 6 行

```python
    client = QdrantClient(":memory:")
```

**语法与数据变化：** 创建Qdrant本地内存客户端。

**为什么与边界：** 不是连接名为memory的远程服务，也不代表有持久化磁盘索引。

<a id="L7"></a>
### 第 7 行

```python
    client.create_collection("geometry", vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE))
```

**语法与数据变化：** 建立geometry集合，二维向量、余弦距离度量。

**为什么与边界：** 查询和写入维度必须一致；真实模型还必须统一模型版本与向量空间。

<a id="L8"></a>
### 第 8 行

```python
    client.upsert("geometry", points=[
```

**语法与数据变化：** 开始upsert三个点，命名集合必须已创建。

**为什么与边界：** upsert按点ID插入或更新，不是每次调用都生成新ID。

<a id="L9"></a>
### 第 9 行

```python
        models.PointStruct(id=1, vector=[1.0, 0.0], payload={"topic": "重试", "tenant": "alpha"}),
```

**语法与数据变化：** ID1向量指向第一轴，payload含重试主题和alpha租户。

**为什么与边界：** topic只是元数据标签，向量并非从这段中文计算出来。

<a id="L10"></a>
### 第 10 行

```python
        models.PointStruct(id=2, vector=[0.0, 1.0], payload={"topic": "密钥", "tenant": "alpha"}),
```

**语法与数据变化：** ID2指向第二轴，同属alpha。

**为什么与边界：** 两个轴正交，便于人工检查余弦排序；不代表真实密钥与重试语义完全无关。

<a id="L11"></a>
### 第 11 行

```python
        models.PointStruct(id=3, vector=[0.9, 0.1], payload={"topic": "私有", "tenant": "beta"}),
```

**语法与数据变化：** ID3与查询方向相近/相同，但属于beta。

**为什么与边界：** 这是用来证明不能以相似度替代权限的反例。

<a id="L12"></a>
### 第 12 行

```python
    ])
```

**语法与数据变化：** 闭合点列表与upsert调用。

**为什么与边界：** 三点共同写入此次内存集合，后续查询才能找到它们。

<a id="L13"></a>
### 第 13 行

```python
    #: 过滤发生在检索候选阶段；第三点再相似，也不能跨租户进入结果。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：过滤发生在检索候选阶段；第三点再相似，也不能跨租户进入结果。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L14"></a>
### 第 14 行

```python
    scope = models.Filter(must=[models.FieldCondition(key="tenant", match=models.MatchValue(value="alpha"))])
```

**语法与数据变化：** 构造must过滤条件，tenant字段必须精确匹配alpha。

**为什么与边界：** 过滤由可信身份确定；生产不能直接采纳用户声称的任意tenant。

<a id="L15"></a>
### 第 15 行

```python
    points = client.query_points("geometry", query=[0.9, 0.1], query_filter=scope, limit=2).points
```

**语法与数据变化：** 用二维query查询、带过滤器、limit=2，再从响应取points列表。

**为什么与边界：** beta在候选阶段排除；没有“先返回再由LLM过滤”的泄漏窗口。

<a id="L16"></a>
### 第 16 行

```python
    print([(point.id, round(point.score, 4)) for point in points])
```

**语法与数据变化：** 打印每个ID与四位小数分数，便于观察。

**为什么与边界：** round仅用于显示，排序已由数据库完成，不是先四舍五入再排。

<a id="L17"></a>
### 第 17 行

```python
    assert points[0].id == 1 and all(point.payload["tenant"] == "alpha" for point in points)
```

**语法与数据变化：** 同时断言第一名ID1和所有候选都是alpha。

**为什么与边界：** 只检查第一名会漏掉列表尾部跨租户泄漏；all检查整组返回。

<a id="L18"></a>
### 第 18 行

```python
    client.close()
```

**语法与数据变化：** 关闭客户端释放本地资源。

**为什么与边界：** 内存内容随此生命周期结束，不应把前一次输出当成持久性证明。

<a id="L19"></a>
### 第 19 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L20"></a>
### 第 20 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L21"></a>
### 第 21 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

查询[0.9,0.1]与beta点相同，但beta必须被过滤；alpha的[1,0]最接近查询方向，应排第一。

## 只练一个关键点（不是新的学习验收记录）

1. 安装本课依赖后运行二维例子，先手算查询更靠近哪一方向。
2. 只在副本将过滤tenant改为beta，再比较返回点；恢复副本设置，不改真实ACL。
3. **复盘：** 几何正确为什么不能证明语义模型能理解q06？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
