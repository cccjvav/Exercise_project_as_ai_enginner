# 最少字段的离线检索追踪：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/trace_allowlist.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

只记录定位性能所需的允许字段，避免把日志变成问题原文和密钥的副本。

### 输入、输出与调用关系

一次词检索→耗时、候选数、错误类型占位和模型调用数的JSON。

### 运行与风险边界

`python -m examples.trace_allowlist`，不调用在线追踪平台。

测量范围不含文档加载，不含模型；只演示成功路径，没有通用异常上报。

## 完整源码

<!-- source: examples/trace_allowlist.py -->
```python
#: 与其靠正则猜所有敏感信息，不如默认不采集原始请求、原文和凭据。
import json
import time
from pathlib import Path
from evidencedesk.documents import load_documents
from evidencedesk.search import search

#: perf_counter 衡量持续时间，不受系统时钟回拨影响；这里不测模型延迟。
def main():
    documents = load_documents(Path("data/sample"))
    started = time.perf_counter()
    hits = search("Webhook 重试", documents, 2)
    trace = {"operation": "lexical_retrieval", "duration_ms": round((time.perf_counter() - started) * 1000, 3),
             "candidate_count": len(hits), "error_type": None, "model_calls": 0}
    print(json.dumps(trace, ensure_ascii=False))
    assert "question" not in trace and "authorization" not in trace

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 与其靠正则猜所有敏感信息，不如默认不采集原始请求、原文和凭据。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：与其靠正则猜所有敏感信息，不如默认不采集原始请求、原文和凭据。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import time
```

**语法与数据变化：** 导入 `time` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库时间接口。perf_counter用于测量持续时间，与业务时间戳/到期时间用途不同；度量范围取决于计时语句放在哪里。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

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
from evidencedesk.documents import load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from evidencedesk.search import search
```

**语法与数据变化：** 从 `evidencedesk.search` 导入 `search`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** search用固定领域词覆盖率返回排序的SearchHit候选；不是模型生成或语义检索。权限过滤应在调用之前完成。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
#: perf_counter 衡量持续时间，不受系统时钟回拨影响；这里不测模型延迟。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：perf_counter 衡量持续时间，不受系统时钟回拨影响；这里不测模型延迟。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L9"></a>
### 第 9 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L10"></a>
### 第 10 行

```python
    documents = load_documents(Path("data/sample"))
```

**语法与数据变化：** 先加载文档，再开始下面的计时。

**为什么与边界：** 因此报告耗时不包含文件读取，不能把它称为整个请求端到端延迟。

<a id="L11"></a>
### 第 11 行

```python
    started = time.perf_counter()
```

**语法与数据变化：** 用perf_counter记录单调高精度起点。

**为什么与边界：** 适合测差值，不是可显示给人的日期或业务过期时间。

<a id="L12"></a>
### 第 12 行

```python
    hits = search("Webhook 重试", documents, 2)
```

**语法与数据变化：** 执行固定问题、k=2的词检索。

**为什么与边界：** 没有模型API，所以本次模型调用数可以明确为0。

<a id="L13"></a>
### 第 13 行

```python
    trace = {"operation": "lexical_retrieval", "duration_ms": round((time.perf_counter() - started) * 1000, 3),
```

**语法与数据变化：** 创建trace，计算结束起点差×1000并保留3位小数。

**为什么与边界：** 计时仅覆盖search和极少周边开销；不同机器或缓存状态不能不加条件比较。

<a id="L14"></a>
### 第 14 行

```python
             "candidate_count": len(hits), "error_type": None, "model_calls": 0}
```

**语法与数据变化：** 记录候选数量、成功路径error_type=None、model_calls=0。

**为什么与边界：** None不是“所有情况下无错误”，这里只展示已成功到达这一行的路径。

<a id="L15"></a>
### 第 15 行

```python
    print(json.dumps(trace, ensure_ascii=False))
```

**语法与数据变化：** 输出JSON而不输出问题和原文。

**为什么与边界：** 控制采集范围通常比事后猜敏感字段做正则脱敏更可靠。

<a id="L16"></a>
### 第 16 行

```python
    assert "question" not in trace and "authorization" not in trace
```

**语法与数据变化：** 明确断言trace不包含question和authorization两个禁字段。

**为什么与边界：** 这不是扫描所有可能秘密的完整安全审计；新的日志字段仍需逐一审查。

<a id="L17"></a>
### 第 17 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L18"></a>
### 第 18 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L19"></a>
### 第 19 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

输出duration_ms随机器变化，不应硬编码具体毫秒；model_calls=0。加入question或authorization字段应触发示例中的禁止字段断言。

## 只练一个关键点（不是新的学习验收记录）

1. 运行示例，列出实际输出的五个字段。
2. 将计时起点与load_documents顺序对照；不要新增问题/认证头/原文日志。
3. **复盘：** 报告是否含文件加载耗时？依据在哪？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
