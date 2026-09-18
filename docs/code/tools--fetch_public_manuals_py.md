# 固定版本公开语料下载与来源留存：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tools/fetch_public_manuals.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

从真实公开项目取得小规模授权文本，保留许可证、原字节和内容指纹。

### 输入、输出与调用关系

固定FastAPI清单，经gh API读取，写ignored raw/processed和provenance.json。

### 运行与风险边界

仅需要重建公开语料时 `python -m tools.fetch_public_manuals`；联网，需已配置gh认证。

会覆盖选定同名语料；不执行第三方代码。许可证片段检查只是初筛，不代替阅读许可，hash不证明内容可信。

## 完整源码

<!-- source: tools/fetch_public_manuals.py -->
```python
"""Fetch a pinned small MIT-licensed documentation sample using gh's authenticated API.
Raw and normalized copies remain in ignored data directories. No third-party code is executed.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def github_file(repo: str, revision: str, path: str) -> bytes:
    result = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={revision}"],
                            capture_output=True, text=True, check=True)
    record = json.loads(result.stdout)
    if record.get("encoding") != "base64" or record["size"] > 250_000:
        raise ValueError("Only small regular text files are supported")
    content = base64.b64decode(record["content"], validate=False)
    if len(content) != record["size"]:
        raise ValueError("Downloaded size mismatch")
    return content


def main():
    manifest = json.loads((ROOT / "data/sources/fastapi.json").read_text())
    repo, revision = manifest["repository"], manifest["revision"]
    license_bytes = github_file(repo, revision, manifest["license_path"])
    if b"Permission is hereby granted" not in license_bytes:
        raise ValueError("Expected MIT license; review source before use")
    downloaded = [(doc, github_file(repo, revision, doc["path"])) for doc in manifest["documents"]]
    raw_dir = ROOT / "data/raw/fastapi"
    processed = ROOT / "data/processed/fastapi"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    for folder in (raw_dir, processed):
        (folder / "LICENSE.txt").write_bytes(license_bytes)
    provenance = []
    for doc, content in downloaded:
        (raw_dir / f"{doc['id']}.md").write_bytes(content)
        url = f"https://github.com/{repo}/blob/{revision}/{doc['path']}"
        text = f"# {doc['title']}\n\nSource: {url}\nLicense: MIT; see LICENSE.txt.\n\n" + content.decode("utf-8")
        (processed / f"{doc['id']}.md").write_text(text, encoding="utf-8")
        provenance.append({**doc, "url": url, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
    report = {"repository": repo, "revision": revision, "license": manifest["license"],
              "license_sha256": hashlib.sha256(license_bytes).hexdigest(), "documents": provenance}
    (processed / "provenance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"downloaded": len(downloaded), "raw_bytes": sum(len(b) for _, b in downloaded),
                      "directory": "data/processed/fastapi", "revision": revision}, indent=2))


if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""Fetch a pinned small MIT-licensed documentation sample using gh's authenticated API.
```

**语法与数据变化：** 开始多行模块说明，声明固定版本和MIT范围。

**为什么与边界：** 描述实际授权目标，不能泛化为任何网上文本都可随意使用。

<a id="L2"></a>
### 第 2 行

```python
Raw and normalized copies remain in ignored data directories. No third-party code is executed.
```

**语法与数据变化：** 说明落盘在忽略目录、不执行第三方代码。

**为什么与边界：** 下载仍是网络和文件写入，不是无副作用操作。

<a id="L3"></a>
### 第 3 行

```python
"""
```

**语法与数据变化：** 闭合模块说明字符串。

**为什么与边界：** 三引号内容是文档，不执行为命令。

<a id="L4"></a>
### 第 4 行

```python
import base64
```

**语法与数据变化：** 导入 `base64` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 字节与 Base64 文本互转，不是加密；编码后的敏感内容仍然敏感。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
import hashlib
```

**语法与数据变化：** 导入 `hashlib` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库摘要算法。sha256 接收字节，hexdigest 返回十六进制文本；哈希可作内容指纹，不是加密、权限校验或真实性认证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
import subprocess
```

**语法与数据变化：** 导入 `subprocess` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库子进程接口。run 可等待外部命令并取得退出码、stdout、stderr；传参数列表与 shell 拼接不同，仍需控制实际调用的程序。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L10"></a>
### 第 10 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 从工具文件定位仓库。

**为什么与边界：** 输出目录固定，不接受用户任意写路径。

<a id="L11"></a>
### 第 11 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
def github_file(repo: str, revision: str, path: str) -> bytes:
```

**语法与数据变化：** 定义取单文件接口，返回bytes而非已解码文本。

**为什么与边界：** 先保留原始字节，便于大小和摘要核对。

<a id="L14"></a>
### 第 14 行

```python
    result = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={revision}"],
