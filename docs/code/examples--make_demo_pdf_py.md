# 构造有文本层的最小PDF：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/make_demo_pdf.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

为PDF读取实验生成可控、非私密的英文测试输入，避免系统字体差异。

### 输入、输出与调用关系

创建一页PDF并写入artifacts/demo.pdf。

### 运行与风险边界

先装本课ingest依赖，再运行 `python -m examples.make_demo_pdf`。

会覆盖同名生成文件；只用于实验，不是通用排版器，也不是OCR。不要把真实隐私文件作为测试替代。

## 完整源码

<!-- source: examples/make_demo_pdf.py -->
```python
#: 只生成虚构英文样例，避免额外字体依赖；生成物放在被 Git 忽略的 artifacts。
from pathlib import Path
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

#: PDF 文本需要字体资源和内容流；这是最小测试夹具，不是通用排版工具。
def main():
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=200)
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 30 150 Td (Webhook retries: 3.) Tj ET")
    page[NameObject("/Contents")] = stream
    target = Path("artifacts/demo.pdf")
    target.parent.mkdir(exist_ok=True)
    with target.open("wb") as handle:
        writer.write(handle)
    print(target)

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 只生成虚构英文样例，避免额外字体依赖；生成物放在被 Git 忽略的 artifacts。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：只生成虚构英文样例，避免额外字体依赖；生成物放在被 Git 忽略的 artifacts。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
from pypdf import PdfWriter
```

**语法与数据变化：** 从 `pypdf` 导入 `PdfWriter`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** PDF 文本层读取库。PdfReader 抽取可解析文本，不内置可靠 OCR，扫描页可能为空。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
```

**语法与数据变化：** 导入PDF内部字典、名称与内容流对象。

**为什么与边界：** 这些是PDF对象而不只是普通Python字符串键；用于构造最小字体资源和绘制文本指令。

<a id="L5"></a>
### 第 5 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L6"></a>
### 第 6 行

```python
#: PDF 文本需要字体资源和内容流；这是最小测试夹具，不是通用排版工具。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：PDF 文本需要字体资源和内容流；这是最小测试夹具，不是通用排版工具。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
    writer = PdfWriter()
```

**语法与数据变化：** 创建空PdfWriter，负责组织并序列化输出PDF。

**为什么与边界：** 此时还没有页面或磁盘文件。

<a id="L9"></a>
### 第 9 行

```python
    page = writer.add_blank_page(width=300, height=200)
```

**语法与数据变化：** 添加300×200的空白页并取得页面对象。

**为什么与边界：** 尺寸是PDF页面单位，不是文本token或图像像素；仅空白页没有文本层内容。

<a id="L10"></a>
### 第 10 行

```python
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
```

**语法与数据变化：** 构造字体字典：Type=Font、Subtype=Type1、BaseFont=Helvetica。

**为什么与边界：** NameObject带/名称语义，内置英文基础字体避免额外字体文件；不保证中文字体覆盖。

<a id="L11"></a>
### 第 11 行

```python
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
```

**语法与数据变化：** 把字体资源挂到页面Resources/Font下，给它本页别名F1。

**为什么与边界：** 内容流中的/F1必须在资源表中定义，否则文字渲染或解析可能不正确。

<a id="L12"></a>
### 第 12 行

```python
    stream = DecodedStreamObject()
```

**语法与数据变化：** 创建一个未编码的内容流对象。

**为什么与边界：** 它将承载PDF绘制操作字节，而不是直接把整页文本存成一个普通字段。

<a id="L13"></a>
### 第 13 行

```python
    stream.set_data(b"BT /F1 12 Tf 30 150 Td (Webhook retries: 3.) Tj ET")
```

**语法与数据变化：** 设置字节指令：BT开始文字，F1 12 Tf选字体字号，30 150 Td定位，Tj绘制字符串，ET结束。

**为什么与边界：** 这是真正可解析的文字操作，不是把文字截图；括号和PDF特殊字符在更复杂输入中需要转义。

<a id="L14"></a>
### 第 14 行

```python
    page[NameObject("/Contents")] = stream
```

**语法与数据变化：** 把流赋给页面Contents，连接页面与绘制操作。

**为什么与边界：** 字体表和内容流两者都需要，单有资源声明不会自动画字。

<a id="L15"></a>
### 第 15 行

```python
    target = Path("artifacts/demo.pdf")
```

**语法与数据变化：** 指定生成路径artifacts/demo.pdf。

**为什么与边界：** 它在忽略目录内，避免把生成二进制混入源码提交。

<a id="L16"></a>
### 第 16 行

```python
    target.parent.mkdir(exist_ok=True)
```

**语法与数据变化：** 创建父目录，已存在则不报错。

**为什么与边界：** 这里没有parents=True，只适用于这个一层目录；不要复制到深层路径后假设仍能自动建全树。

<a id="L17"></a>
### 第 17 行

```python
    with target.open("wb") as handle:
```

**语法与数据变化：** 以wb打开目标，准备写二进制，with负责关闭。

**为什么与边界：** wb会截断同名旧文件，确认这是可覆盖的实验产物。

<a id="L18"></a>
### 第 18 行

```python
        writer.write(handle)
```

**语法与数据变化：** PdfWriter将对象结构写入句柄，形成真实PDF文件。

**为什么与边界：** 这一步才写出完整格式，不是print一下路径就算生成成功。

<a id="L19"></a>
### 第 19 行

```python
    print(target)
```

**语法与数据变化：** 打印文件路径供后续提取脚本使用。

**为什么与边界：** 打印路径本身不能证明提取成功，仍需下一实验读取核对。

<a id="L20"></a>
### 第 20 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L21"></a>
### 第 21 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L22"></a>
### 第 22 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

成功后读取应能提取 Webhook retries: 3.；只有空白页不带内容流时不能提取到这句文本。

## 只练一个关键点（不是新的学习验收记录）

1. 确认artifacts/demo.pdf可覆盖后生成虚构PDF。
2. 再运行PDF集成测试核对文字提取，不把文件存在当内容正确。
3. **复盘：** 字体资源、内容流、页面分别负责什么？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
