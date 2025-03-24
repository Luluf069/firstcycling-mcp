import os
import sys
from mcp.server.fastmcp import FastMCP

# Add the FirstCyclingAPI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "FirstCyclingAPI"))

# Import from the FirstCycling API
from first_cycling_api.rider.rider import Rider

# Create a new server
mcp = FastMCP("FirstCycling")

@mcp.tool()
async def get_rider_info(rider_id: int) -> str:
    """
    Get information about a cyclist by their FirstCycling ID.
    
    Args:
        rider_id: The FirstCycling ID of the rider
    
    Returns:
        Information about the rider's recent results
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
            
        # Get rider year results (latest year by default)
        year_results = rider.year_results()
        
        if year_results is None or not hasattr(year_results, 'results_df') or year_results.results_df.empty:
            return f"No results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Format the results
        results_text = "Recent results:\n\n"
        
        # Convert to string and format
        results_df = year_results.results_df.head(10)  # Limit to 10 most recent results
        for _, row in results_df.iterrows():
            date = row.get('Date', 'Unknown date')
            position = row.get('Pos', 'Unknown position')
            race = row.get('Race', 'Unknown race')
            category = row.get('CAT', 'Unknown category')
            
            results_text += f"Date: {date}\n"
            results_text += f"Position: {position}\n"
            results_text += f"Race: {race}\n"
            results_text += f"Category: {category}\n"
            results_text += "-----------------------\n"
        
        return results_text
    except Exception as e:
        return f"Error retrieving rider information for ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

if __name__ == "__main__":
    mcp.run() 