# Document 与目录加载器：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/documents.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把磁盘上的 Markdown 变成约定明确的 Document；文件格式错误要显式拒绝，不能伪装成没有检索结果。

### 输入、输出与调用关系

输入是目录 Path；输出按文件名排序的 list[Document]。search/评测/API 会复用这个入口。类本身不检查非空，业务检查在加载器。

### 运行与风险边界

仓库根目录运行 `python -m examples.load_manuals`；环境安装见课程 setup，核心读取只用标准库。

只读文件，没有数据库或网络。解码错误、权限问题会抛出异常；函数不保证输入目录内的文件在检查后不会被外部进程替换。

## 完整源码

<!-- source: src/evidencedesk/documents.py -->
```python
#: Path 表达路径，dataclass 为字段生成初始化方法；此时不需要数据库或框架。
from pathlib import Path
from dataclasses import dataclass

#: frozen 防止误改字段；ID 标识文档，source 定位来源，二者用途不同。
@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    source: str

#: 入口先区分不存在与不是目录；这些是输入错误，不应伪装成零命中。
def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(data_dir)
    if not data_dir.is_dir():
        raise NotADirectoryError(data_dir)
    documents = []
    #: 只读第一层 Markdown 文件；排序让结果可复现，跳过名字以 .md 结尾的目录。
    for path in sorted(data_dir.glob("*.md")):
        if not path.is_file():
            continue
        source = path.relative_to(data_dir).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        #: 先判空再访问首行；startswith 真正校验前缀，而 removeprefix 本身不会报错。
        if not lines or not lines[0].startswith("# "):
            raise ValueError(f"{source}: 第一行必须是 # 标题")
        title = lines[0][2:].strip()
        text = "\n".join(lines[1:]).strip()
        if not title or not text:
            raise ValueError(f"{source}: 标题和正文不能为空")
        #: 每个文件变成一个结构化对象；空目录自然返回空列表。
        documents.append(Document(path.stem, title, text, source))
    return documents
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: Path 表达路径，dataclass 为字段生成初始化方法；此时不需要数据库或框架。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Path 表达路径，dataclass 为字段生成初始化方法；此时不需要数据库或框架。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

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
from dataclasses import dataclass
```

**语法与数据变化：** 从 `dataclasses` 导入 `dataclass`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 数据类工具。dataclass 自动生成初始化及比较等方法，asdict 转字典，field 控制字段默认值；普通字段类型注解不自动验证输入。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L5"></a>
### 第 5 行

```python
#: frozen 防止误改字段；ID 标识文档，source 定位来源，二者用途不同。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：frozen 防止误改字段；ID 标识文档，source 定位来源，二者用途不同。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L6"></a>
### 第 6 行

```python
@dataclass(frozen=True)
```

**语法与数据变化：** 装饰器让 dataclass 生成初始化、字段比较等方法；frozen=True 阻止普通字段重新赋值。

**为什么与边界：** 它不是输入验证器，也不保证任意嵌套对象深度不可变；本类四个字段恰好都是字符串。

<a id="L7"></a>
### 第 7 行

```python
class Document:
```

**语法与数据变化：** 定义 Document 类，实例代表一份文档，不是文档列表。

**为什么与边界：** 后续加载器每读一份文件就构造一个对象，列表负责集合，类负责字段结构。

<a id="L8"></a>
### 第 8 行

```python
    id: str
```

**语法与数据变化：** 声明 id 字段为字符串，初始化时必须提供；普通注解不强制运行时类型。

**为什么与边界：** 本加载器用文件名 stem 生成 ID，改名会影响引用与评测金标准，不应随意变动。

<a id="L9"></a>
### 第 9 行

```python
    title: str
```

**语法与数据变化：** title 保存首行提取的可读标题。

**为什么与边界：** 标题与 ID 分开，修改标题不必改变文件身份；非空要求在加载函数而非此声明中。

<a id="L10"></a>
### 第 10 行

```python
    text: str
