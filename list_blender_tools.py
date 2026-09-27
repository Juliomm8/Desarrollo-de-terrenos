import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def run():
    async with sse_client("http://localhost:9876/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"Tool: {t.name}")
                print(f"Desc: {t.description}")
                
asyncio.run(run())
