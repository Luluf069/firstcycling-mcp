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
        
        # Get year results for most recent year (default behavior when no year is specified)
        year_results = rider.year_results()
        
        # Get header and sidebar details
        header_details = year_results.header_details
        sidebar_details = year_results.sidebar_details
        
        # Format basic rider information
        info = f"Name: {rider_id}\n"  # We'll replace this with actual name if available
        
        # Add current team if available
        if header_details.get('current_team'):
            info = f"Name: {header_details.get('current_team').split('(')[0].strip()}\n"
            info += f"Team: {header_details.get('current_team')}\n"
        
        # Add Twitter handle if available
        if header_details.get('twitter_handle'):
            info += f"Twitter: @{header_details.get('twitter_handle')}\n"
        
        # Add year details if available
        if hasattr(year_results, 'year_details'):
            year_details = year_results.year_details
            if year_details.get('Team'):
                info += f"Current Team: {year_details.get('Team')}\n"
            if year_details.get('Division'):
                info += f"Division: {year_details.get('Division')}\n"
            if year_details.get('UCI Ranking'):
                info += f"UCI Ranking: {year_details.get('UCI Ranking')}\n"
            if year_details.get('UCI Points'):
                info += f"UCI Points: {year_details.get('UCI Points')}\n"
            if year_details.get('UCI Wins'):
                info += f"Wins: {year_details.get('UCI Wins')}\n"
        
        # Add recent results if available
        if hasattr(year_results, 'results_df') and not year_results.results_df.empty:
            info += "\nRecent Results:\n"
            for i, (_, row) in enumerate(year_results.results_df.iterrows(), 1):
                if i > 5:  # Show only the first 5 results
                    break
                date = row.get('Date', 'N/A')
                race = row.get('Race', 'N/A')
                pos = row.get('Pos', 'N/A')
                info += f"{i}. {date} - {race}: {pos}\n"
        
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
        race_edition = RaceEdition(race_id, year)
        race_results = race_edition.results()
        
        # Format race information
        info = f"Race: Race ID {race_id} - {year}\n"
        
        # Try to get race name from results table if available
        if hasattr(race_results, 'race_name'):
            info = f"Race: {race_results.race_name} {year}\n"
        
        # Add race details if available
        if hasattr(race_results, 'race_details'):
            race_details = race_results.race_details
            if 'Date' in race_details:
                info += f"Date: {race_details['Date']}\n"
            if 'Category' in race_details:
                info += f"Category: {race_details['Category']}\n"
            if 'Country' in race_details:
                info += f"Country: {race_details['Country']}\n"
                
        info += "\n"
        
        # Add general classification results if available
        if hasattr(race_results, 'results_table') and not race_results.results_table.empty:
            info += "General Classification:\n"
            
            # Get top 10 results
            results_df = race_results.results_table.head(10)
            
            for _, row in results_df.iterrows():
                pos = row.get('Pos', 'N/A')
                rider = row.get('Rider', 'N/A')
                team = row.get('Team', 'N/A')
                time = row.get('Time', '')
                
                info += f"{pos}. {rider} ({team})"
                if time:
                    info += f" - {time}"
                info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving race results: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 