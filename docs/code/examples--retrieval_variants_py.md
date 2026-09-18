# 改写、融合、重排与父级回填的机制串联：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/retrieval_variants.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

先用受控输入看清每一阶段的列表怎样变化，之后才比较真实模型质量。

### 输入、输出与调用关系

两份预设子块排名→RRF→固定pair分数重排→父文档列表。

### 运行与风险边界

`python -m examples.retrieval_variants`；离线不下载模型。

查询改写和重排分数全是fixture，不得当成真实LLM/cross-encoder效果。

## 完整源码

<!-- source: examples/retrieval_variants.py -->
```python
#: MultiQuery 与 rerank 先用受控 fixture 演示数据流，真实质量需要模型和实验验证。
from evidencedesk.hybrid import rrf, expand_parents

#: 两条查询的候选排名来自固定样例，不宣称是模型自动改写的结果。
def main():
    original_ranking = ["retry-child", "keys-child"]
    rewritten_ranking = ["retry-child", "ticket-child"]
    fused = [doc_id for doc_id, score in rrf([original_ranking, rewritten_ranking])]
    #: Cross-encoder 对 (query, passage) 打分；这里用预置分数替身验证排序连接方式。
    fixture_pair_scores = {"retry-child": 0.8, "keys-child": 0.1, "ticket-child": 0.3}
    reranked = sorted(fused, key=lambda item: (-fixture_pair_scores[item], item))[:2]
    parents = expand_parents(reranked, {"retry-child": "webhook-delivery", "keys-child": "api-key-policy", "ticket-child": "incident-escalation"})
    print({"fused": fused, "fixture_reranked": reranked, "parents": parents})

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: MultiQuery 与 rerank 先用受控 fixture 演示数据流，真实质量需要模型和实验验证。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：MultiQuery 与 rerank 先用受控 fixture 演示数据流，真实质量需要模型和实验验证。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
from evidencedesk.hybrid import rrf, expand_parents
```

**语法与数据变化：** 从 `evidencedesk.hybrid` 导入 `rrf, expand_parents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** bm25按词频及文档频率评分；rrf按榜单位置融合；expand_parents将子ID映射到父ID并去重，三者都不是在线模型调用。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L4"></a>
### 第 4 行

```python
#: 两条查询的候选排名来自固定样例，不宣称是模型自动改写的结果。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：两条查询的候选排名来自固定样例，不宣称是模型自动改写的结果。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
    original_ranking = ["retry-child", "keys-child"]
```

**语法与数据变化：** 原查询榜单固定为两个子块ID。

**为什么与边界：** 这里没有真的运行检索器，仅提供可控输入。

<a id="L7"></a>
### 第 7 行

```python
    rewritten_ranking = ["retry-child", "ticket-child"]
```

**语法与数据变化：** 改写榜单另含ticket-child。

**为什么与边界：** 这不是模型自动改写的结果，不能据此声称改写保留了原意。

<a id="L8"></a>
### 第 8 行

```python
    fused = [doc_id for doc_id, score in rrf([original_ranking, rewritten_ranking])]
```

**语法与数据变化：** 把两榜交给RRF，再取融合后的ID顺序。

**为什么与边界：** 融合按排名贡献，不用原分数加和；同ID跨榜支持会累计。

<a id="L9"></a>
### 第 9 行

```python
    #: Cross-encoder 对 (query, passage) 打分；这里用预置分数替身验证排序连接方式。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Cross-encoder 对 (query, passage) 打分；这里用预置分数替身验证排序连接方式。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L10"></a>
### 第 10 行

```python
    fixture_pair_scores = {"retry-child": 0.8, "keys-child": 0.1, "ticket-child": 0.3}
```

**语法与数据变化：** 为每个候选预置一个问题-段落相关性分数。

**为什么与边界：** 这些数值只验证排序连接，不能拿它们计算真实模型对照结论。

<a id="L11"></a>
### 第 11 行

```python
    reranked = sorted(fused, key=lambda item: (-fixture_pair_scores[item], item))[:2]
```

**语法与数据变化：** 按预置分降序、同分ID升序，截前2项。

**为什么与边界：** 重排仅在已有候选内重新排序；召回阶段缺失的文档不能凭重排产生。

<a id="L12"></a>
### 第 12 行

```python
    parents = expand_parents(reranked, {"retry-child": "webhook-delivery", "keys-child": "api-key-policy", "ticket-child": "incident-escalation"})
```

**语法与数据变化：** 按映射把子ID展开为父文档ID并去重。

**为什么与边界：** 仍只是标识映射，未读取父正文；真实扩展应再做授权和token预算检查。

<a id="L13"></a>
### 第 13 行

```python
    print({"fused": fused, "fixture_reranked": reranked, "parents": parents})
```

**语法与数据变化：** 打印三个阶段的数据供逐步观察。

**为什么与边界：** 可定位变化发生在融合还是重排，而不是只看最终看似合理的父列表。

<a id="L14"></a>
### 第 14 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L15"></a>
### 第 15 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L16"></a>
### 第 16 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

融合后用0.8/0.3/0.1排序，前两项应是retry-child、ticket-child，父级分别为Webhook和incident文档。

## 只练一个关键点（不是新的学习验收记录）

1. 运行离线示例并顺次画出fused→fixture_reranked→parents。
2. 在副本交换两个fixture_pair_scores值，其他输入保持不变，检查变化从哪一阶段开始。
3. **复盘：** 重排能不能补回从未进入fused的ID？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
