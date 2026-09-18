# 受限本地PostgreSQL运行器：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tools/local_postgres.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

使用已有本地Linux-x64实验二进制，通过私有Unix socket运行真实数据库，不暴露TCP。

### 输入、输出与调用关系

init创建实验数据目录；version查看版本；serve替换当前进程为PostgreSQL。

### 运行与风险边界

按数据库课先 `npm --prefix tools/postgres-runtime ci --ignore-scripts`，再运行version/init；serve是长驻服务，须用进程管理工具启动。

会执行第三方数据库二进制和建立目录/符号链接；非root本地实验专用，不是生产安全背书。不要把DATA指向重要数据库。

## 完整源码

<!-- source: tools/local_postgres.py -->
```python
"""Local Linux-x64 lab only. No network listener, no cloud account, no passwords."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "tools/postgres-runtime/node_modules/@embedded-postgres/linux-x64"
NATIVE = PACKAGE / "native"
DATA = ROOT / "artifacts/postgres/data"
SOCKET = ROOT / "artifacts/postgres/socket"
PORT = 55432


def runtime():
    if not (NATIVE / "bin/postgres").is_file():
        raise SystemExit("先运行 npm --prefix tools/postgres-runtime ci --ignore-scripts")
    # Hydrate only validated links within this package; do not execute npm lifecycle scripts.
    for item in json.loads((NATIVE / "pg-symlinks.json").read_text()):
        source, target = PACKAGE / item["source"], PACKAGE / item["target"]
        if not source.resolve().is_relative_to(NATIVE.resolve()) or not target.parent.resolve().is_relative_to(NATIVE.resolve()):
            raise ValueError("Unexpected symlink outside package")
        if not target.exists():
            target.symlink_to(os.path.relpath(source, target.parent))
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(NATIVE / "lib")
    return env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "serve", "version"])
    args = parser.parse_args()
    env = runtime()
    if args.action == "version":
        subprocess.run([str(NATIVE / "bin/postgres"), "--version"], env=env, check=True)
        return
    SOCKET.mkdir(parents=True, exist_ok=True, mode=0o700)
    SOCKET.chmod(0o700)
    if args.action == "init":
        if (DATA / "PG_VERSION").exists():
            print("已有实验数据库，保留数据，不重复初始化。")
            return
        subprocess.run([str(NATIVE / "bin/initdb"), "-D", str(DATA), "--auth-local=peer",
                        "--auth-host=reject", "--encoding=UTF8", "--locale=C"], env=env, check=True)
        return
    if not (DATA / "PG_VERSION").exists():
        raise SystemExit("请先运行 init")
    # Database access is via an owner-only Unix socket. There is deliberately no TCP port.
    os.execve(str(NATIVE / "bin/postgres"), [str(NATIVE / "bin/postgres"), "-D", str(DATA),
              "-k", str(SOCKET), "-p", str(PORT), "-c", "listen_addresses=", "-c", "shared_buffers=32MB",
              "-c", "max_connections=10"], env)


if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""Local Linux-x64 lab only. No network listener, no cloud account, no passwords."""
```

**语法与数据变化：** docstring限定Linux-x64、无网络监听和无云账号。

**为什么与边界：** 不意味着任何本机进程都无风险，也不是生产部署方式。

<a id="L2"></a>
### 第 2 行

```python
import argparse
```

**语法与数据变化：** 导入 `argparse` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库命令行解析器。它把终端字符串按参数规则转换，type=int 是实际调用整数转换，而不是类型注解。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

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
import os
```

**语法与数据变化：** 导入 `os` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库操作系统接口，用于环境变量、目录权限或进程环境。环境变量来自进程，不会因为代码中有名字就自动配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
import subprocess
```

**语法与数据变化：** 导入 `subprocess` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库子进程接口。run 可等待外部命令并取得退出码、stdout、stderr；传参数列表与 shell 拼接不同，仍需控制实际调用的程序。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
ROOT = Path(__file__).resolve().parents[1]
```

**语法与数据变化：** 定位仓库根目录。

**为什么与边界：** 运行资源位于明确实验子目录。

<a id="L9"></a>
### 第 9 行

```python
PACKAGE = ROOT / "tools/postgres-runtime/node_modules/@embedded-postgres/linux-x64"
```

**语法与数据变化：** 指定npm平台包目录。

**为什么与边界：** 它在node_modules，由锁文件安装，不纳入项目业务源码。

<a id="L10"></a>
### 第 10 行

```python
NATIVE = PACKAGE / "native"
```

**语法与数据变化：** 取native子目录中的二进制与库。

**为什么与边界：** 平台不同不能直接运行这些Linux-x64程序。

<a id="L11"></a>
### 第 11 行

```python
DATA = ROOT / "artifacts/postgres/data"
```

**语法与数据变化：** 固定实验数据库数据目录。

**为什么与边界：** 包含可持久化数据，不能随意删除或把它当一次性缓存。

<a id="L12"></a>
### 第 12 行

```python
SOCKET = ROOT / "artifacts/postgres/socket"
```

**语法与数据变化：** 固定Unix socket目录。

**为什么与边界：** 后面权限700限制其他系统用户访问。

<a id="L13"></a>
### 第 13 行

```python
PORT = 55432
```

**语法与数据变化：** 设socket端口标识55432。

**为什么与边界：** 数据库仍禁TCP监听，不是预览HTTP服务端口。

<a id="L14"></a>
### 第 14 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L15"></a>
### 第 15 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L16"></a>
### 第 16 行

```python
def runtime():
```

**语法与数据变化：** runtime准备二进制链接及子进程环境。

**为什么与边界：** 函数确实有文件系统副作用，不是纯配置读取。

<a id="L17"></a>
### 第 17 行

```python
    if not (NATIVE / "bin/postgres").is_file():
