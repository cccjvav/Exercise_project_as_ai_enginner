# MCP客户端的发现与只读调用：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/mcp_client.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用stdio子进程验证协议握手、工具发现和调用，不借助LLM。

### 输入、输出与调用关系

启动mcp_server.py，初始化会话，调用search_public并展示文本内容。

### 运行与风险边界

安装本课MCP依赖与本项目后 `python -m examples.mcp_client`，无需另开常驻端口。

子进程使用本机权限；本例只读虚构目录。协议通不代表多租户授权、工具写操作或生产隔离已完成。

## 完整源码

<!-- source: examples/mcp_client.py -->
```python
#: 客户端负责启动与关闭子进程；无需手工常驻服务或暴露端口。
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

#: 使用当前解释器确保客户端和服务器处于同一虚拟环境。
async def main():
    server = str(Path(__file__).with_name("mcp_server.py"))
    params = StdioServerParameters(command=sys.executable, args=[server])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            #: 初始化→发现工具→执行工具，是协议交互，不要求使用 LLM。
            await session.initialize()
            tools = await session.list_tools()
            assert any(tool.name == "search_public" for tool in tools.tools)
            result = await session.call_tool("search_public", {"query": "Webhook 重试"})
            assert not result.isError
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)

if __name__ == "__main__":
    asyncio.run(main())
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 客户端负责启动与关闭子进程；无需手工常驻服务或暴露端口。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：客户端负责启动与关闭子进程；无需手工常驻服务或暴露端口。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import asyncio
```

**语法与数据变化：** 导入 `asyncio` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库异步事件循环。async/await 管理可等待操作，run 启动顶层协程；异步不意味着自动并行所有工作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import sys
```

**语法与数据变化：** 导入 `sys` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 当前 Python 进程信息；executable 可取得解释器路径，argv 是命令行参数，exit 可设置退出状态。它不是新建虚拟环境的工具。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from mcp import ClientSession, StdioServerParameters
```

**语法与数据变化：** 从 `mcp` 导入 `ClientSession, StdioServerParameters`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** MCP 协议会话及传输组件，用于客户端/服务端交换工具调用；协议连通不等于业务授权完整。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from mcp.client.stdio import stdio_client
```

**语法与数据变化：** 从 `mcp.client.stdio` 导入 `stdio_client`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 通过子进程标准输入输出建立 MCP 传输；协议 stdout 不能混入普通调试日志。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
#: 使用当前解释器确保客户端和服务器处于同一虚拟环境。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：使用当前解释器确保客户端和服务器处于同一虚拟环境。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L9"></a>
### 第 9 行

```python
async def main():
```

**语法与数据变化：** 异步定义主流程，涉及会话握手与读取需await。

**为什么与边界：** 普通调用产生协程，并不会自动完成协议交换。

<a id="L10"></a>
### 第 10 行

```python
    server = str(Path(__file__).with_name("mcp_server.py"))
```

**语法与数据变化：** 以当前文件同目录定位mcp_server.py并转成字符串。

**为什么与边界：** 不依赖终端当前目录猜路径，也不接受用户指定任意可执行脚本。

<a id="L11"></a>
### 第 11 行

```python
    params = StdioServerParameters(command=sys.executable, args=[server])
```

**语法与数据变化：** 使用当前Python解释器及服务端脚本参数构造启动配置。

**为什么与边界：** 避免系统python与虚拟环境依赖不一致；参数列表不是shell命令拼接。

<a id="L12"></a>
### 第 12 行

```python
    async with stdio_client(params) as (read, write):
```

**语法与数据变化：** 异步上下文启动stdio传输，取得read/write流。

**为什么与边界：** 退出负责收尾子进程和连接，不能把它当HTTP公开服务。

<a id="L13"></a>
### 第 13 行

```python
        async with ClientSession(read, write) as session:
```

**语法与数据变化：** 用两个流创建ClientSession，再由上下文管理生命周期。

**为什么与边界：** 传输连接和协议会话是不同层，不能跳过初始化直接假设工具可用。

<a id="L14"></a>
### 第 14 行

```python
            #: 初始化→发现工具→执行工具，是协议交互，不要求使用 LLM。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：初始化→发现工具→执行工具，是协议交互，不要求使用 LLM。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L15"></a>
### 第 15 行

```python
            await session.initialize()
```

**语法与数据变化：** 等待MCP握手初始化完成。

**为什么与边界：** 这是协议要求，不是模型推理请求。

<a id="L16"></a>
### 第 16 行

```python
            tools = await session.list_tools()
```

**语法与数据变化：** 请求工具列表并等待返回。

**为什么与边界：** 发现结果来自真实服务端，不是本地手写名称列表。

<a id="L17"></a>
### 第 17 行

```python
            assert any(tool.name == "search_public" for tool in tools.tools)
```

**语法与数据变化：** 检查至少一个工具名为search_public。

**为什么与边界：** 只验证存在性，不验证所有工具都安全或参数schema完全符合预期。

<a id="L18"></a>
### 第 18 行

```python
            result = await session.call_tool("search_public", {"query": "Webhook 重试"})
```

**语法与数据变化：** 调用指定工具并传查询参数。

**为什么与边界：** 字典键query必须匹配服务端接口；工具自身仍应验证输入。

<a id="L19"></a>
### 第 19 行

```python
            assert not result.isError
```

**语法与数据变化：** 断言服务端没有标记工具执行错误。

**为什么与边界：** 成功状态不保证检索命中或事实充分，还要看内容。

<a id="L20"></a>
### 第 20 行

```python
            for content in result.content:
```

**语法与数据变化：** 遍历返回的内容块。

**为什么与边界：** 协议可能支持文本以外的内容，不应假定每项都有text。

<a id="L21"></a>
### 第 21 行

```python
                if hasattr(content, "text"):
```

**语法与数据变化：** 用hasattr筛有text属性的块。

**为什么与边界：** 这里只展示文本，其他类型被跳过，并非完整多模态客户端。

<a id="L22"></a>
### 第 22 行

```python
                    print(content.text)
```

**语法与数据变化：** 打印文本块，发生在客户端而非服务端协议stdout内。

**为什么与边界：** 客户端终端输出供人看，不会被服务端当成协议帧。

<a id="L23"></a>
### 第 23 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L24"></a>
### 第 24 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L25"></a>
### 第 25 行

```python
    asyncio.run(main())
```

**语法与数据变化：** 用asyncio.run运行整个协程并等待退出。

**为什么与边界：** 在已有事件循环的交互环境需相应调整，不能盲目嵌套。

## 跟一遍数据与验证边界

工具发现列表必须包含search_public，调用结果不能isError；子进程stdout由协议使用，服务端不能混入print调试。

## 只练一个关键点（不是新的学习验收记录）

1. 依赖齐备后运行客户端，让它管理服务端子进程。
2. 观察initialize→list_tools→call_tool顺序；不用另开公网端口或接LLM。
3. **复盘：** 协议成功与业务授权/事实正确之间还差什么？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
