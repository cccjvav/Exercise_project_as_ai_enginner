# 旧教材源码副本的有限同步器：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tools/sync_course_sources.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

只更新指定形状的旧课程源码块与注释概括表，不重写答题档案和解释正文。

### 输入、输出与调用关系

读取docs/lessons下Markdown，匹配旧模板后写回改变的文件。

### 运行与风险边界

维护者先看git diff并备份；确需同步时 `python tools/sync_course_sources.py`，随后检查课程与diff。

会写教材；不会更新docs/code逐行解释或行号清单。源码改动后不能只跑此工具就宣称新精讲仍准确。

## 完整源码

<!-- source: tools/sync_course_sources.py -->
~~~python
"""Refresh source copies and nearby-comment line tables without rewriting lesson prose."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(
    r"(<!-- source: ([^\n]+) -->\n```[^\n]*\n)(.*?)(```\n\n#### 逐行 / 相邻语句讲解\n\n)(\|[^\n]*\n(?:\|[^\n]*\n)*)",
    re.S,
)


def replace(match):
    source = (ROOT / match[2]).read_text(encoding="utf-8")
    lines = source.splitlines()
    markers = []
    for number, line in enumerate(lines, 1):
        comment = re.match(r"\s*(?:#|//|--):\s*(.*)", line)
        if comment:
            markers.append((number, comment[1]))
    table = "| 源码行 | 为什么这样写、数据如何变化 |\n|---|---|\n"
    for index, (start, text) in enumerate(markers):
        end = markers[index + 1][0] - 1 if index + 1 < len(markers) else len(lines)
        table += f"| {start}–{end} | {text.replace('|', '／')} |\n"
    if not markers:
        table += "| 全文件 | 配置字段按小课原理和操作步骤解释；修改后以构建和测试验证。 |\n"
    return match[1] + source + match[4] + table


def main():
    changed = 0
    for path in (ROOT / "docs/lessons").glob("*.md"):
        old = path.read_text(encoding="utf-8")
        new = PATTERN.sub(replace, old)
        if old != new:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} lesson source copies / line tables")


if __name__ == "__main__":
    main()
~~~

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

~~~python
"""Refresh source copies and nearby-comment line tables without rewriting lesson prose."""
~~~

**语法与数据变化：** docstring限制工具职责为源码副本和附近注释表。

**为什么与边界：** 不把简短注释自动扩写成1A精讲，也不应覆盖学员档案。

<a id="L2"></a>
### 第 2 行

~~~python
from pathlib import Path
~~~

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

~~~python
import re
~~~

**语法与数据变化：** 导入 `re` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库正则表达式。模式识别文本形状，不等于完整解析任意 Markdown、SQL 或自然语言。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L5"></a>
### 第 5 行

~~~python
ROOT = Path(__file__).resolve().parents[1]
~~~

**语法与数据变化：** 定位仓库根目录。

**为什么与边界：** 输出位置由受控目录决定，不接收任意用户路径。

<a id="L6"></a>
### 第 6 行

~~~python
PATTERN = re.compile(
~~~

**语法与数据变化：** 编译复用的多行正则。

**为什么与边界：** 这是一种模板替换器，不是完整Markdown语法树编辑器。

<a id="L7"></a>
### 第 7 行

~~~python
    r"(<!-- source: ([^\n]+) -->\n```[^\n]*\n)(.*?)(```\n\n#### 逐行 / 相邻语句讲解\n\n)(\|[^\n]*\n(?:\|[^\n]*\n)*)",
~~~

**语法与数据变化：** 分组捕获源码标记/路径、旧代码、固定讲解标题和表格。

**为什么与边界：** 严格依赖旧模板与三反引号，不能随意改组号后仍沿用match索引。

<a id="L8"></a>
### 第 8 行

~~~python
    re.S,
~~~

**语法与数据变化：** re.S让点号跨行，才能捕获整段源码。

**为什么与边界：** 非贪婪匹配仍不适合任意嵌套围栏，因此限制用途。

<a id="L9"></a>
### 第 9 行

~~~python
)
~~~

**语法与数据变化：** 闭合正则构造。

**为什么与边界：** 此时没有读取或修改文档。

<a id="L10"></a>
### 第 10 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L11"></a>
### 第 11 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L12"></a>
### 第 12 行

~~~python
def replace(match):
~~~

**语法与数据变化：** 定义sub替换回调，接收一个匹配对象。

**为什么与边界：** 不是字符串replace同名方法；随后PATTERN.sub会逐次调用。

<a id="L13"></a>
### 第 13 行

~~~python
    source = (ROOT / match[2]).read_text(encoding="utf-8")
~~~

**语法与数据变化：** 用第2捕获组找到源文件并按UTF-8读取。

**为什么与边界：** 缺文件就报错，不保留过时副本假装成功。

<a id="L14"></a>
### 第 14 行

~~~python
    lines = source.splitlines()
~~~

**语法与数据变化：** 拆行便于编号。

**为什么与边界：** splitlines去换行，只用于表格行范围，实际替换代码仍用完整source。

<a id="L15"></a>
### 第 15 行

~~~python
    markers = []
~~~

**语法与数据变化：** 初始化注释标记列表。

**为什么与边界：** 只认特定#:、//:、--:说明，不自动分析所有语句。

<a id="L16"></a>
### 第 16 行

~~~python
    for number, line in enumerate(lines, 1):
~~~

**语法与数据变化：** 从1编号遍历每行。

**为什么与边界：** 与编辑器行号一致，便于旧表定位。

<a id="L17"></a>
### 第 17 行

~~~python
        comment = re.match(r"\s*(?:#|//|--):\s*(.*)", line)
~~~

**语法与数据变化：** 正则匹配三种语言的特殊注释前缀并捕获正文。

**为什么与边界：** 普通注释不一定进入表，不能把此表当完整逐行解释。

<a id="L18"></a>
### 第 18 行

~~~python
        if comment:
~~~

**语法与数据变化：** 只有匹配到指定注释才处理。

**为什么与边界：** 没有注释的执行逻辑不会被自动理解。

<a id="L19"></a>
### 第 19 行

~~~python
            markers.append((number, comment[1]))
~~~

**语法与数据变化：** 保存行号与注释正文。

**为什么与边界：** 后面以相邻标记界定语句组范围。

<a id="L20"></a>
### 第 20 行

~~~python
    table = "| 源码行 | 为什么这样写、数据如何变化 |\n|---|---|\n"
~~~

**语法与数据变化：** 建立Markdown表头。

**为什么与边界：** 这张表是旧式分组概括，不是新增docs/code每行讲解。

<a id="L21"></a>
### 第 21 行

~~~python
    for index, (start, text) in enumerate(markers):
~~~

**语法与数据变化：** 枚举注释段起点及正文。

**为什么与边界：** index用于找到下一段起始行。

<a id="L22"></a>
### 第 22 行

~~~python
        end = markers[index + 1][0] - 1 if index + 1 < len(markers) else len(lines)
~~~

**语法与数据变化：** 段尾为下一注释前一行，末段到文件最后。

**为什么与边界：** 可能把多条业务语句合并，正是本轮需要另写精讲的原因。

<a id="L23"></a>
### 第 23 行

~~~python
        table += f"| {start}–{end} | {text.replace('|', '／')} |\n"
~~~

**语法与数据变化：** 写范围行并将正文中的竖线改全角避免破坏表格。

**为什么与边界：** 仅解决表格分隔，不是通用Markdown转义器。

<a id="L24"></a>
### 第 24 行

~~~python
    if not markers:
~~~

**语法与数据变化：** 没有任何特殊注释时使用兜底表。

**为什么与边界：** 兜底文字不代表配置每行已经充分讲解。

<a id="L25"></a>
### 第 25 行

~~~python
        table += "| 全文件 | 配置字段按小课原理和操作步骤解释；修改后以构建和测试验证。 |\n"
~~~

**语法与数据变化：** 加入全文件概括提示。

**为什么与边界：** 教学覆盖清单不能据此把文件标为逐行完成。

<a id="L26"></a>
### 第 26 行

~~~python
    return match[1] + source + match[4] + table
~~~

**语法与数据变化：** 拼接旧开头、真实源码、固定标题与新表替换匹配段。

**为什么与边界：** 未匹配到的正文/学习档案保留，但仍应检查diff防模板误匹配。

<a id="L27"></a>
### 第 27 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L28"></a>
### 第 28 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L29"></a>
### 第 29 行

~~~python
def main():
~~~

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L30"></a>
### 第 30 行

~~~python
    changed = 0
~~~

**语法与数据变化：** 初始化改变的文档数。

**为什么与边界：** 计的是文件而不是替换块数。

<a id="L31"></a>
### 第 31 行

~~~python
    for path in (ROOT / "docs/lessons").glob("*.md"):
~~~

**语法与数据变化：** 只扫描docs/lessons本层Markdown。

**为什么与边界：** 不处理新docs/code，也不遍历用户笔记。

<a id="L32"></a>
### 第 32 行

~~~python
        old = path.read_text(encoding="utf-8")
~~~

**语法与数据变化：** 读取旧内容作为对照。

**为什么与边界：** 没有写入前可完整比较文本。

<a id="L33"></a>
### 第 33 行

~~~python
        new = PATTERN.sub(replace, old)
~~~

**语法与数据变化：** 执行所有模板替换，得到new字符串。

**为什么与边界：** 此时还是内存结果。

<a id="L34"></a>
### 第 34 行

~~~python
        if old != new:
~~~

**语法与数据变化：** 仅在文本不同才写盘。

**为什么与边界：** 重复运行无变化时应为0，减少无意义文件修改。

<a id="L35"></a>
### 第 35 行

~~~python
            path.write_text(new, encoding="utf-8")
~~~

**语法与数据变化：** 以UTF-8覆盖该课程文件。

**为什么与边界：** 这是实际副作用，运行前后必须审查git diff。

<a id="L36"></a>
### 第 36 行

~~~python
            changed += 1
~~~

**语法与数据变化：** 改变文件数加1。

**为什么与边界：** 一个文件含多个块也只计一次。

<a id="L37"></a>
### 第 37 行

~~~python
    print(f"Updated {changed} lesson source copies / line tables")
~~~

**语法与数据变化：** 打印真实改变数量。

**为什么与边界：** 0不能证明精讲已同步，只代表本工具模板未产生差异。

<a id="L38"></a>
### 第 38 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L39"></a>
### 第 39 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L40"></a>
### 第 40 行

~~~python
if __name__ == "__main__":
~~~

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L41"></a>
### 第 41 行

~~~python
    main()
~~~

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

只有source标记+三反引号源码+指定四级标题+表格的连续结构才匹配；新逐行页不符合此模板，也不在扫描目录。

## 只练一个关键点（不是新的学习验收记录）

1. 先看PATTERN与只扫描docs/lessons的路径，不立即运行写操作。
2. 确需同步时先git diff，运行后只审阅源码/旧表变化；docs/code逐行解释必须人工复核。
3. **复盘：** 同步旧注释表为什么不能替代更新逐行教材？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