```

**语法与数据变化：** 检查postgres二进制是否存在。

**为什么与边界：** 存在不保证CPU/动态库兼容或可信。

<a id="L18"></a>
### 第 18 行

```python
        raise SystemExit("先运行 npm --prefix tools/postgres-runtime ci --ignore-scripts")
```

**语法与数据变化：** 缺文件时退出并提示安全安装命令。

**为什么与边界：** 使用ignore-scripts避免盲目执行npm生命周期脚本，仍需审阅包来源。

<a id="L19"></a>
### 第 19 行

```python
    # Hydrate only validated links within this package; do not execute npm lifecycle scripts.
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Hydrate only validated links within this package; do not execute npm lifecycle scripts. 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L20"></a>
### 第 20 行

```python
    for item in json.loads((NATIVE / "pg-symlinks.json").read_text()):
```

**语法与数据变化：** 读取包的符号链接清单并逐项处理。

**为什么与边界：** 清单不直接作为shell脚本执行。

<a id="L21"></a>
### 第 21 行

```python
        source, target = PACKAGE / item["source"], PACKAGE / item["target"]
```

**语法与数据变化：** 将source/target相对于包目录拼接。

**为什么与边界：** Path拼接本身不阻止..越界，所以后面resolve核查必要。

<a id="L22"></a>
### 第 22 行

```python
        if not source.resolve().is_relative_to(NATIVE.resolve()) or not target.parent.resolve().is_relative_to(NATIVE.resolve()):
```

**语法与数据变化：** 要求解析后source和target父目录都在native内。

**为什么与边界：** 阻止明显包外链接，非通用抗竞态沙箱；已安装包仍需信任/审计。

<a id="L23"></a>
### 第 23 行

```python
            raise ValueError("Unexpected symlink outside package")
```

**语法与数据变化：** 越界立即拒绝。

**为什么与边界：** 不能为了启动成功去掉路径检查。

<a id="L24"></a>
### 第 24 行

```python
        if not target.exists():
```

**语法与数据变化：** 目标不存在才创建链接。

**为什么与边界：** 已存在目标不替换；损坏链接等边界可能报错，别把它当万能修复器。

<a id="L25"></a>
### 第 25 行

```python
            target.symlink_to(os.path.relpath(source, target.parent))
```

**语法与数据变化：** 计算相对目标父目录的source路径并建立符号链接。

**为什么与边界：** 不是复制二进制，移动包布局会影响链接有效性。

<a id="L26"></a>
### 第 26 行

```python
    env = os.environ.copy()
```

**语法与数据变化：** 复制当前环境字典。

**为什么与边界：** 避免原地改变整个Python进程环境。

<a id="L27"></a>
### 第 27 行

```python
    env["LD_LIBRARY_PATH"] = str(NATIVE / "lib")
```

**语法与数据变化：** 对子进程设置native/lib动态库搜索目录。

**为什么与边界：** 覆盖这个环境变量可影响加载库选择；捆绑库不自动获得生产安全保证。

<a id="L28"></a>
### 第 28 行

```python
    return env
```

**语法与数据变化：** 返回准备好的环境。

**为什么与边界：** 随后subprocess/exec显式使用它。

<a id="L29"></a>
### 第 29 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L32"></a>
### 第 32 行

```python
    parser = argparse.ArgumentParser()
```

**语法与数据变化：** 创建action解析器。

**为什么与边界：** 不会自行启动数据库。

<a id="L33"></a>
### 第 33 行

```python
    parser.add_argument("action", choices=["init", "serve", "version"])
```

**语法与数据变化：** 只允许init、serve、version三个动作。

**为什么与边界：** 不是任意外部命令执行接口。

<a id="L34"></a>
### 第 34 行

```python
    args = parser.parse_args()
```

**语法与数据变化：** 解析参数得到args.action。

**为什么与边界：** 非法动作在触发runtime前就报用法错误。

<a id="L35"></a>
### 第 35 行

```python
    env = runtime()
```

**语法与数据变化：** 准备运行环境，即使version也会执行链接检查。

**为什么与边界：** 看版本不是绝对无文件写入，需理解调用链。

<a id="L36"></a>
### 第 36 行

```python
    if args.action == "version":
```

**语法与数据变化：** 先处理version分支。

**为什么与边界：** 避免后续创建数据库目录。

<a id="L37"></a>
### 第 37 行

```python
        subprocess.run([str(NATIVE / "bin/postgres"), "--version"], env=env, check=True)
```

