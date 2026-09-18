# PDF文本提取与编码器计数：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/pdf_tokens.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

分清页码、正文字符数和特定token编码的长度，遇到无文本层要明确停止。

### 输入、输出与调用关系

输入有权限读取的PDF路径；逐页输出页码、字符数、token数。

### 运行与风险边界

`python -m examples.pdf_tokens artifacts/demo.pdf`；依赖pypdf/tiktoken，编码表首次加载可能联网。

不解密未授权文件、不做OCR。本环境先前编码表下载遇TLS问题，补写文档不等于已恢复计数验证，不应关闭TLS绕过。

## 完整源码

<!-- source: examples/pdf_tokens.py -->
```python
#: PyPDF 提取文本层，tiktoken 计算某一种编码的 token；两者不负责 OCR。
import argparse
from pypdf import PdfReader
import tiktoken

#: PDF 必须是你有权使用的文件；本脚本只打印长度，避免无意输出原文。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    args = parser.parse_args()
    reader = PdfReader(args.pdf)
    if reader.is_encrypted:
        raise ValueError("请先通过有授权的流程解密")
    #: 页码从 1 开始；空提取结果是待处理问题，不能静默当成无内容。
    for page_number, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        if not text:
            raise ValueError(f"第 {page_number} 页无文本层，可能需要 OCR")
        #: 首次加载编码表可能下载缓存；网络失败不应通过关闭 TLS 校验来绕过。
        encoding = tiktoken.get_encoding("cl100k_base")
        token_ids = encoding.encode(text, disallowed_special=())
        print({"page": page_number, "characters": len(text), "tokens": len(token_ids)})

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: PyPDF 提取文本层，tiktoken 计算某一种编码的 token；两者不负责 OCR。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：PyPDF 提取文本层，tiktoken 计算某一种编码的 token；两者不负责 OCR。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
from pypdf import PdfReader
```

**语法与数据变化：** 从 `pypdf` 导入 `PdfReader`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** PDF 文本层读取库。PdfReader 抽取可解析文本，不内置可靠 OCR，扫描页可能为空。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
import tiktoken
```

**语法与数据变化：** 导入tiktoken分词编码库，不是中文分词器或PDF识别工具。

**为什么与边界：** get_encoding可能下载编码表；包可导入不代表下载和计数已完成。

<a id="L5"></a>
### 第 5 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L6"></a>
### 第 6 行

```python
#: PDF 必须是你有权使用的文件；本脚本只打印长度，避免无意输出原文。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：PDF 必须是你有权使用的文件；本脚本只打印长度，避免无意输出原文。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L7"></a>
### 第 7 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L8"></a>
### 第 8 行

```python
    parser = argparse.ArgumentParser()
```

**语法与数据变化：** 创建参数解析器供终端传PDF路径。

**为什么与边界：** 解析器只管参数形状，不判断文件是否合法或有权限。

<a id="L9"></a>
### 第 9 行

```python
    parser.add_argument("pdf")
```

**语法与数据变化：** 注册必填位置参数pdf，不带--前缀。

**为什么与边界：** 遗漏路径会在parse_args阶段报用法错误。

<a id="L10"></a>
### 第 10 行

```python
    args = parser.parse_args()
```

**语法与数据变化：** 解析终端参数，通过args.pdf取得字符串路径。

**为什么与边界：** 与Path转换例子不同，这里没有设置type=Path，PdfReader可接受这个路径字符串。

<a id="L11"></a>
### 第 11 行

```python
    reader = PdfReader(args.pdf)
```

**语法与数据变化：** 打开并解析PDF结构，创建reader。

**为什么与边界：** 文件缺失、损坏或解析不支持都可能在这里失败，不是返回“知识库无答案”。

<a id="L12"></a>
### 第 12 行

```python
    if reader.is_encrypted:
```

**语法与数据变化：** 检查PDF是否加密。

**为什么与边界：** 不能默默尝试绕过加密，也不把读不到内容归咎于检索器。

<a id="L13"></a>
### 第 13 行

```python
        raise ValueError("请先通过有授权的流程解密")
```

**语法与数据变化：** 明确拒绝，要求先走有授权的解密流程。

**为什么与边界：** 此脚本没有接收或记录密码的逻辑。

<a id="L14"></a>
### 第 14 行

```python
    #: 页码从 1 开始；空提取结果是待处理问题，不能静默当成无内容。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：页码从 1 开始；空提取结果是待处理问题，不能静默当成无内容。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L15"></a>
### 第 15 行

```python
    for page_number, page in enumerate(reader.pages, 1):
```

**语法与数据变化：** enumerate从1开始给页面编号。

**为什么与边界：** 这是人读页码，区别于底层列表从0索引；以后引用要说明页码约定。

<a id="L16"></a>
### 第 16 行

```python
        text = (page.extract_text() or "").strip()
```

**语法与数据变化：** extract_text尝试读文本层，None回退空串，strip清理两端空白。

**为什么与边界：** 不进行OCR或布局语义恢复，表格顺序和复杂排版仍可能不理想。

<a id="L17"></a>
### 第 17 行

```python
        if not text:
```

**语法与数据变化：** 如果清理后的文本为空，进入失败分支。

**为什么与边界：** 不能静默跳过并宣称整份PDF已成功入库。

<a id="L18"></a>
### 第 18 行

```python
            raise ValueError(f"第 {page_number} 页无文本层，可能需要 OCR")
```

**语法与数据变化：** 带页码报错，提示可能需要OCR。

**为什么与边界：** “可能”不是确定诊断，也可能有提取器不支持的结构，需要检查原页。

<a id="L19"></a>
### 第 19 行

```python
        #: 首次加载编码表可能下载缓存；网络失败不应通过关闭 TLS 校验来绕过。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：首次加载编码表可能下载缓存；网络失败不应通过关闭 TLS 校验来绕过。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L20"></a>
### 第 20 行

```python
        encoding = tiktoken.get_encoding("cl100k_base")
```

**语法与数据变化：** 加载指定cl100k_base编码。

**为什么与边界：** 它对应特定token规则，不是所有模型通用；网络或缓存失败应如实标待验。

<a id="L21"></a>
### 第 21 行

```python
        token_ids = encoding.encode(text, disallowed_special=())
```

**语法与数据变化：** 把文本编码为token ID列表，disallowed_special=()不把特殊样式字符串作为禁止项抛错。

**为什么与边界：** 这不意味着自动把它们当成模型特殊指令token；仍按编码器规则处理文本。

<a id="L22"></a>
### 第 22 行

```python
        print({"page": page_number, "characters": len(text), "tokens": len(token_ids)})
```

**语法与数据变化：** 打印页码和两种长度，不输出整页正文。

**为什么与边界：** 减少终端泄露原文；tokens计数不是实际费用，还需模型计费规则及输入输出用量。

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

可解析英文样例应有非空text；扫描或纯图形页可能无文本。字符长度与token长度不相等，换编码器后token数可能变。

## 只练一个关键点（不是新的学习验收记录）

1. 先确认有权读取文件；阅读空页测试和本页风险，不为计数关闭TLS。
2. 若编码表不可用，记录失败位置并停在待验；能加载后再比较characters与tokens。
3. **复盘：** 提取失败和编码器下载失败为何是两类问题？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
