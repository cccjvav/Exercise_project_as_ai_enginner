# 重跑与正文更新的对照：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/chunk_versions.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

验证幂等重建与正文变化后旧块被剔除，而不是只看函数没报错。

### 输入、输出与调用关系

读取首份样例文档，在内存中生成索引和更新后的快照；不改原手册。

### 运行与风险边界

`python -m examples.chunk_versions`，标准库加本项目组件。

索引只是内存字典。浅拷贝并不等于持久化事务或并发安全更新。

## 完整源码

<!-- source: examples/chunk_versions.py -->
```python
#: replace 为 frozen 数据类创建修改后的副本，而不是原地写入。
from pathlib import Path
from dataclasses import replace
from evidencedesk.documents import load_documents
from evidencedesk.ingest import chunks, replace_document

#: 同样输入重复导入得到同一结果，这是幂等；不是“没有异常”就算幂等。
def main():
    doc = load_documents(Path("data/sample"))[0]
    index = replace_document({}, doc)
    assert replace_document(index, doc) == index
    #: 增加内容会换版本；确认新快照没有旧块，避免过期内容继续被搜到。
    changed = replace(doc, text=doc.text + "\n练习：增加一条说明。")
    new_index = replace_document(index, changed)
    assert set(index).isdisjoint(new_index)
    print({"initial_chunks": len(chunks(doc)), "updated_chunks": len(new_index), "old_chunks_removed": True})

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: replace 为 frozen 数据类创建修改后的副本，而不是原地写入。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：replace 为 frozen 数据类创建修改后的副本，而不是原地写入。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
from dataclasses import replace
```

**语法与数据变化：** 导入dataclasses.replace，它按字段创建数据类的新对象。

**为什么与边界：** 不同于字符串replace或字典update；可用于frozen的Document而不原地赋值。

<a id="L4"></a>
### 第 4 行

```python
from evidencedesk.documents import load_documents
```

**语法与数据变化：** 从 `evidencedesk.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from evidencedesk.ingest import chunks, replace_document
```

**语法与数据变化：** 从 `evidencedesk.ingest` 导入 `chunks, replace_document`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** chunks生成含父ID、版本和字符偏移的块；replace_document返回替换该父文档后的新索引字典，不自动持久化。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

```python
#: 同样输入重复导入得到同一结果，这是幂等；不是“没有异常”就算幂等。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：同样输入重复导入得到同一结果，这是幂等；不是“没有异常”就算幂等。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L8"></a>
### 第 8 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L9"></a>
### 第 9 行

```python
    doc = load_documents(Path("data/sample"))[0]
```

**语法与数据变化：** 加载按路径排序的文档列表并取第一项。

**为什么与边界：** 依赖样例目录非空；第一项是排序结果而不是“最重要”的文档。

<a id="L10"></a>
### 第 10 行

```python
    index = replace_document({}, doc)
```

**语法与数据变化：** 从空索引导入这份文档，获得以块ID为键的字典。

**为什么与边界：** 赋值接住新快照；replace_document不就地修改原来的空字典。

<a id="L11"></a>
### 第 11 行

```python
    assert replace_document(index, doc) == index
```

**语法与数据变化：** 再次导入相同文档并比较整个字典。

**为什么与边界：** 相等验证内容和键不增长，仅len相同不足以证明幂等。

<a id="L12"></a>
### 第 12 行

```python
    #: 增加内容会换版本；确认新快照没有旧块，避免过期内容继续被搜到。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：增加内容会换版本；确认新快照没有旧块，避免过期内容继续被搜到。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L13"></a>
### 第 13 行

```python
    changed = replace(doc, text=doc.text + "\n练习：增加一条说明。")
```

**语法与数据变化：** 用replace创建changed，只替换text为旧正文加一行，其他字段保留。

**为什么与边界：** 原doc和磁盘文件不变；父ID保持才能定位要替换的旧块。

<a id="L14"></a>
### 第 14 行

```python
    new_index = replace_document(index, changed)
```

**语法与数据变化：** 将changed替换进旧索引，保存新字典。

**为什么与边界：** 旧index仍可作为对照，当前例子没有正式数据库发布步骤。

<a id="L15"></a>
### 第 15 行

```python
    assert set(index).isdisjoint(new_index)
```

**语法与数据变化：** set(index)取旧键，isdisjoint检查与新字典键没有交集。

**为什么与边界：** 正文版本进入所有块身份，所以本例全部换ID；若索引还含别的文档，这个整集合断言就不适用。

<a id="L16"></a>
### 第 16 行

```python
    print({"initial_chunks": len(chunks(doc)), "updated_chunks": len(new_index), "old_chunks_removed": True})
```

**语法与数据变化：** 打印初始块数、更新后块数与已通过断言的移除标志。

**为什么与边界：** True是前面检查后的演示摘要，不是生产持久化确认；块数可能不变而ID已改变。

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

相同文档重复replace应完全相等；追加正文构造副本后，新旧键集合应不相交。这里的初始索引仅含这一份文档。

## 只练一个关键点（不是新的学习验收记录）

1. 从仓库根运行示例，定位三个assert依赖的输入。
2. 在临时实验中比较原doc与replace后的changed，确认原正文没有被修改。
3. **复盘：** 为什么只看updated_chunks数量不能证明旧块清理？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
