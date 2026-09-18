# 第一份文档的完整读取路径：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/01_read_document.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用最少标准库语句展示文件到字符串、行列表、字段的转换；原1A还保留了更多入门演算。

### 输入、输出与调用关系

输入固定手册路径，输出人读的字段与正文；不是可靠加载器，也不生成Document对象。

### 运行与风险边界

`python examples/01_read_document.py`；可从源码定位仓库，不依赖当前工作目录。

只读虚构文件。空文件和格式错误没有健壮检查，不应替代documents.py的业务入口。

## 完整源码

<!-- source: examples/01_read_document.py -->
```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "sample" / "webhook-delivery.md"
raw_text = path.read_text(encoding="utf-8")
lines = raw_text.splitlines()

document_id = path.stem
title = lines[0].removeprefix("# ").strip()
body = "\n".join(lines[1:]).strip()
source = path.relative_to(ROOT / "data" / "sample").as_posix()

print(f"ID: {document_id}")
print(f"标题: {title}")
print(f"来源: {source}")
print("正文:")
print(body)
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L2"></a>
### 第 2 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L3"></a>
### 第 3 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** __file__是此脚本路径，resolve转绝对规范路径，parents[1]取examples的上一级仓库目录。

**为什么与边界：** 不能在没有__file__的普通notebook单元里原样使用；移动脚本层级也要调整父级数。

<a id="L4"></a>
### 第 4 行

```python
path = ROOT / "data" / "sample" / "webhook-delivery.md"
```

**语法与数据变化：** Path的/逐段拼接data、sample和文件名，得到Path对象。

**为什么与边界：** 这不是数值除法，也尚未检查文件存在；路径指定了要读哪份真实输入。

<a id="L5"></a>
### 第 5 行

```python
raw_text = path.read_text(encoding="utf-8")
```

**语法与数据变化：** 以UTF-8打开文件并读成str，保存raw_text，读完自动关闭。

**为什么与边界：** 中文应使用约定编码；缺文件、权限不足、非法字节都可能报错，不能当作空结果。

<a id="L6"></a>
### 第 6 行

```python
lines = raw_text.splitlines()
```

**语法与数据变化：** splitlines把全文拆为字符串列表，每项去掉行尾换行，内部空行仍是空字符串。

**为什么与边界：** 例如'# 标题\n\n正文'得到三项；空文件会是空列表，下面直接索引并不安全。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
document_id = path.stem
```

**语法与数据变化：** stem去掉最后一级文件名的扩展名，成为文档ID。

**为什么与边界：** webhook-delivery.md得到webhook-delivery；ID来自路径而不是标题。

<a id="L9"></a>
### 第 9 行

```python
title = lines[0].removeprefix("# ").strip()
```

**语法与数据变化：** 取首行，removeprefix去掉精确'# '前缀，再strip两端空白。

**为什么与边界：** 没有该前缀会原样保留，并不自动报错；首行不存在会IndexError，1B才补严格校验。

<a id="L10"></a>
### 第 10 行

```python
body = "\n".join(lines[1:]).strip()
```

**语法与数据变化：** 取第二行到最后，使用换行join再清理整体首尾空白。

**为什么与边界：** 不能用空串join，否则行与行粘连；这是保留正文，不是模型摘要。

<a id="L11"></a>
### 第 11 行

```python
source = path.relative_to(ROOT / "data" / "sample").as_posix()
```

**语法与数据变化：** 计算相对语料目录的路径，再转为统一斜杠格式。

**为什么与边界：** 不输出本机绝对路径；source用于回查，ID用于身份，两者作用不同。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
print(f"ID: {document_id}")
```

**语法与数据变化：** f-string把document_id插入文本，print写到终端标准输出。

**为什么与边界：** 这是面向人的展示格式，不是机器JSON接口。

<a id="L14"></a>
### 第 14 行

```python
print(f"标题: {title}")
```

**语法与数据变化：** 同样输出标题变量的当前值。

**为什么与边界：** 打印不会重新读取文件，也不会验证标题真实有效。

<a id="L15"></a>
### 第 15 行

```python
print(f"来源: {source}")
```

**语法与数据变化：** 输出前面算好的相对来源。

**为什么与边界：** 看起来像文件名不等于网页链接，更不等于证据已审核。

<a id="L16"></a>
### 第 16 行

```python
print("正文:")
```

**语法与数据变化：** 输出固定“正文:”标签，给读者划分字段区域。

**为什么与边界：** 只是文字，不会改变body字符串。

<a id="L17"></a>
### 第 17 行

```python
print(body)
```

**语法与数据变化：** 输出body本身，字符串内换行会在终端换行。

**为什么与边界：** 至此仅完成读取展示，没有检索排序、权限或答案生成。

## 跟一遍数据与验证边界

把文件名改为api-key-policy.md后，ID、来源和正文随输入改变；只改标题内容，文件派生ID不变。详细课堂记录见1A。

## 只练一个关键点（不是新的学习验收记录）

1. 先读原1A示例，再运行本页命令一次；记下ID、标题、来源三项。
2. 只在临时副本改标题再读取，逐项比较变化；不要改正式语料ID或金标准。
3. **复盘：** 哪些字段来自路径，哪些来自文件内容？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
