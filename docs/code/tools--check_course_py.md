# 课程链接、源码副本与语法检查器：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tools/check_course.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

让教材中的完整源码与仓库保持一致，并检查本地导航和22课数量；不自动评判教学细度。

### 输入、输出与调用关系

读取README/docs和Python源文件，assert失败退出非零；成功打印检查摘要。

### 运行与风险边界

`python tools/check_course.py`，仅标准库，不运行课程中的模型/数据库实验。

检查不等于掌握或运行正确。源码注释中的Markdown围栏可能含反引号，本轮将解析收紧为行首成对围栏，并支持波浪线围栏。

## 完整源码

<!-- source: tools/check_course.py -->
```python
"""无网络校验：课程本地链接、完整源码同步、Python 语法、课数。"""
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    count = 0
    for doc in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
        text = doc.read_text(encoding="utf-8")
        # Links in fenced source examples are not documentation navigation links.
        without_code = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", "", text, flags=re.S | re.M)
        for link in re.findall(r"\]\(([^)]+)\)", without_code):
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = (doc.parent / link.split("#")[0]).resolve()
            assert target.exists(), f"Broken local link: {doc.relative_to(ROOT)} -> {link}"
        for source, fence, code in re.findall(r"<!-- source: ([^\n]+) -->\n(`{3,}|~{3,})[^\n]*\n(.*?)^\2[ \t]*$", text, re.S | re.M):
            assert (ROOT / source).read_text(encoding="utf-8") == code, f"Source drift: {doc.name} / {source}"
            count += 1
    manifest = json.loads((ROOT / "docs/code/manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"] + manifest["supplementary"]:
        raw = (ROOT / entry["source"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], f"Guide source changed: {entry['source']}"
        total = len(raw.decode("utf-8").splitlines())
        assert total == entry["line_count"], entry["source"]
        if entry.get("coverage") == "individual-lines":
            page = (ROOT / entry["page"]).read_text(encoding="utf-8")
            expected = list(range(1, total + 1))
            assert entry["explained_lines"] == expected, entry["source"]
            assert re.findall(r'<a id="L(\d+)"></a>', page) == list(map(str, expected)), entry["page"]
    for path in [*(ROOT / "src").rglob("*.py"), *(ROOT / "examples").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lessons = list((ROOT / "docs/lessons").glob("[0-9][0-9][a-z]-*.md"))
    assert len(lessons) == 22, len(lessons)
    print(f"PASS: 22 lessons; {count} embedded source copies match; local links and Python syntax valid")

if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""无网络校验：课程本地链接、完整源码同步、Python 语法、课数。"""
```

**语法与数据变化：** 模块docstring声明此工具无网络及检查范围。

**为什么与边界：** Python语法检查不是执行测试，链接存在也不是内容正确。

<a id="L2"></a>
### 第 2 行

```python
import ast
```

**语法与数据变化：** 导入 `ast` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 Python 语法树工具。parse 检查语法并构造树，不执行业务代码；语法合法不代表运行成功或结果正确。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import hashlib
```

**语法与数据变化：** 导入 `hashlib` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库摘要算法。sha256 接收字节，hexdigest 返回十六进制文本；哈希可作内容指纹，不是加密、权限校验或真实性认证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
import re
```

**语法与数据变化：** 导入 `re` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库正则表达式。模式识别文本形状，不等于完整解析任意 Markdown、SQL 或自然语言。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 以工具文件位置定位仓库根目录。

**为什么与边界：** 可从其他cwd启动，不靠当前目录猜README位置。

<a id="L9"></a>
### 第 9 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L10"></a>
### 第 10 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L11"></a>
### 第 11 行

```python
    count = 0
```

**语法与数据变化：** 初始化完整源码副本计数。

**为什么与边界：** 同一源文件在多篇教材出现会被多次计数，不等于独立文件数。

<a id="L12"></a>
### 第 12 行

```python
    for doc in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
```

**语法与数据变化：** 遍历根README与docs下递归排序的所有Markdown。

**为什么与边界：** 不是扫描全仓库任意后缀，用户未提交笔记不在此导航检查范围。

<a id="L13"></a>
### 第 13 行

```python
        text = doc.read_text(encoding="utf-8")
```

**语法与数据变化：** 按UTF-8读当前文档。

**为什么与边界：** 读失败应报错，不默默跳过。

<a id="L14"></a>
### 第 14 行

```python
        # Links in fenced source examples are not documentation navigation links.
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Links in fenced source examples are not documentation navigation links. 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L15"></a>
### 第 15 行

```python
        without_code = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", "", text, flags=re.S | re.M)
```

**语法与数据变化：** 正则去掉行首开头、同符号同长度闭合的反引号/波浪线围栏，S使点跨行、M使^/$按行。

**为什么与边界：** 反向引用\1匹配原围栏，避免把源码字符串里的三个反引号误当结束；仍是受控Markdown约定，不是完整CommonMark解析器。

<a id="L16"></a>
### 第 16 行

```python
        for link in re.findall(r"\]\(([^)]+)\)", without_code):
```

**语法与数据变化：** 从非代码正文提取Markdown目标链接。

**为什么与边界：** 不解析所有HTML链接或复杂嵌套括号，适用于当前课程约定。

<a id="L17"></a>
### 第 17 行

```python
            if link.startswith(("https://", "http://", "#", "mailto:")):
```

**语法与数据变化：** 外部HTTP、页内锚点与邮件链接不做本地文件检查。

**为什么与边界：** 跳过不证明远端可达或页内锚点确实存在。

<a id="L18"></a>
### 第 18 行

```python
                continue
```

**语法与数据变化：** 命中外部类型就处理下一条链接。

**为什么与边界：** continue只结束本次链接循环，不退出整份文档检查。

<a id="L19"></a>
### 第 19 行

```python
            target = (doc.parent / link.split("#")[0]).resolve()
```

**语法与数据变化：** 去掉#片段，把相对路径相对于文档目录解析为绝对路径。

**为什么与边界：** 检查文件存在，不检查片段目标；本轮行锚点另用清单核对。

<a id="L20"></a>
### 第 20 行

```python
            assert target.exists(), f"Broken local link: {doc.relative_to(ROOT)} -> {link}"
```

**语法与数据变化：** 目标不存在则assert报告文档与坏链接。

**为什么与边界：** 用python -O会禁用assert，校验命令不要开启优化模式。

<a id="L21"></a>
### 第 21 行

```python
        for source, fence, code in re.findall(r"<!-- source: ([^\n]+) -->\n(`{3,}|~{3,})[^\n]*\n(.*?)^\2[ \t]*$", text, re.S | re.M):
```

**语法与数据变化：** 提取source标记、围栏及其完整内容，用\2找到相同的行首闭合围栏。

**为什么与边界：** 允许源码文本本身含```；捕获fence供匹配而非业务使用，code保留源文件换行。

<a id="L22"></a>
### 第 22 行

```python
            assert (ROOT / source).read_text(encoding="utf-8") == code, f"Source drift: {doc.name} / {source}"
```

**语法与数据变化：** 读取标记路径的实际源码，要求文本逐字相同。

**为什么与边界：** 空白、注释和末尾换行漂移也会失败；并不验证逐行解释是否语义正确。

<a id="L23"></a>
### 第 23 行

```python
            count += 1
```

**语法与数据变化：** 每匹配一个完整副本加1。

**为什么与边界：** 逐行小片段没有source标记，不计作另一份完整源码。

<a id="L24"></a>
### 第 24 行

```python
    manifest = json.loads((ROOT / "docs/code/manifest.json").read_text(encoding="utf-8"))
```

**语法与数据变化：** 读取精讲清单JSON，取得文件路径、摘要、行数及覆盖类型。

**为什么与边界：** 清单是机械对照基准，不是教学内容质量评分；缺失应让检查失败。

<a id="L25"></a>
### 第 25 行

```python
    for entry in manifest["files"] + manifest["supplementary"]:
```

**语法与数据变化：** 同时遍历主线逐行文件和补充维护配置。

**为什么与边界：** 两种覆盖类型分开，不能把锁文件算成逐行业务精讲。

<a id="L26"></a>
### 第 26 行

```python
        raw = (ROOT / entry["source"]).read_bytes()
```

**语法与数据变化：** 读取真实源文件原始字节。

**为什么与边界：** 摘要基于实际字节，不先标准化换行，以发现源文件变更。

<a id="L27"></a>
### 第 27 行

```python
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], f"Guide source changed: {entry['source']}"
```

**语法与数据变化：** 计算SHA256并与清单比对，失败说明原文已有变化。

**为什么与边界：** 这防止更新源码却忘记复核讲解；不是来源认证或隐私保护。

<a id="L28"></a>
### 第 28 行

```python
        total = len(raw.decode("utf-8").splitlines())
```

**语法与数据变化：** UTF-8解码并按splitlines统计物理行。

**为什么与边界：** 空行/注释也算在内，单行文件中的多个配置字段仍是一物理行。

<a id="L29"></a>
### 第 29 行

```python
        assert total == entry["line_count"], entry["source"]
```

**语法与数据变化：** 源文件行数必须匹配记录。

**为什么与边界：** hash相同之外再检查清单自身行数元数据是否正确。

<a id="L30"></a>
### 第 30 行

```python
        if entry.get("coverage") == "individual-lines":
```

**语法与数据变化：** 仅individual-lines类型继续逐行覆盖检查。

**为什么与边界：** supplementary按用途/维护解释，不假装每个第三方锁记录都做业务精讲。

<a id="L31"></a>
### 第 31 行

```python
            page = (ROOT / entry["page"]).read_text(encoding="utf-8")
```

**语法与数据变化：** 读取对应Markdown精讲页。

**为什么与边界：** 不存在会失败，不能只有清单条目而没有实际材料。

<a id="L32"></a>
### 第 32 行

```python
            expected = list(range(1, total + 1))
```

**语法与数据变化：** 从1到total构造完整预期行号序列。

**为什么与边界：** range右界不含，因此用total+1包含最后一行。

<a id="L33"></a>
### 第 33 行

```python
            assert entry["explained_lines"] == expected, entry["source"]
```

**语法与数据变化：** 要求清单列出每一个物理行且顺序完整。

**为什么与边界：** 这发现编号漏项/重复，但不证明解释准确。

<a id="L34"></a>
### 第 34 行

```python
            assert re.findall(r'<a id="L(\d+)"></a>', page) == list(map(str, expected)), entry["page"]
```

**语法与数据变化：** 从页面提取显式L数字锚点，与预期字符串列表完全比较。

**为什么与边界：** 既查遗漏也查重复/错序；语法解释是否充分仍需人工看正文。

<a id="L35"></a>
### 第 35 行

```python
    for path in [*(ROOT / "src").rglob("*.py"), *(ROOT / "examples").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
```

**语法与数据变化：** 枚举src递归及examples/tests当前层的Python文件。

**为什么与边界：** 此循环不含tools；工具语法本轮还要另外parse，不能夸大为全部Python已由此循环覆盖。

<a id="L36"></a>
### 第 36 行

```python
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
```

**语法与数据变化：** ast.parse做语法解析，filename使异常定位到文件。

**为什么与边界：** 不会导入依赖或执行main，因此不触发在线实验。

<a id="L37"></a>
### 第 37 行

```python
    lessons = list((ROOT / "docs/lessons").glob("[0-9][0-9][a-z]-*.md"))
```

**语法与数据变化：** 按两位数字+小写字母命名规则找课程文件。

**为什么与边界：** 只统计符合规范的22课，不把源码精讲页当新课程阶段。

<a id="L38"></a>
### 第 38 行

```python
    assert len(lessons) == 22, len(lessons)
```

**语法与数据变化：** 要求恰好22，失败时显示实际数量。

**为什么与边界：** 课程数正确不说明每课已学或已验收。

<a id="L39"></a>
### 第 39 行

```python
    print(f"PASS: 22 lessons; {count} embedded source copies match; local links and Python syntax valid")
```

**语法与数据变化：** 输出本次实际副本数和检查范围。

**为什么与边界：** PASS只能用于所列机械检查，不是教学质量认证。

<a id="L40"></a>
### 第 40 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L41"></a>
### 第 41 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L42"></a>
### 第 42 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

改完整源码副本一个字符应报Source drift；改正文解释未必被检查器发现，所以讲解仍需人工校对。

## 只练一个关键点（不是新的学习验收记录）

1. 运行检查器，查看副本数量；再读manifest中本文件条目。
2. 在临时副本做坏链接/源码字符/行锚点三种变异并确认检查失败，恢复后重跑；不改学习档案。
3. **复盘：** 行号齐全为什么仍不能自动证明解释充分？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
