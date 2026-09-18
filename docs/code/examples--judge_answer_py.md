# 用真实候选答案做模型辅助评测：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/judge_answer.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

展示Faithfulness裁判接口，同时强调裁判不是无偏真理。

### 输入、输出与调用关系

环境中的真实candidate、固定问题和对应上下文→一条Ragas评分。

### 运行与风险边界

可选在线实验，按7A安装兼容Ragas版本；配置OPENAI_API_KEY、CANDIDATE_ANSWER、JUDGE_MODEL并确认外发/费用后才运行。

会调用裁判模型且可能收费；本轮未验证。接口属于Ragas0.3系列，升级要核对迁移；不能用手写标准答案冒充系统候选。

## 完整源码

<!-- source: examples/judge_answer.py -->
```python
#: 在线可选：Ragas 的 LLM 裁判也会收费，且评分有随机性与模型偏差。
import asyncio
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness
from evidencedesk.documents import load_documents

#: 从真实候选答案构造单条评测，不能把人工标准答案伪装为系统输出。
async def main():
    os.environ["OPENAI_API_KEY"]
    candidate = os.environ["CANDIDATE_ANSWER"]
    doc = next(doc for doc in load_documents(Path("data/sample")) if doc.id == "webhook-delivery")
    sample = SingleTurnSample(user_input="Webhook 重试多少次？", response=candidate, retrieved_contexts=[doc.text])
    #: 此接口属于 Ragas 0.3 系列；升级应先核对迁移说明，不能只更新版本号。
    judge = LangchainLLMWrapper(ChatOpenAI(model=os.environ["JUDGE_MODEL"], temperature=0, timeout=30, max_retries=1))
    metric = Faithfulness(llm=judge)
    score = await metric.single_turn_ascore(sample)
    print({"metric": "faithfulness", "score": score, "human_review_required": True})

if __name__ == "__main__":
    asyncio.run(main())
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 在线可选：Ragas 的 LLM 裁判也会收费，且评分有随机性与模型偏差。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：在线可选：Ragas 的 LLM 裁判也会收费，且评分有随机性与模型偏差。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import asyncio
```

**语法与数据变化：** 导入 `asyncio` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库异步事件循环。async/await 管理可等待操作，run 启动顶层协程；异步不意味着自动并行所有工作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import os
```

**语法与数据变化：** 导入 `os` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库操作系统接口，用于环境变量、目录权限或进程环境。环境变量来自进程，不会因为代码中有名字就自动配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

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
from langchain_openai import ChatOpenAI
```

**语法与数据变化：** 从 `langchain_openai` 导入 `ChatOpenAI`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** OpenAI 兼容的聊天/嵌入封装。模型名、密钥与端点由配置决定；调用可能外发文本并产生费用，不应在没确认预算时直接运行。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from ragas import SingleTurnSample
```

**语法与数据变化：** 从 `ragas` 导入 `SingleTurnSample`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 评测数据结构与工具。SingleTurnSample描述一条问题、系统回答和上下文，不代表它已经获得裁判评分。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from ragas.llms import LangchainLLMWrapper
```

**语法与数据变化：** 从 `ragas.llms` 导入 `LangchainLLMWrapper`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 把LangChain模型适配为Ragas裁判接口；包装不免费，也不会消除裁判模型的偏差。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
from ragas.metrics import Faithfulness
```

**语法与数据变化：** 从 `ragas.metrics` 导入 `Faithfulness`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 指标实现。Faithfulness检查候选回答与上下文的支持关系，是模型辅助评估，不等于正确性、完整性和安全性的全部指标。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

```python
from evidencedesk.documents import load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L10"></a>
### 第 10 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L11"></a>
### 第 11 行

