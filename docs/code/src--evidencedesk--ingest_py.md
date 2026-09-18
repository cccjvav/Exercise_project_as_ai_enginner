# 可追溯字符分块与替换更新：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/ingest.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把长正文切成有来源与版本的块，重跑相同输入保持块身份，正文更新后移除该文档旧块。

### 输入、输出与调用关系

chunks 输入 Document/窗口参数，输出字典列表；replace_document 输入内存索引和新 Document，返回新的顶层字典。它尚未自动接入 search。

### 运行与风险边界

离线运行 `python -m examples.chunk_versions`。先理解字符窗口，再看哈希；不需要模型或数据库。

不是持久化索引、不是数据库事务。字典拷贝是浅拷贝；正文 hash 不涵盖 title/ACL/source 等全部元数据。

## 完整源码

<!-- source: src/evidencedesk/ingest.py -->
```python
#: 哈希记录内容版本；JSON 编码复合身份避免拼接歧义。
import hashlib
import json
from .documents import Document

#: 本实现按字符分块，绝非 token 分块；步长必须正，否则可能死循环。
def chunks(doc: Document, size: int = 120, overlap: int = 20) -> list[dict]:
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("要求整数且 0 <= overlap < size")
    version = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
    result = []
    #: 半开区间 [start,end) 可直接定位 Python 字符串；版本变化时全部块 ID 变化。
    for start in range(0, len(doc.text), size - overlap):
        end = min(start + size, len(doc.text))
        identity = json.dumps([doc.id, version, size, overlap, start], ensure_ascii=False)
        chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        result.append({"id": chunk_id, "parent_id": doc.id, "version": version,
                       "source": doc.source, "start": start, "end": end, "text": doc.text[start:end]})
        if end == len(doc.text):
            break
    return result

#: 先剔除该父文档旧块，再合入新块；返回新字典，校验失败也不破坏旧索引。
def replace_document(index: dict[str, dict], doc: Document, size: int = 120) -> dict[str, dict]:
    updated = {key: value for key, value in index.items() if value["parent_id"] != doc.id}
    updated.update({chunk["id"]: chunk for chunk in chunks(doc, size)})
    return updated
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 哈希记录内容版本；JSON 编码复合身份避免拼接歧义。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：哈希记录内容版本；JSON 编码复合身份避免拼接歧义。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
from .documents import Document
```

**语法与数据变化：** 从 `.documents` 导入 `Document`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L6"></a>
### 第 6 行

```python
#: 本实现按字符分块，绝非 token 分块；步长必须正，否则可能死循环。
```

**语法与数据变化：** 这条注释强调字符窗口和正步长；注释本身不实施检查。

**为什么与边界：** 准确边界是下面会先拒绝非法参数；若绕过检查，本文件用的 range 步长为 0 会报 ValueError，而非真的在这里无限循环。

<a id="L7"></a>
### 第 7 行

```python
def chunks(doc: Document, size: int = 120, overlap: int = 20) -> list[dict]:
```

**语法与数据变化：** 定义 chunks，默认最多120字符、重叠20字符，返回块字典列表。

**为什么与边界：** size/overlap 是字符参数不是 token；如果只改 size 为4而不改默认 overlap=20，会触发非法参数检查。

<a id="L8"></a>
### 第 8 行

```python
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
```

**语法与数据变化：** type 精确比较排除 bool/浮点/字符串；链式比较要求 0≤overlap<size。

**为什么与边界：** 该约束同时保证 size 正且 size-overlap>0；类型提示本身不能替代这条运行时检查。

<a id="L9"></a>
### 第 9 行

```python
        raise ValueError("要求整数且 0 <= overlap < size")
```

**语法与数据变化：** 参数不合法立即抛 ValueError。

**为什么与边界：** 调用方不能把它当成空文档或“质量不佳”；应先修正分块设置。

<a id="L10"></a>
### 第 10 行

```python
    version = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
```

**语法与数据变化：** 正文先 encode 成 UTF-8 字节，再算 SHA-256，hexdigest 得到稳定十六进制版本指纹。

**为什么与边界：** 相同正文同版本，字符变化通常改变摘要；title、来源和权限变化不会反映在此摘要，生产版本设计需另补。

<a id="L11"></a>
### 第 11 行

```python
    result = []
```

**语法与数据变化：** 创建本次调用的块结果列表。

**为什么与边界：** 空正文会让后面的 range 不迭代，返回 []；单独调用 chunks 不会重新执行 Markdown 加载器的非空校验。

<a id="L12"></a>
### 第 12 行

```python
    #: 半开区间 [start,end) 可直接定位 Python 字符串；版本变化时全部块 ID 变化。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：半开区间 [start,end) 可直接定位 Python 字符串；版本变化时全部块 ID 变化。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L13"></a>
### 第 13 行

```python
    for start in range(0, len(doc.text), size - overlap):
```

**语法与数据变化：** range 从0开始，不到正文长度为止，每次加 size-overlap；start 是正文字符偏移。

**为什么与边界：** 不是块编号。overlap=2,size=4 时起点理论序列为0,2,4…，但后面的 break 会提前结束。

<a id="L14"></a>
### 第 14 行

```python
        end = min(start + size, len(doc.text))