```

**语法与数据变化：** text 保存正文字符串，不包含首行标题。

**为什么与边界：** 字符偏移和后面的正文版本哈希都基于这个字段，不应把它误作文件原始字节。

<a id="L11"></a>
### 第 11 行

```python
    source: str
```

**语法与数据变化：** source 保存相对于输入目录的来源标识。

**为什么与边界：** 它用于回查来源，不是自动验证过的 URL，也不因字段存在就证明文档内容可信。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
#: 入口先区分不存在与不是目录；这些是输入错误，不应伪装成零命中。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：入口先区分不存在与不是目录；这些是输入错误，不应伪装成零命中。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L14"></a>
### 第 14 行

```python
def load_documents(data_dir: Path) -> list[Document]:
```

**语法与数据变化：** 定义目录到文档列表的转换函数；data_dir 注解为 Path，返回提示为 list[Document]。

**为什么与边界：** 调用者应传 Path 对象；类型提示不会把字符串自动转成 Path，这与 argparse 的 type=Path 转换不同。

<a id="L15"></a>
### 第 15 行

```python
    if not data_dir.exists():
```

**语法与数据变化：** 先调用 exists 检查输入路径是否存在，not 将检查失败变为分支条件。

**为什么与边界：** 不存在与空目录意义不同；空目录可以返回空列表，不存在则通常是配置错误。

<a id="L16"></a>
### 第 16 行

```python
        raise FileNotFoundError(data_dir)
```

**语法与数据变化：** 抛出 FileNotFoundError 并附带路径，立即结束本次函数。

**为什么与边界：** 调用者可以按异常类型处理，不必根据字符串猜测错误；不要 catch 后随意返回 []。

<a id="L17"></a>
### 第 17 行

```python
    if not data_dir.is_dir():
```

**语法与数据变化：** 存在还不够，再检查是否为目录。

**为什么与边界：** 一个普通文件也 exists=True，不能拿它当目录扫描。

<a id="L18"></a>
### 第 18 行

```python
        raise NotADirectoryError(data_dir)
```

**语法与数据变化：** 路径不是目录则抛出 NotADirectoryError。

**为什么与边界：** 这与没有 Markdown 文件不同，错误路径应修复而不是当作检索失败。

<a id="L19"></a>
### 第 19 行

```python
    documents = []
```

**语法与数据变化：** 为本次调用创建独立空列表 documents。

**为什么与边界：** 不要放成共享可变默认参数，否则多次加载可能相互污染；空目录最终原样返回此列表。

<a id="L20"></a>
### 第 20 行

```python
    #: 只读第一层 Markdown 文件；排序让结果可复现，跳过名字以 .md 结尾的目录。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：只读第一层 Markdown 文件；排序让结果可复现，跳过名字以 .md 结尾的目录。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L21"></a>
### 第 21 行

```python
    for path in sorted(data_dir.glob("*.md")):
```

**语法与数据变化：** glob("*.md") 只匹配当前目录一层；sorted 先按路径排序，再逐一绑定 path。

**为什么与边界：** 没有递归扫描子目录，也不会读取 .txt；排序让输入顺序稳定，便于测试复现。

<a id="L22"></a>
### 第 22 行

```python
        if not path.is_file():
```

**语法与数据变化：** 对每个匹配项确认是文件，因为同名后缀也可能属于目录。

**为什么与边界：** 这里并不禁止指向文件的符号链接，不能把它当成完善的目录沙箱。

<a id="L23"></a>
### 第 23 行

```python
            continue
```

**语法与数据变化：** continue 跳过当前匹配项，继续下一次循环。

**为什么与边界：** 不是退出整个加载器，也不会向结果中放一个空 Document。

<a id="L24"></a>
### 第 24 行

```python
        source = path.relative_to(data_dir).as_posix()
```

**语法与数据变化：** relative_to 去掉 data_dir 前缀，as_posix 将分隔符统一为 /。

**为什么与边界：** 避免把本机用户名或绝对路径放入来源；这个相对标识依赖选用的数据根目录。

<a id="L25"></a>
### 第 25 行

