# 1A：读取一份文档——先看完整实例，再逐行理解

[全部课程](../course/index.md) · [下一课：可靠文档加载](01b-structured-loading.md)

后续课程已提前备齐，但学习进度仍从这一课开始。

本课只解决一个问题：**把磁盘上的手册，变成后续程序可以使用的字段。** 不做搜索，不调用大模型，不要求你先搭 Python 包。

## 一、完整示例

文件：`examples/01_read_document.py`。以下代码与仓库示例一致，不用自己从空白写起。

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

## 二、逐行解释：语法 → 数据变化 → 为什么需要

下列行号对应源文件，空行只用于分组，不执行操作。

### 第 1 行：`from pathlib import Path`

从 Python 自带的 `pathlib` 模块导入 `Path` 类。它用于表达文件路径和操作文件，不需要 pip 安装。

**为什么用它？** 不必自己拼接 Windows 的反斜杠和 Linux/macOS 的斜杠。

### 第 3 行：`ROOT = Path(__file__).resolve().parents[1]`

- `__file__` 是当前这个脚本文件的位置，不是你在终端里所在的位置。
- `Path(...)` 把位置包装为路径对象；这一步还没读取手册内容。
- `.resolve()` 得到解析后的绝对路径。
- `.parents[0]` 是 `examples/`，`.parents[1]` 是它上一级，也就是仓库根目录。索引从 0 开始。
- `ROOT` 是变量名；全大写是一种“当作常量使用”的约定，不是 Python 强制只读。

**为什么这样找根目录？** 即便从另一个工作目录运行脚本，它也能找到数据。但这依赖示例位于根目录下一层的 `examples/`；移动脚本层级就需要调整。后续工程化时再提供配置参数。

此示例应保存为 `.py` 文件运行；不要逐行粘贴进 notebook，因为 notebook 通常没有 `__file__`。

### 第 4 行：`path = ROOT / "data" / "sample" / "webhook-delivery.md"`

这里的 `/` 是 Path 提供的路径拼接操作，不是数字除法。

结果是指向手册文件的 `Path` 对象。这一步不验证文件存在，也不读取内容。

### 第 5 行：`raw_text = path.read_text(encoding="utf-8")`

真正打开文件，把字节按 UTF-8 解码为 Python 字符串 `str`，保存到 `raw_text`，读完后自动关闭文件。

**为什么指定编码？** 我们的手册包含中文且采用 UTF-8，明确编码避免依赖不同电脑的默认设置。不应宣称“删掉 encoding 就一定报错”：默认编码也可能恰好是 UTF-8。

路径错误会报 `FileNotFoundError`；没有权限或编码不匹配也会产生相应异常，不应把错误当成“没有相关文档”。

### 第 6 行：`lines = raw_text.splitlines()`

把一个完整字符串按换行拆成字符串列表 `list[str]`，每项末尾不保留换行符。例如：

```python
"# 示例标题\n\n第一段。\n".splitlines()
# 得到 ["# 示例标题", "", "第一段。"]
```

**为什么拆行？** 我们约定第一行是标题，剩余行是正文。中间空行仍保留为空字符串。

### 第 8 行：`document_id = path.stem`

取最后一级文件名去掉扩展名：`webhook-delivery.md` → `webhook-delivery`。

它取决于文件名，不是标题文本；将来改文件名会影响引用和评测 ID。

### 第 9 行：`title = lines[0].removeprefix("# ").strip()`

按从左到右的顺序执行：

1. `lines[0]` 取第一行，例如 `# Webhook 投递与重试`。
2. `.removeprefix("# ")` 去掉开头精确匹配的 `# `，得到 `Webhook 投递与重试`。
3. `.strip()` 去掉两端空白，不删除标题中间的空格。

**注意局限：** `removeprefix` 不会验证标题是否合法；没有这个前缀就原样返回。空文件的 `lines[0]` 则会报 `IndexError`。本课先观察正常数据流，下一小课专门引入校验，不把这段当成可靠的生产加载器。

### 第 10 行：`body = "\n".join(lines[1:]).strip()`

