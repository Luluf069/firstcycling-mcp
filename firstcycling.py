from typing import Any
import sys
import os
from mcp.server.fastmcp import FastMCP

# Add the FirstCyclingAPI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "FirstCyclingAPI"))

# Import from the FirstCycling API
from first_cycling_api.rider.rider import Rider
from first_cycling_api.race.race import RaceEdition

# Initialize FastMCP server
mcp = FastMCP("firstcycling")

@mcp.tool()
async def get_rider_info(rider_id: int) -> str:
    """Get information about a professional cyclist.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
    """
    try:
        # Create a rider instance and fetch data
        rider = Rider(rider_id)
        profile = rider.get_profile()
        results = rider.get_year_results()
        
        # Format rider information
        info = f"Name: {profile.get('name', 'N/A')}\n"
        info += f"Team: {profile.get('team', 'N/A')}\n"
        info += f"Nationality: {profile.get('nationality', 'N/A')}\n"
        
        if profile.get('date_of_birth'):
            info += f"Date of Birth: {profile.get('date_of_birth')}\n"
        
        info += f"UCI ID: {profile.get('uci_id', 'N/A')}\n\n"
        
        # Add recent results if available
        if results:
            info += "Recent Results:\n"
            for i, result in enumerate(results[:5], 1):  # Show only the first 5 results
                info += f"{i}. {result.get('date', 'N/A')} - {result.get('race', 'N/A')}: {result.get('result', 'N/A')}\n"
        
        return info
    except Exception as e:
        return f"Error retrieving rider information: {str(e)}"

@mcp.tool()
async def get_race_results(race_id: int, year: int) -> str:
    """Get results for a specific race in a given year.

    Args:
        race_id: The FirstCycling race ID (e.g., 17 for Tour de France)
        year: The year of the race (e.g., 2023)
    """
    try:
        # Create a race edition instance and fetch results
        race = RaceEdition(race_id, year)
        race_info = race.get_info()
        results = race.get_results()
        
        # Format race information
        info = f"Race: {race_info.get('name', 'N/A')} {year}\n"
        info += f"Date: {race_info.get('date_start', 'N/A')} to {race_info.get('date_end', 'N/A')}\n"
        info += f"Category: {race_info.get('category', 'N/A')}\n"
        info += f"Country: {race_info.get('country', 'N/A')}\n\n"
        
        # Add general classification results if available
        if results:
            info += "General Classification:\n"
            
            # Sort results by position if available
            if results and isinstance(results, list):
                results_to_show = sorted(
                    [r for r in results if r.get('position')], 
                    key=lambda x: int(x.get('position', '999')) if x.get('position', '').isdigit() else 999
                )[:10]  # Show only top 10
                
                for result in results_to_show:
                    info += f"{result.get('position', 'N/A')}. {result.get('rider_name', 'N/A')} ({result.get('team', 'N/A')})"
                    if result.get('time'):
                        info += f" - {result.get('time')}"
                    info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving race results: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 