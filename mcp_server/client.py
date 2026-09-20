import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = str(Path(__file__).parent / "server.py")



def _server_params() -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])


async def _web_search_async(query: str, max_results: int = 5) -> str:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )


    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "web_search", {"query": query, "max_results": max_results}
            )

            return result.content[0].text

async def _call_tool_async(tool_name: str, arguments: dict) -> str:
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text


def _call_tool(tool_name: str, arguments: dict) -> str:
    return asyncio.run(_call_tool_async(tool_name, arguments))


def web_search(query: str, max_results: int = 5) -> str:
    return asyncio.run(_web_search_async(query, max_results))
    #return _call_tool("web_search", {"query": query, "max_results": max_results})

def execute_python(code: str, timeout_seconds: int = 5) -> str:
    return _call_tool("execute_python", {"code": code, "timeout_seconds": timeout_seconds})
 
 
def rag_search(query: str, n_results: int = 3) -> str:
    return _call_tool("rag_search", {"query": query, "n_results": n_results})