- `lines[1:]` 是从第二行到最后一行的列表切片，不包含标题。
- `"\n".join(...)` 用换行符把这些行重新连接成一个字符串。
- `.strip()` 去掉正文开头/结尾的空白，内部段落空行仍保留。

**为什么不直接拼成 `"".join(...)`？** 那样会丢失行与行之间的分隔，可能把独立句子或表格行粘在一起。

这是提取原文，不是摘要，也没有“理解”或改写内容。

### 第 11 行：`source = path.relative_to(ROOT / "data" / "sample").as_posix()`

- `.relative_to(...)` 取得相对于数据目录的位置，这里是 `webhook-delivery.md`。
- `.as_posix()` 转成统一用 `/` 分隔的字符串。

**为什么不直接输出绝对路径？** 来源标识不应依赖你电脑的用户名或目录结构。ID 用于身份，source 用于定位来源，本课二者相似但作用不同。

### 第 13 行：`print(f"ID: {document_id}")`

`f"..."` 是格式化字符串，会把花括号中的变量值嵌入文本；`print` 将结果显示到终端。

### 第 14 行：`print(f"标题: {title}")`

同理，打印已提取的标题，不会重新读文件。

### 第 15 行：`print(f"来源: {source}")`

打印相对来源路径，不是网页链接，也不是自动验证过的引用。

### 第 16 行：`print("正文:")`

只打印固定标签，帮助人阅读输出。

### 第 17 行：`print(body)`

打印正文字符串；其中的换行会在终端中正常显示。至此完成“文件 → 字符串 → 行列表 → 字段”的转换。

## 三、先运行，不必先改

1. 用编辑器打开本仓库，在仓库根目录打开终端。
2. 运行 `python --version`，本项目约定使用 Python 3.11+。如果系统使用 `python3` 或 Windows 的 `py`，后续命令统一替换对应解释器名。
3. 运行：

```bash
python examples/01_read_document.py
```

不用创建虚拟环境或安装第三方包；此示例只用标准库。开始使用依赖时再讲环境隔离。

预期输出开头：

```text
ID: webhook-delivery
标题: Webhook 投递与重试
来源: webhook-delivery.md
正文:
本文描述虚构产品 Northstar Cloud 的练习规则，不对应任何真实服务。
```

后面应继续打印全部正文，包括“最多执行 3 次重试”。不是只有上面这五行。

## 四、唯一必做实操：替换输入文件

**目的：** 验证你理解字段来自文件，而不是程序里写死的一份答案。

1. 打开 `examples/01_read_document.py`。
2. 只把第 4 行的 `"webhook-delivery.md"` 替换为 `"api-key-policy.md"`，其余代码不改。
3. 运行前先预测：ID、标题、来源是否会一起变化？正文是否仍会包含“最多执行 3 次重试”？
4. 运行同一个命令：`python examples/01_read_document.py`。
5. 对照预期：

```text
ID: api-key-policy
标题: API 密钥管理与签名校验
来源: api-key-policy.md
```

正文应来自密钥手册，不应再含“最多执行 3 次重试”。若仍显示旧内容，先检查是否保存文件、是否运行了同一份脚本。

6. 将输出前三行和一句解释发给导师；核对完可将文件名恢复为原值，保留示例初始状态。

**只需要解释：为什么我们仅改了一处，ID、标题和正文都变了？** 不要求默写这 17 行。

## 五、验证与反思

本课成功不是“建好了 RAG”，而是能说明：路径是位置，`read_text` 才读取内容；后续字段由读取的内容或路径派生。

还没有实现：多文档加载、格式校验、检索、LLM 回答、自动拒答、权限或来源可信度验证。此脚本顶层会直接执行，暂时不作为可导入库；下一小课再示范函数封装与入口保护。

导师已验证基础示例不等于学习者已完成实操。等你给出观察结果，我们才记录本课理解是否通过，再继续阶段 1 内的下一小课；整阶段结束仍会询问是否进入阶段 2。

参考：Python 官方 [pathlib](https://docs.python.org/3/library/pathlib.html) 与 [字符串方法](https://docs.python.org/3/library/stdtypes.html#string-methods)。目前只需查本课使用到的方法。