```python
        lines = path.read_text(encoding="utf-8").splitlines()
```

**语法与数据变化：** read_text 真正读文件并按 UTF-8 解码；splitlines 转为不带行尾换行的字符串列表。

**为什么与边界：** 空文件得到 []；读取权限、错误编码会报错，不会被这一行吞掉。

<a id="L26"></a>
### 第 26 行

```python
        #: 先判空再访问首行；startswith 真正校验前缀，而 removeprefix 本身不会报错。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：先判空再访问首行；startswith 真正校验前缀，而 removeprefix 本身不会报错。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L27"></a>
### 第 27 行

```python
        if not lines or not lines[0].startswith("# "):
```

**语法与数据变化：** or 左边先判空，非空才访问 lines[0]，再要求精确的 '# ' 前缀。

**为什么与边界：** 短路避免空文件索引越界；`## 标题` 是合法 Markdown，但不满足本加载器的一级标题约定。

<a id="L28"></a>
### 第 28 行

```python
            raise ValueError(f"{source}: 第一行必须是 # 标题")
```

**语法与数据变化：** 格式不符合时抛 ValueError，f-string 把来源文件名放进说明。

**为什么与边界：** 错误信息定位到具体文件；并不继续加载其余文件后返回半成功结果。

<a id="L29"></a>
### 第 29 行

```python
        title = lines[0][2:].strip()
```

**语法与数据变化：** 从首行索引 2 开始切掉 '# '，strip 清理标题两端空白。

**为什么与边界：** '#   ' 通过前缀检查但得到空标题，需要下面的非空检查；不应把它误判为有内容。

<a id="L30"></a>
### 第 30 行

```python
        text = "\n".join(lines[1:]).strip()
```

**语法与数据变化：** 从第二行开始取正文，用换行重新连接并清理整体两端空白。

**为什么与边界：** 保留内部换行，避免把原来独立段落粘成一个词；开头空行被去掉，偏移从清理后的正文算起。

<a id="L31"></a>
### 第 31 行

```python
        if not title or not text:
```

**语法与数据变化：** 字符串为空在布尔上下文为假，任一字段空都会进入分支。

**为什么与边界：** 正文全空白经过 strip 后也为空；非空不等于事实正确，只是最低格式约定。

<a id="L32"></a>
### 第 32 行

```python
            raise ValueError(f"{source}: 标题和正文不能为空")
```

**语法与数据变化：** 拒绝空标题或空正文，说明来源和规则。

**为什么与边界：** Document 的字段声明本身没有做这一步，直接构造对象仍可绕过加载业务校验。

<a id="L33"></a>
### 第 33 行

```python
        #: 每个文件变成一个结构化对象；空目录自然返回空列表。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：每个文件变成一个结构化对象；空目录自然返回空列表。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L34"></a>
### 第 34 行

```python
        documents.append(Document(path.stem, title, text, source))
```

**语法与数据变化：** path.stem 取得不含末尾扩展名的文件名；按字段次序构造 Document 并 append 到列表。

**为什么与边界：** append 加的是单个对象，不是返回新列表；此处不会修改已读文件。

<a id="L35"></a>
### 第 35 行

```python
    return documents
```

**语法与数据变化：** 循环结束后返回本次收集的文档列表。

**为什么与边界：** 若中途抛错不会执行这里；零文件的合法空目录返回 []，让调用者区分空集合与加载异常。

## 跟一遍数据与验证边界

以 `x.md` 内容 `# 指南

正文` 为例：id=x、title=指南、text=正文、source=x.md。把首行改为 `## 指南` 应拒绝；仅保留空白正文也应拒绝。直接构造 Document("x","","","x.md") 不会经过这些业务检查。

## 只练一个关键点（不是新的学习验收记录）

1. 阅读test_loading的tmp_path写法，用临时x.md写一级标题、空行和正文。
2. 运行 tests/test_search.py 的loading与invalid_document用例；不要改真实手册来制造错误。
3. **复盘：** 空目录、缺目录、空正文为什么不能都返回[]？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
