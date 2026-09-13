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
