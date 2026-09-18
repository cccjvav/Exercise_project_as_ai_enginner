# 只打包白名单的Space导出器：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tools/export_space.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把本地演示需要的少量文件打包，不上传整个仓库和用户资料。

### 输入、输出与调用关系

白名单文件字节→artifacts/evidencedesk-space.zip，调整Space根Dockerfile和README。

### 运行与风险边界

`python -m tools.export_space`；离线但会覆盖同名ZIP。先用test_space_export检查白名单。

不创建云资源、不登录Hugging Face、不构建Docker。上传和免费硬件/Secrets仍需单独确认。

## 完整源码

<!-- source: tools/export_space.py -->
```python
"""Create a small allowlisted Hugging Face Docker Space bundle, without uploading it."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def space_files() -> dict[str, bytes]:
    selected = [ROOT / path for path in ["pyproject.toml", "requirements-tested.lock.txt",
        "frontend/index.html", "frontend/client.ts", "frontend/package.json", "frontend/package-lock.json", "frontend/tsconfig.json"]]
    selected += sorted((ROOT / "src/evidencedesk").glob("*.py"))
    selected += sorted((ROOT / "data/sample").glob("*.md"))
    files = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in selected}
    docker = (ROOT / "deploy/Dockerfile").read_text().replace("useradd --create-home appuser", "useradd --create-home --uid 1000 appuser")
    files["Dockerfile"] = docker.encode()
    files["README.md"] = (ROOT / "deploy/huggingface/README.md").read_bytes()
    files[".dockerignore"] = (ROOT / ".dockerignore").read_bytes()
    return files


def main():
    target = ROOT / "artifacts/evidencedesk-space.zip"
    target.parent.mkdir(exist_ok=True)
    files = space_files()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            archive.writestr(name, content)
    print(f"Prepared {len(files)} allowlisted files, {target.stat().st_size} bytes. No upload or cloud resource creation.")
    print("artifacts/evidencedesk-space.zip")


if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""Create a small allowlisted Hugging Face Docker Space bundle, without uploading it."""
```

**语法与数据变化：** docstring明确打包而不上传。

**为什么与边界：** 生成ZIP成功不能报告为部署成功。

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
import zipfile
```

**语法与数据变化：** 导入 `zipfile` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 ZIP 读写接口。写 ZIP 是打包本地文件，不等于已上传或在云上构建运行。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L5"></a>
### 第 5 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 定位仓库根目录。

**为什么与边界：** 文件选择与cwd无关。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
def space_files() -> dict[str, bytes]:
```

**语法与数据变化：** 函数返回路径到bytes的字典。

**为什么与边界：** 先在内存建立清单，便于测试而不必真的写ZIP。

<a id="L9"></a>
### 第 9 行

```python
    selected = [ROOT / path for path in ["pyproject.toml", "requirements-tested.lock.txt",
```

**语法与数据变化：** 开始列举项目配置和依赖快照。

**为什么与边界：** 显式白名单优于对整个目录盲目压缩。

<a id="L10"></a>
### 第 10 行

```python
        "frontend/index.html", "frontend/client.ts", "frontend/package.json", "frontend/package-lock.json", "frontend/tsconfig.json"]]
```

**语法与数据变化：** 补上五个前端源/构建配置并将字符串转Path。

**为什么与边界：** 不包含本机node_modules和生成dist。

<a id="L11"></a>
### 第 11 行

```python
    selected += sorted((ROOT / "src/evidencedesk").glob("*.py"))
```

**语法与数据变化：** 追加受控包目录的Python文件。

**为什么与边界：** glob会包含以后新加的模块，新增源码仍需审查是否可公开。

<a id="L12"></a>
### 第 12 行

```python
    selected += sorted((ROOT / "data/sample").glob("*.md"))
```

**语法与数据变化：** 只追加data/sample的Markdown。

**为什么与边界：** 真实下载语料和用户私有文件不自动进入包。

<a id="L13"></a>
### 第 13 行

```python
    files = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in selected}
```

**语法与数据变化：** 以仓库相对统一斜杠路径为键，读原始字节为值。

**为什么与边界：** ZIP内部不应出现本机绝对路径。