```

**语法与数据变化：** 用参数列表调用gh api，仓库/路径/ref组成内容端点。

**为什么与边界：** 复用已配置认证，不在代码或聊天里要求Key；ref固定才能追溯。

<a id="L15"></a>
### 第 15 行

```python
                            capture_output=True, text=True, check=True)
```

**语法与数据变化：** 捕获文本输出并check=True，非零会抛子进程异常。

**为什么与边界：** 认证/网络失败不等同“没有文档”，不要吞掉后继续生成报告。

<a id="L16"></a>
### 第 16 行

```python
    record = json.loads(result.stdout)
```

**语法与数据变化：** 解码GitHub JSON响应。

**为什么与边界：** 接口响应JSON与文件内容是不同层。

<a id="L17"></a>
### 第 17 行

```python
    if record.get("encoding") != "base64" or record["size"] > 250_000:
```

**语法与数据变化：** 要求base64编码且声明大小不超过250000字节。

**为什么与边界：** 限制小文件；不是下载总费用硬上限，也未验证完整响应schema。

<a id="L18"></a>
### 第 18 行

```python
        raise ValueError("Only small regular text files are supported")
```

**语法与数据变化：** 不符合就抛ValueError。

**为什么与边界：** 不尝试把目录/大文件当文本强行解析。

<a id="L19"></a>
### 第 19 行

```python
    content = base64.b64decode(record["content"], validate=False)
```

**语法与数据变化：** Base64解码原内容，validate=False容许API里的换行。

**为什么与边界：** Base64不是加密，此处应只下载允许公开使用的文本。

<a id="L20"></a>
### 第 20 行

```python
    if len(content) != record["size"]:
```

**语法与数据变化：** 检查解码后长度与API声明一致。

**为什么与边界：** 能发现截断/异常内容，不能替代来源真实性与许可核对。

<a id="L21"></a>
### 第 21 行

```python
        raise ValueError("Downloaded size mismatch")
```

**语法与数据变化：** 不一致立即失败。

**为什么与边界：** 不把损坏文件当成功输入入库。

<a id="L22"></a>
### 第 22 行

```python
    return content
```

**语法与数据变化：** 返回原始bytes给调用方。

**为什么与边界：** UTF-8解码在生成规范文本时才发生。

<a id="L23"></a>
### 第 23 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L24"></a>
### 第 24 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L25"></a>
### 第 25 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L26"></a>
### 第 26 行

```python
    manifest = json.loads((ROOT / "data/sources/fastapi.json").read_text())
```

**语法与数据变化：** 读取固定来源清单。

**为什么与边界：** 本行未显式encoding，当前JSON是兼容文本；清单需人工审阅，不能当任意不可信路径执行器。

<a id="L27"></a>
### 第 27 行

```python
    repo, revision = manifest["repository"], manifest["revision"]
```

**语法与数据变化：** 同时解包仓库名和revision。

**为什么与边界：** 固定commit而不是不断变化的main，支持复现实验。

<a id="L28"></a>
### 第 28 行

```python
    license_bytes = github_file(repo, revision, manifest["license_path"])
```

**语法与数据变化：** 先下载同revision的许可文件。

**为什么与边界：** 资料入库前先检查许可范围。

<a id="L29"></a>
### 第 29 行

```python
    if b"Permission is hereby granted" not in license_bytes:
```

**语法与数据变化：** 查MIT典型许可片段。

**为什么与边界：** 这是粗筛，不是律师意见，也不能识别所有许可证变种。

<a id="L30"></a>
### 第 30 行

```python
        raise ValueError("Expected MIT license; review source before use")
```

**语法与数据变化：** 不满足就停止，要求人工复核。

**为什么与边界：** 不能先用内容再忽略许可失败。

<a id="L31"></a>
### 第 31 行

```python
    downloaded = [(doc, github_file(repo, revision, doc["path"])) for doc in manifest["documents"]]
```

**语法与数据变化：** 下载清单每份文档并保存(doc元数据,原bytes)对。

**为什么与边界：** 此列表完成后才开始主要落盘，仍不保证所有磁盘写入原子化。

<a id="L32"></a>
### 第 32 行

```python
    raw_dir = ROOT / "data/raw/fastapi"
```

**语法与数据变化：** 指定原始字节保存目录。

**为什么与边界：** 被忽略不代表加密，文件仍可被本机有权限进程读取。

<a id="L33"></a>
### 第 33 行

```python
    processed = ROOT / "data/processed/fastapi"
```

**语法与数据变化：** 指定规范文档目录。

**为什么与边界：** 与raw分开，保留转换前输入。

<a id="L34"></a>
### 第 34 行

```python
    raw_dir.mkdir(parents=True, exist_ok=True)
```

**语法与数据变化：** 递归创建raw目录并允许存在。

**为什么与边界：** 不会自动删除历史多余文件。

<a id="L35"></a>
### 第 35 行

```python
    processed.mkdir(parents=True, exist_ok=True)