```

**语法与数据变化：** min 取窗口右端与全文长度的较小值。

**为什么与边界：** 末块可不足 size；右端不能超出正文。Python 切片本身容忍越界，但记录正确 end 才能准确定位。

<a id="L15"></a>
### 第 15 行

```python
        identity = json.dumps([doc.id, version, size, overlap, start], ensure_ascii=False)
```

**语法与数据变化：** 把父ID、正文版本、size、overlap、start 放进 JSON 列表字符串。

**为什么与边界：** 这种复合身份避免简单拼接造成歧义，例如不同字段边界拼出同一串；参数变化也会改变块身份。

<a id="L16"></a>
### 第 16 行

```python
        chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
```

**语法与数据变化：** 对复合身份的 UTF-8 字节取摘要，得到此块 ID。

**为什么与边界：** 它与 parent_id 不同：同一父文档的块共享 parent_id，但起点不同会产生不同身份输入。哈希不是访问控制。

<a id="L17"></a>
### 第 17 行

```python
        result.append({"id": chunk_id, "parent_id": doc.id, "version": version,
```

**语法与数据变化：** 开始构造块字典并追加：id 是块标识，parent_id 来自 doc.id，version 来自正文摘要。

**为什么与边界：** 这是 append 的跨行参数，尚不能把这行看成一次独立返回；父ID让块级检索能映射回文档级金标准。

<a id="L18"></a>
### 第 18 行

```python
                       "source": doc.source, "start": start, "end": end, "text": doc.text[start:end]})
```

**语法与数据变化：** 补充 source、start、end 和正文切片，闭合字典及 append 调用。

**为什么与边界：** 区间为 [start,end)，基于 doc.text 而非原文件字节或 PDF 页码；相同来源名并不保证相同父ID。

<a id="L19"></a>
### 第 19 行

```python
        if end == len(doc.text):
```

**语法与数据变化：** 检查当前块右端是否已到正文末尾。

**为什么与边界：** 到末尾即可停止，即使 range 还可能产生下一起点，也不应再生成纯重复尾部小块。

<a id="L20"></a>
### 第 20 行

```python
            break
```

**语法与数据变化：** break 退出最近一层 for 循环。

**为什么与边界：** 不是丢掉刚 append 的末块，末块已经在 result 里；也不是 return，接下来执行统一返回。

<a id="L21"></a>
### 第 21 行

```python
    return result
```

**语法与数据变化：** 返回全部块字典。

**为什么与边界：** 只是内存对象，没有自动写入向量库、数据库或文件；也没证明分块改善了 q06/q09。

<a id="L22"></a>
### 第 22 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L23"></a>
### 第 23 行

```python
#: 先剔除该父文档旧块，再合入新块；返回新字典，校验失败也不破坏旧索引。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：先剔除该父文档旧块，再合入新块；返回新字典，校验失败也不破坏旧索引。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L24"></a>
### 第 24 行

```python
def replace_document(index: dict[str, dict], doc: Document, size: int = 120) -> dict[str, dict]:
```

**语法与数据变化：** 定义按父文档替换的函数，index 用块ID映射到块字典；size 默认120。

**为什么与边界：** 这里没有公开 overlap 参数，下面 chunks(doc,size) 会使用默认 overlap=20；小 size 必须考虑该默认值。

<a id="L25"></a>
### 第 25 行

```python
    updated = {key: value for key, value in index.items() if value["parent_id"] != doc.id}
```

**语法与数据变化：** 字典推导遍历旧索引，只保留 parent_id 不等于新文档ID的项。

**为什么与边界：** 先在新字典里删掉该父文档的全部旧块；如果文档 ID 本身改了，就不能靠此函数找到原身份的旧块。

<a id="L26"></a>
### 第 26 行

```python
    updated.update({chunk["id"]: chunk for chunk in chunks(doc, size)})
```

**语法与数据变化：** 对新文档分块，以每块 id 为键构造字典，再合入 updated。

**为什么与边界：** 同一输入重跑不会增加重复键；若分块抛错，原 index 顶层未改变，但这不是多进程数据库原子提交。

<a id="L27"></a>
### 第 27 行

```python
    return updated
```

**语法与数据变化：** 返回新的索引字典，调用者需保存或重新赋值。

**为什么与边界：** 不接住返回值就不会替换旧变量；未修改的块对象仍可能共享，不能把浅拷贝理解成深度隔离。

## 跟一遍数据与验证边界

ABCDEFGHIJ 在 size=4、overlap=2 时得到 [0,4)、[2,6)、[4,8)、[6,10)。相同输入重跑 ID 相同；同父文档正文改动后 version 和全部块 ID 改变。别把重叠字符总数当成 token 费用。

## 只练一个关键点（不是新的学习验收记录）

1. 用2A现有小字符串实验，固定size=4，只将overlap从0改为2。
2. 逐块对照start/end切片，并检查同parent_id下的块ID；不要求重写chunks。
3. **复盘：** 哪些字段能定位原文，哪些字段用于版本/块身份？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