```python
#: 从真实候选答案构造单条评测，不能把人工标准答案伪装为系统输出。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：从真实候选答案构造单条评测，不能把人工标准答案伪装为系统输出。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L12"></a>
### 第 12 行

```python
async def main():
```

**语法与数据变化：** 定义异步入口，调用它先得到协程，需await或事件循环运行。

**为什么与边界：** 不能直接main()后以为网络评测已完成。

<a id="L13"></a>
### 第 13 行

```python
    os.environ["OPENAI_API_KEY"]
```

**语法与数据变化：** 要求Key环境变量存在，不打印。

**为什么与边界：** 没有Key就应在外发前失败，不能临时把它写进源码。

<a id="L14"></a>
### 第 14 行

```python
    candidate = os.environ["CANDIDATE_ANSWER"]
```

**语法与数据变化：** 读取实际候选答案文本。

**为什么与边界：** 不能为了高分替换成人工参考答案，否则测的不是系统输出。

<a id="L15"></a>
### 第 15 行

```python
    doc = next(doc for doc in load_documents(Path("data/sample")) if doc.id == "webhook-delivery")
```

**语法与数据变化：** 加载手册后用生成器找到Webhook文档，next取首个匹配。

**为什么与边界：** 没有匹配会StopIteration；本例假定样例齐全，不是任意语料容错加载。

<a id="L16"></a>
### 第 16 行

```python
    sample = SingleTurnSample(user_input="Webhook 重试多少次？", response=candidate, retrieved_contexts=[doc.text])
```

**语法与数据变化：** 构造SingleTurnSample，明确问题、候选回答、检索上下文列表。

**为什么与边界：** 本例上下文是固定选取，不证明真实检索管道确实返回了它；端到端评测需保存真实候选证据。

<a id="L17"></a>
### 第 17 行

```python
    #: 此接口属于 Ragas 0.3 系列；升级应先核对迁移说明，不能只更新版本号。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：此接口属于 Ragas 0.3 系列；升级应先核对迁移说明，不能只更新版本号。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L18"></a>
### 第 18 行

```python
    judge = LangchainLLMWrapper(ChatOpenAI(model=os.environ["JUDGE_MODEL"], temperature=0, timeout=30, max_retries=1))
```

**语法与数据变化：** 用LangChain聊天模型包成Ragas裁判接口，模型名显式配置。

**为什么与边界：** 温度0仍有服务/裁判偏差，timeout与retry也不是总费用限额。

<a id="L19"></a>
### 第 19 行

```python
    metric = Faithfulness(llm=judge)
```

**语法与数据变化：** 将裁判传给Faithfulness指标。

**为什么与边界：** 指标关注回答与提供上下文的支持关系，不是总体产品正确率。

<a id="L20"></a>
### 第 20 行

```python
    score = await metric.single_turn_ascore(sample)
```

**语法与数据变化：** await异步评分，真正等待模型辅助评估结果。

**为什么与边界：** 可能发生外发和费用，错误需单独记录，不能拿fixture分数代替。

<a id="L21"></a>
### 第 21 行

```python
    print({"metric": "faithfulness", "score": score, "human_review_required": True})
```

**语法与数据变化：** 打印指标名、分数及人工复核提醒。

**为什么与边界：** 不能把一个分数当成自动上线许可，应校准、多样本对照并记录版本。

<a id="L22"></a>
### 第 22 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L23"></a>
### 第 23 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L24"></a>
### 第 24 行

```python
    asyncio.run(main())
```

**语法与数据变化：** asyncio.run创建事件循环执行协程并等待完成。

**为什么与边界：** 普通脚本可用；已有事件循环的notebook里通常应直接await，不能盲目嵌套run。

## 跟一遍数据与验证边界

候选说重试3次时还要核对上下文是否完整支持，裁判高分不保证引用、完整性、安全性全好；需人工校准。

## 只练一个关键点（不是新的学习验收记录）

1. 只标出候选、上下文和裁判模型三个输入，不调用在线裁判。
2. 准备人工复核表，并记录候选必须来自实际系统输出；收费与外发另行确认。
3. **复盘：** faithfulness高分为什么不等于答案完整、安全或全局正确？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
