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
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get rider year results (latest year by default)
        year_results = rider.year_results()
        
        # Check if results exist
        if year_results is None or not hasattr(year_results, 'results_df') or year_results.results_df.empty:
            return f"No results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Extract details from the response
        header_details = year_results.header_details
        sidebar_details = year_results.sidebar_details
        
        # Build rider information string
        info = ""
        
        # Add name from header details
        if header_details and 'name' in header_details:
            info += f"Name: {header_details['name']}\n"
        else:
            info += f"Rider ID: {rider_id}\n"
        
        # Add team if available
        if header_details and 'current_team' in header_details:
            info += f"Team: {header_details['current_team']}\n"
        
        # Add Twitter/social media if available
        if header_details and 'twitter_handle' in header_details:
            info += f"Twitter: @{header_details['twitter_handle']}\n"
        
        # Add information from sidebar details
        if sidebar_details:
            if 'Nationality' in sidebar_details:
                info += f"Nationality: {sidebar_details['Nationality']}\n"
            if 'Date of Birth' in sidebar_details:
                info += f"Date of Birth: {sidebar_details['Date of Birth']}\n"
            if 'UCI ID' in sidebar_details:
                info += f"UCI ID: {sidebar_details['UCI ID']}\n"
        
        # Get results for current year
        if hasattr(year_results, 'results_df') and not year_results.results_df.empty:
            info += "\nRecent Results:\n"
            results_count = min(5, len(year_results.results_df))
            for i in range(results_count):
                row = year_results.results_df.iloc[i]
                date = row.get('Date', 'N/A')
                race = row.get('Race', 'N/A')
                pos = row.get('Pos', 'N/A')
                info += f"{i+1}. {date} - {race}: {pos}\n"
        
        # Add victories if available (just a count)
        try:
            victories = rider.victories(uci=True)
            if hasattr(victories, 'results_df') and not victories.results_df.empty:
                info += f"\nUCI Victories: {len(victories.results_df)}\n"
        except:
            pass
        
        return info
    except Exception as e:
        return f"Error retrieving rider information for ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

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
        info = f"Race: {race_id} - {year}\n"
        
        # Try to get race name from results
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