```

**语法与数据变化：** 同样准备processed目录。

**为什么与边界：** 重跑会覆盖同名文件，但不是完整增量清理系统。

<a id="L36"></a>
### 第 36 行

```python
    for folder in (raw_dir, processed):
```

**语法与数据变化：** 循环两个目标目录。

**为什么与边界：** 许可需跟随两种副本保留。

<a id="L37"></a>
### 第 37 行

```python
        (folder / "LICENSE.txt").write_bytes(license_bytes)
```

**语法与数据变化：** 以bytes写LICENSE.txt。

**为什么与边界：** 保持许可证原字节，不让编码转换损坏。

<a id="L38"></a>
### 第 38 行

```python
    provenance = []
```

**语法与数据变化：** 建立来源记录列表。

**为什么与边界：** 每条记录对应一份实际下载文档。

<a id="L39"></a>
### 第 39 行

```python
    for doc, content in downloaded:
```

**语法与数据变化：** 逐项取元数据与内容。

**为什么与边界：** ID来自受控清单，若开放不可信清单须补路径安全验证。

<a id="L40"></a>
### 第 40 行

```python
        (raw_dir / f"{doc['id']}.md").write_bytes(content)
```

**语法与数据变化：** 按doc.id写raw Markdown。

**为什么与边界：** 覆盖同名原件，未对任意ID路径穿越做通用防御。

<a id="L41"></a>
### 第 41 行

```python
        url = f"https://github.com/{repo}/blob/{revision}/{doc['path']}"
```

**语法与数据变化：** 构造指向固定commit的浏览器来源URL。

**为什么与边界：** 不是仅存可变主页链接。

<a id="L42"></a>
### 第 42 行

```python
        text = f"# {doc['title']}\n\nSource: {url}\nLicense: MIT; see LICENSE.txt.\n\n" + content.decode("utf-8")
```

**语法与数据变化：** 加课程标题、Source/License提示，再拼UTF-8解码正文。

**为什么与边界：** 不删除原始Markdown标题，可能出现多层标题；也没有执行其中代码。

<a id="L43"></a>
### 第 43 行

```python
        (processed / f"{doc['id']}.md").write_text(text, encoding="utf-8")
```

**语法与数据变化：** 以UTF-8写规范文档。

**为什么与边界：** 其字节已不同于raw，后面的hash明确针对raw。

<a id="L44"></a>
### 第 44 行

```python
        provenance.append({**doc, "url": url, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
```

**语法与数据变化：** 复制元数据，增加URL、raw SHA256和raw字节数。

**为什么与边界：** **doc是字典展开，后面的同名键会覆盖；hash不是隐私保护。

<a id="L45"></a>
### 第 45 行

```python
    report = {"repository": repo, "revision": revision, "license": manifest["license"],
```

**语法与数据变化：** 开始报告，保存仓库、revision、声明许可。

**为什么与边界：** 报告随数据而不是靠口头记忆版本。

<a id="L46"></a>
### 第 46 行

```python
              "license_sha256": hashlib.sha256(license_bytes).hexdigest(), "documents": provenance}
```

**语法与数据变化：** 加入许可摘要与每文档来源列表。

**为什么与边界：** 许可变化也可被指纹识别，仍需要人工解释变化含义。

<a id="L47"></a>
### 第 47 行

```python
    (processed / "provenance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
```

**语法与数据变化：** 将来源报告写到processed/provenance.json。

**为什么与边界：** 文件写入非数据库事务，中途失败时需检查部分产物再重跑。

<a id="L48"></a>
### 第 48 行

```python
    print(json.dumps({"downloaded": len(downloaded), "raw_bytes": sum(len(b) for _, b in downloaded),
```

**语法与数据变化：** 打印文档数与原字节总量，忽略每对中的元数据只取bytes长度。

**为什么与边界：** 此数不是tokens或模型费用。

<a id="L49"></a>
### 第 49 行

```python
                      "directory": "data/processed/fastapi", "revision": revision}, indent=2))
```

**语法与数据变化：** 输出处理目录与固定revision，闭合JSON打印。

**为什么与边界：** 下载完成不等于已经建向量索引或接入API。

<a id="L50"></a>
### 第 50 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L51"></a>
### 第 51 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L52"></a>
### 第 52 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L53"></a>
### 第 53 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

同revision路径应得到可复核原字节。processed额外加标题/来源，因此raw hash不等于processed文件hash；此英语语料与虚构Northstar题集不同。

## 只练一个关键点（不是新的学习验收记录）

1. 先读来源清单的revision、路径、license，圈出两个输出目录。
2. 确需重建语料再运行联网下载；把raw字节hash与provenance记录核对，不执行下载正文中的代码。
3. **复盘：** processed加了标题和来源后为什么不能拿raw hash校验整个新文件？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
