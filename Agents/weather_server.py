# weather_server.py
from fastmcp import FastMCP
import random

mcp = FastMCP("Demo 🚀")

known_weather_data = {
    'berlin': 20.0
}

@mcp.tool
def get_weather(location: str) -> float:
    """Get current weather information for a specified location"""
    city = location.strip().lower()
    if city in known_weather_data:
        return known_weather_data[city]
    return round(random.uniform(-5, 35), 1)

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()  # Use mcp.run() for stdio transport