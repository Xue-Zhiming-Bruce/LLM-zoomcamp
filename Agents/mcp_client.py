# mcp_client.py
from fastmcp import Client
import asyncio

# For standalone script execution
async def main():
    async with Client("weather_server.py") as mcp_client:
        # Get the list of available tools
        tools = await mcp_client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- Name: {tool.name}")
            print(f"  Description: {tool.description}")
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(f"  Parameters: {tool.inputSchema}")
            print()
        return tools

if __name__ == "__main__":
    result = asyncio.run(main())