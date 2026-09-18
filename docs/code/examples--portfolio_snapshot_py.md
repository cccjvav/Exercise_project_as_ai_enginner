# 从代码与数据生成可追溯基线报告：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/portfolio_snapshot.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

避免在作品集里手填提升百分比，用固定输入与版本指纹生成真实检索报告。

### 输入、输出与调用关系

读取手册与八题JSONL，写artifacts/baseline-report.json。

### 运行与风险边界

`python -m examples.portfolio_snapshot`，离线运行；会覆盖同名生成报告。

只覆盖词检索开发基线，未评估生成答案；哈希不是隐私保护或通用签名。

## 完整源码

<!-- source: examples/portfolio_snapshot.py -->
```python
#: 从当前代码和数据生成真实基线报告；不手填改善百分比或模型效果。
import hashlib
import json
from pathlib import Path
from evidencedesk.documents import load_documents
from evidencedesk.evaluate import evaluate

#: 哈希含文件名及内容，用于识别语料变动；不是将 hash 当隐私保护。
def main():
    paths = sorted(Path("data/sample").glob("*.md")) + [Path("data/questions.jsonl")]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.as_posix().encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    rows = [json.loads(line) for line in Path("data/questions.jsonl").read_text(encoding="utf-8").splitlines()]
    result = {"system": "lexical-baseline", "dataset_sha256": digest.hexdigest(),
              "synthetic_data": True, "question_count": len(rows),
              "metrics": evaluate(rows, load_documents(Path("data/sample")), 1),
              "limitations": ["公开开发题不是最终测试集", "未评估生成答案", "q06 有隐含 Webhook 上下文"]}
    target = Path("artifacts/baseline-report.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 从当前代码和数据生成真实基线报告；不手填改善百分比或模型效果。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：从当前代码和数据生成真实基线报告；不手填改善百分比或模型效果。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import hashlib
```

**语法与数据变化：** 导入 `hashlib` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库摘要算法。sha256 接收字节，hexdigest 返回十六进制文本；哈希可作内容指纹，不是加密、权限校验或真实性认证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

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
from evidencedesk.documents import load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from evidencedesk.evaluate import evaluate
```

**语法与数据变化：** 从 `evidencedesk.evaluate` 导入 `evaluate`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** evaluate按固定标注分组计算Recall、MRR与无答案空返回率，保留每题结果；gold不传给检索器。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
#: 哈希含文件名及内容，用于识别语料变动；不是将 hash 当隐私保护。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：哈希含文件名及内容，用于识别语料变动；不是将 hash 当隐私保护。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
    paths = sorted(Path("data/sample").glob("*.md")) + [Path("data/questions.jsonl")]
```

**语法与数据变化：** 手册路径排序后追加原八题路径，固定摘要输入顺序。

**为什么与边界：** 不是自动扫描全部项目数据，九题回归副本不在此脚本默认输入中。

<a id="L11"></a>
### 第 11 行

```python
    digest = hashlib.sha256()
```

**语法与数据变化：** 创建可逐次update的SHA-256摘要对象。

**为什么与边界：** 还没有最终指纹，必须按确定顺序喂入全部输入。

<a id="L12"></a>
### 第 12 行

```python
    for path in paths:
```

**语法与数据变化：** 依次处理每个被纳入报告的文件。

**为什么与边界：** 路径缺失或不可读会失败，不能跳过后仍称同版本报告。

<a id="L13"></a>
### 第 13 行

```python
        digest.update(path.as_posix().encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
```

**语法与数据变化：** 将路径UTF-8字节、零字节分隔符、文件原字节再加分隔符送入摘要。

**为什么与边界：** 将名字纳入版本，使重命名也被识别；这是教学组合编码，不是任意二进制结构的通用规范化/签名协议。

<a id="L14"></a>
### 第 14 行

```python
    rows = [json.loads(line) for line in Path("data/questions.jsonl").read_text(encoding="utf-8").splitlines()]
```

**语法与数据变化：** 逐行解析JSONL为题目列表。

**为什么与边界：** 这里不像evaluate CLI那样过滤空白行，额外空行可能导致解析错误，需要保持文件约定。

<a id="L15"></a>
### 第 15 行

```python
    result = {"system": "lexical-baseline", "dataset_sha256": digest.hexdigest(),
```

**语法与数据变化：** 开始报告，写明词法系统及输入摘要。

**为什么与边界：** 不是只保存一个孤立分数，才能让日后知道用的是哪份数据。

<a id="L16"></a>
### 第 16 行

```python
              "synthetic_data": True, "question_count": len(rows),
```

**语法与数据变化：** 显式标注虚构数据与题数。

**为什么与边界：** 公开小样例不能当真实企业数据或留出测试集。

<a id="L17"></a>
### 第 17 行

```python
              "metrics": evaluate(rows, load_documents(Path("data/sample")), 1),
```

**语法与数据变化：** 调用当前evaluate，以k=1计算真实参考指标。

**为什么与边界：** 不是把预期5/6手填进去，代码变化会反映在输出中。

<a id="L18"></a>
### 第 18 行

```python
              "limitations": ["公开开发题不是最终测试集", "未评估生成答案", "q06 有隐含 Webhook 上下文"]}
```

**语法与数据变化：** 把数据公开性、未测生成和q06上下文假设写进限制列表。

**为什么与边界：** 这些限制应随作品报告一起展示，不能只留下漂亮分数。

<a id="L19"></a>
### 第 19 行

```python
    target = Path("artifacts/baseline-report.json")
```

**语法与数据变化：** 指定生成报告路径。

**为什么与边界：** artifacts按仓库规则忽略，不把每次运行产物当源码提交。

<a id="L20"></a>
### 第 20 行

```python
    target.parent.mkdir(exist_ok=True)
```

**语法与数据变化：** 创建父目录，允许已存在。

**为什么与边界：** 此固定路径只有一层；不是递归建立任意深层目录。

<a id="L21"></a>
### 第 21 行

```python
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
```

**语法与数据变化：** 将整个结果格式化为UTF-8 JSON并写文件。

**为什么与边界：** 会覆盖旧报告，正式对照应另存带版本名称的产物，避免丢失历史。

<a id="L22"></a>
### 第 22 行

```python
    print(target)
```

**语法与数据变化：** 打印报告位置方便打开。

**为什么与边界：** 路径输出不是云上传或部署成功的证明。

<a id="L23"></a>
### 第 23 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L24"></a>
### 第 24 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L25"></a>
### 第 25 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

相同文件路径与字节内容给相同指纹；更改标题/题集会改变输入摘要。报告明确synthetic_data和限制，不能把它当在线模型质量报告。

## 只练一个关键点（不是新的学习验收记录）

1. 运行离线脚本前确认报告可覆盖，打开生成JSON并记录数据摘要。
2. 对照它读取的是原八题，另保存九题命令输出；不要手改指标制造提升。
3. **复盘：** 数据版本指纹为何必须与题集范围和限制一起展示？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