**语法与数据变化：** 运行postgres --version，非零抛异常。

**为什么与边界：** 真实二进制版本输出，不是仅看npm包版本号。

<a id="L38"></a>
### 第 38 行

```python
        return
```

**语法与数据变化：** 退出main，不继续init/serve。

**为什么与边界：** 分支必须短路，防止查版本意外启动服务。

<a id="L39"></a>
### 第 39 行

```python
    SOCKET.mkdir(parents=True, exist_ok=True, mode=0o700)
```

**语法与数据变化：** 递归创建socket目录，期望权限700。

**为什么与边界：** mode受umask且已存在目录不会重新设权限，下一行明确chmod。

<a id="L40"></a>
### 第 40 行

```python
    SOCKET.chmod(0o700)
```

**语法与数据变化：** 强制socket目录仅所有者可访问。

**为什么与边界：** 不代替数据库角色/RLS授权，但缩小本机连接范围。

<a id="L41"></a>
### 第 41 行

```python
    if args.action == "init":
```

**语法与数据变化：** 进入初始化分支。

**为什么与边界：** 不会在普通serve时重建数据。

<a id="L42"></a>
### 第 42 行

```python
        if (DATA / "PG_VERSION").exists():
```

**语法与数据变化：** 检查PG_VERSION表示已有集群。

**为什么与边界：** 只是保护性存在检查，不是完整数据健康诊断。

<a id="L43"></a>
### 第 43 行

```python
            print("已有实验数据库，保留数据，不重复初始化。")
```

**语法与数据变化：** 说明保留现有数据库。

**为什么与边界：** 不会清空原记录重置实验。

<a id="L44"></a>
### 第 44 行

```python
            return
```

**语法与数据变化：** 提前返回，防止重复initdb。

**为什么与边界：** 幂等保护依赖固定DATA路径。

<a id="L45"></a>
### 第 45 行

```python
        subprocess.run([str(NATIVE / "bin/initdb"), "-D", str(DATA), "--auth-local=peer",
```

**语法与数据变化：** 调用initdb指定数据目录、本地peer认证。

**为什么与边界：** peer依据系统用户身份，不是无条件trust；需要非root适配的本机用户。

<a id="L46"></a>
### 第 46 行

```python
                        "--auth-host=reject", "--encoding=UTF8", "--locale=C"], env=env, check=True)
```

**语法与数据变化：** 拒绝主机认证、UTF8和C locale，带env/check=True。

**为什么与边界：** initdb失败必须明确报告，不可关安全设置强行放行远程连接。

<a id="L47"></a>
### 第 47 行

```python
        return
```

**语法与数据变化：** 初始化后返回，不自动常驻。

**为什么与边界：** 启动服务是另一个显式动作。

<a id="L48"></a>
### 第 48 行

```python
    if not (DATA / "PG_VERSION").exists():
```

**语法与数据变化：** serve前要求已存在PG_VERSION。

**为什么与边界：** 缺集群就停止，而不是偷偷用别的路径。

<a id="L49"></a>
### 第 49 行

```python
        raise SystemExit("请先运行 init")
```

**语法与数据变化：** 提示先init并非零退出。

**为什么与边界：** 不能把启动失败当数据库无数据。

<a id="L50"></a>
### 第 50 行

```python
    # Database access is via an owner-only Unix socket. There is deliberately no TCP port.
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Database access is via an owner-only Unix socket. There is deliberately no TCP port. 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L51"></a>
### 第 51 行

```python
    os.execve(str(NATIVE / "bin/postgres"), [str(NATIVE / "bin/postgres"), "-D", str(DATA),
```

**语法与数据变化：** execve将当前进程替换为postgres，传二进制、数据目录。

**为什么与边界：** 成功后不再返回Python，长驻任务不能放短超时bash里假装持续运行。

<a id="L52"></a>
### 第 52 行

```python
              "-k", str(SOCKET), "-p", str(PORT), "-c", "listen_addresses=", "-c", "shared_buffers=32MB",
```

**语法与数据变化：** 指定socket、端口标识、空listen_addresses及32MB缓存。

**为什么与边界：** 空监听地址禁TCP；这是私有数据库而非用户浏览器预览端口。

<a id="L53"></a>
### 第 53 行

```python
              "-c", "max_connections=10"], env)
```

**语法与数据变化：** 最多10连接并传环境，闭合exec。

**为什么与边界：** 实验资源限制不是生产容量规划或并发性能验证。

<a id="L54"></a>
### 第 54 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L55"></a>
### 第 55 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L56"></a>
### 第 56 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L57"></a>
### 第 57 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

init看到PG_VERSION会保留现有数据；serve设置listen_addresses为空。55432用于socket名称/连接标识，不表示开放TCP端口。

## 只练一个关键点（不是新的学习验收记录）

1. 仅在准备好的Linux-x64实验环境先运行version，核对真实服务器输出。
2. 需要init/serve时按数据库课显式执行，serve交进程管理；检查无TCP监听，勿换DATA到业务库。
3. **复盘：** socket的55432为何不等于公网开放端口？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