<a id="L14"></a>
### 第 14 行

```python
    docker = (ROOT / "deploy/Dockerfile").read_text().replace("useradd --create-home appuser", "useradd --create-home --uid 1000 appuser")
```

**语法与数据变化：** 读Dockerfile并把创建用户语句改为UID1000。

**为什么与边界：** 字面replace依赖原句匹配；上游变化时可能不替换，测试负责捕获该关键字段缺失。

<a id="L15"></a>
### 第 15 行

```python
    files["Dockerfile"] = docker.encode()
```

**语法与数据变化：** 把改后文本编码存为导出根Dockerfile。

**为什么与边界：** 不修改仓库deploy/Dockerfile本体。

<a id="L16"></a>
### 第 16 行

```python
    files["README.md"] = (ROOT / "deploy/huggingface/README.md").read_bytes()
```

**语法与数据变化：** 用Space专用README作为根README，携带平台元数据。

**为什么与边界：** 不是把整份课程README放到部署入口。

<a id="L17"></a>
### 第 17 行

```python
    files[".dockerignore"] = (ROOT / ".dockerignore").read_bytes()
```

**语法与数据变化：** 加入Docker忽略规则。

**为什么与边界：** 仍需白名单自身安全，不能只靠忽略文件防泄漏。

<a id="L18"></a>
### 第 18 行

```python
    return files
```

**语法与数据变化：** 返回文件字典。

**为什么与边界：** 没有上传或写ZIP副作用，读取文件已发生。

<a id="L19"></a>
### 第 19 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L20"></a>
### 第 20 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L21"></a>
### 第 21 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L22"></a>
### 第 22 行

```python
    target = ROOT / "artifacts/evidencedesk-space.zip"
```

**语法与数据变化：** 定义固定产物路径。

**为什么与边界：** artifacts应被Git忽略，不提交重复二进制。

<a id="L23"></a>
### 第 23 行

```python
    target.parent.mkdir(exist_ok=True)
```

**语法与数据变化：** 创建父目录，允许已存在。

**为什么与边界：** 固定一层目录无需递归创建。

<a id="L24"></a>
### 第 24 行

```python
    files = space_files()
```

**语法与数据变化：** 调用白名单收集函数。

**为什么与边界：** 文件缺失会在打包前失败，不能静默缺核心文件。

<a id="L25"></a>
### 第 25 行

```python
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
```

**语法与数据变化：** 以w创建/覆盖ZIP，使用DEFLATED压缩并自动关闭。

**为什么与边界：** 确认已有同名产物可覆盖；不是追加历史版本。

<a id="L26"></a>
### 第 26 行

```python
        for name, content in sorted(files.items()):
```

**语法与数据变化：** 排序遍历路径/内容对，使条目顺序稳定。

**为什么与边界：** ZIP时间戳等仍可能变化，不能承诺二进制完全可复现。

<a id="L27"></a>
### 第 27 行

```python
            archive.writestr(name, content)
```

**语法与数据变化：** 把内存字节写为指定ZIP内路径。

**为什么与边界：** 不通过外部shell命令拼接，白名单决定实际内容。

<a id="L28"></a>
### 第 28 行

```python
    print(f"Prepared {len(files)} allowlisted files, {target.stat().st_size} bytes. No upload or cloud resource creation.")
```

**语法与数据变化：** 打印文件数、实际ZIP字节数，并强调未上传。

**为什么与边界：** stat读取产物大小，不代表云端已接收。

<a id="L29"></a>
### 第 29 行

```python
    print("artifacts/evidencedesk-space.zip")
```

**语法与数据变化：** 额外打印相对路径方便定位。

**为什么与边界：** 人读路径不是部署URL。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L32"></a>
### 第 32 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L33"></a>
### 第 33 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

当前白名单包含应用、前端、虚构语料，不带处理后的外部文档、模型Key、node_modules和Git历史。

## 只练一个关键点（不是新的学习验收记录）

1. 先运行test_space_export，不登录或上传云平台。
2. 需导出时确认ZIP可覆盖再运行，打开条目清单核对只有白名单；不把整个仓库拖去上传。
3. **复盘：** ZIP生成成功与远端构建启动成功差哪些步骤？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
