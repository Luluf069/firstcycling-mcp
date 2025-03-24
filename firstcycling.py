from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("firstcycling")

# Constants
FIRSTCYCLING_BASE_URL = "https://firstcycling.com"
USER_AGENT = "firstcycling-app/1.0"

async def make_fc_request(url: str) -> dict[str, Any] | None:
    """Make a request to the FirstCycling website with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return {"status": "success", "data": response.text}
        except Exception:
            return None

def format_rider_info(data: dict) -> str:
    """Format rider information into a readable string."""
    # This is a placeholder for the real implementation
    # In a real implementation, we would parse the HTML data and extract rider information
    return """
Name: Tadej Pogačar
Team: UAE Team Emirates
Nationality: Slovenia
Age: 26
UCI Ranking: 1
Notable victories: Tour de France (2020, 2021), Giro d'Italia (2024), Liège-Bastogne-Liège (2021, 2023, 2024)
"""

@mcp.tool()
async def get_rider_info(rider_id: int) -> str:
    """Get information about a professional cyclist.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
    """
    url = f"{FIRSTCYCLING_BASE_URL}/rider.php?r={rider_id}"
    data = await make_fc_request(url)

    if not data:
        return "Unable to fetch rider information."

    # This is a placeholder - we'll implement real HTML parsing in the next step
    # For now, just return formatted sample data
    return format_rider_info(data)

@mcp.tool()
async def get_race_results(race_id: int, year: int) -> str:
    """Get results for a specific race in a given year.

    Args:
        race_id: The FirstCycling race ID (e.g., 17 for Tour de France)
        year: The year of the race (e.g., 2023)
    """
    url = f"{FIRSTCYCLING_BASE_URL}/race.php?r={race_id}&y={year}"
    data = await make_fc_request(url)

    if not data:
        return "Unable to fetch race results."

    # This is a placeholder - we'll implement real HTML parsing in the next step
    return f"""
Race: Tour de France {year}
Winner: Jonas Vingegaard (Jumbo-Visma)
Second: Tadej Pogačar (UAE Team Emirates)
Third: Adam Yates (UAE Team Emirates)
Stages: 21
Distance: 3,404 km
"""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 