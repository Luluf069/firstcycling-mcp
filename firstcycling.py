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
async def get_rider_best_results(rider_id: int, limit: int = 10) -> str:
    """Get the best results achieved by a professional cyclist throughout their career.

    This tool retrieves the rider's top performances across all races, sorted by position.
    It includes details such as the race name, date, position, and race category.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        limit: Maximum number of results to return (default: 10)
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get best results
        best_results = rider.best_results()
        
        # Check if results exist
        if best_results is None or not hasattr(best_results, 'results_df') or best_results.results_df.empty:
            return f"No best results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(best_results, 'header_details') and best_results.header_details and 'name' in best_results.header_details:
            info += f"Best Results for {best_results.header_details['name']}:\n\n"
        else:
            info += f"Best Results for Rider ID {rider_id}:\n\n"
        
        # Get top results
        results_df = best_results.results_df.head(limit)
        
        for _, row in results_df.iterrows():
            date = row.get('Date', 'N/A')
            race = row.get('Race', 'N/A')
            pos = row.get('Pos', 'N/A')
            category = row.get('CAT', 'N/A')
            country = row.get('Race_Country', 'N/A')
            
            result_line = f"{pos}. {race} ({category})"
            if date != 'N/A':
                result_line += f" - {date}"
            if country != 'N/A':
                result_line += f" - {country}"
            info += result_line + "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving best results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_grand_tour_results(rider_id: int) -> str:
    """Get the results of a professional cyclist in Grand Tours (Tour de France, Giro d'Italia, Vuelta a España).

    This tool retrieves the rider's performances in all three Grand Tours, including their best positions
    and stage results. It provides a comprehensive overview of their Grand Tour achievements.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get grand tour results
        grand_tour_results = rider.grand_tour_results()
        
        # Check if results exist
        if grand_tour_results is None or not hasattr(grand_tour_results, 'results_df') or grand_tour_results.results_df.empty:
            return f"No Grand Tour results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(grand_tour_results, 'header_details') and grand_tour_results.header_details and 'name' in grand_tour_results.header_details:
            info += f"Grand Tour Results for {grand_tour_results.header_details['name']}:\n\n"
        else:
            info += f"Grand Tour Results for Rider ID {rider_id}:\n\n"
        
        # Get results for each Grand Tour
        results_df = grand_tour_results.results_df
        
        # Group results by race
        for race in results_df['Race'].unique():
            race_results = results_df[results_df['Race'] == race]
            info += f"{race}:\n"
            
            # Sort by year (most recent first)
            race_results = race_results.sort_values('Year', ascending=False)
            
            for _, row in race_results.iterrows():
                year = row.get('Year', 'N/A')
                pos = row.get('Pos', 'N/A')
                time = row.get('Time', '')
                
                result_line = f"  {year}: {pos}"
                if time:
                    result_line += f" - {time}"
                info += result_line + "\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving Grand Tour results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_monument_results(rider_id: int) -> str:
    """Get the results of a professional cyclist in cycling's five Monuments (Milan-San Remo, Tour of Flanders,
    Paris-Roubaix, Liège-Bastogne-Liège, and Giro di Lombardia).

    This tool retrieves the rider's performances in all five Monument races, including their positions
    and times. It provides a comprehensive overview of their achievements in cycling's most prestigious one-day races.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get monument results
        monument_results = rider.monument_results()
        
        # Check if results exist
        if monument_results is None or not hasattr(monument_results, 'results_df') or monument_results.results_df.empty:
            return f"No Monument results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(monument_results, 'header_details') and monument_results.header_details and 'name' in monument_results.header_details:
            info += f"Monument Results for {monument_results.header_details['name']}:\n\n"
        else:
            info += f"Monument Results for Rider ID {rider_id}:\n\n"
        
        # Get results for each Monument
        results_df = monument_results.results_df
        
        # Group results by race
        for race in results_df['Race'].unique():
            race_results = results_df[results_df['Race'] == race]
            info += f"{race}:\n"
            
            # Sort by year (most recent first)
            race_results = race_results.sort_values('Year', ascending=False)
            
            for _, row in race_results.iterrows():
                year = row.get('Year', 'N/A')
                pos = row.get('Pos', 'N/A')
                time = row.get('Time', '')
                
                result_line = f"  {year}: {pos}"
                if time:
                    result_line += f" - {time}"
                info += result_line + "\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving Monument results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_team_and_ranking(rider_id: int) -> str:
    """Get information about a professional cyclist's team affiliations and UCI rankings throughout their career.

    This tool retrieves the rider's team history and their UCI ranking points over time. It provides a comprehensive
    overview of their professional career progression through different teams and their performance in the UCI rankings.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get team and ranking information
        team_ranking = rider.team_and_ranking()
        
        # Check if results exist
        if team_ranking is None or not hasattr(team_ranking, 'results_df') or team_ranking.results_df.empty:
            return f"No team and ranking information found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(team_ranking, 'header_details') and team_ranking.header_details and 'name' in team_ranking.header_details:
            info += f"Team and Ranking History for {team_ranking.header_details['name']}:\n\n"
        else:
            info += f"Team and Ranking History for Rider ID {rider_id}:\n\n"
        
        # Get results
        results_df = team_ranking.results_df
        
        # Sort by year (most recent first)
        results_df = results_df.sort_values('Year', ascending=False)
        
        # Group by year
        for year in results_df['Year'].unique():
            year_data = results_df[results_df['Year'] == year]
            info += f"{year}:\n"
            
            # Get team information
            team = year_data['Team'].iloc[0] if not year_data['Team'].empty else 'N/A'
            info += f"  Team: {team}\n"
            
            # Get ranking information
            ranking = year_data['Ranking'].iloc[0] if not year_data['Ranking'].empty else 'N/A'
            points = year_data['Points'].iloc[0] if not year_data['Points'].empty else 'N/A'
            
            if ranking != 'N/A' or points != 'N/A':
                info += "  UCI Ranking: "
                if ranking != 'N/A':
                    info += f"{ranking}"
                if points != 'N/A':
                    info += f" ({points} points)"
                info += "\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving team and ranking information for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_race_history(rider_id: int, year: int = None) -> str:
    """Get the complete race history of a professional cyclist, optionally filtered by year.

    This tool retrieves a comprehensive list of all races the rider has participated in, including their
    positions, times, and race categories. It provides a detailed overview of their racing career.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get race history
        race_history = rider.race_history()
        
        # Check if results exist
        if race_history is None or not hasattr(race_history, 'results_df') or race_history.results_df.empty:
            return f"No race history found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(race_history, 'header_details') and race_history.header_details and 'name' in race_history.header_details:
            info += f"Race History for {race_history.header_details['name']}"
            if year:
                info += f" ({year})"
            info += ":\n\n"
        else:
            info += f"Race History for Rider ID {rider_id}"
            if year:
                info += f" ({year})"
            info += ":\n\n"
        
        # Get results
        results_df = race_history.results_df
        
        # Filter by year if specified
        if year:
            results_df = results_df[results_df['Year'] == year]
        
        # Sort by date (most recent first)
        results_df = results_df.sort_values('Date', ascending=False)
        
        # Group by year
        for year in results_df['Year'].unique():
            year_data = results_df[results_df['Year'] == year]
            info += f"{year}:\n"
            
            for _, row in year_data.iterrows():
                date = row.get('Date', 'N/A')
                race = row.get('Race', 'N/A')
                pos = row.get('Pos', 'N/A')
                category = row.get('CAT', 'N/A')
                time = row.get('Time', '')
                
                result_line = f"  {date} - {race} ({category}): {pos}"
                if time:
                    result_line += f" - {time}"
                info += result_line + "\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving race history for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_one_day_races(rider_id: int, year: int = None) -> str:
    """Get the results of a professional cyclist in one-day races, optionally filtered by year.

    This tool retrieves a comprehensive list of all one-day races the rider has participated in, including
    their positions, times, and race categories. It provides a detailed overview of their performance in
    one-day events.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get one-day race results
        one_day_results = rider.one_day_races()
        
        # Check if results exist
        if one_day_results is None or not hasattr(one_day_results, 'results_df') or one_day_results.results_df.empty:
            return f"No one-day race results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(one_day_results, 'header_details') and one_day_results.header_details and 'name' in one_day_results.header_details:
            info += f"One-Day Race Results for {one_day_results.header_details['name']}"
            if year:
                info += f" ({year})"
            info += ":\n\n"
        else:
            info += f"One-Day Race Results for Rider ID {rider_id}"
            if year:
                info += f" ({year})"
            info += ":\n\n"
        
        # Get results
        results_df = one_day_results.results_df
        
        # Filter by year if specified
        if year:
            results_df = results_df[results_df['Year'] == year]
        
        # Sort by date (most recent first)
        results_df = results_df.sort_values('Date', ascending=False)
        
        # Group by year
        for year in results_df['Year'].unique():
            year_data = results_df[results_df['Year'] == year]
            info += f"{year}:\n"
            
            for _, row in year_data.iterrows():
                date = row.get('Date', 'N/A')
                race = row.get('Race', 'N/A')
                pos = row.get('Pos', 'N/A')
                category = row.get('CAT', 'N/A')
                time = row.get('Time', '')
                
                result_line = f"  {date} - {race} ({category}): {pos}"
                if time:
                    result_line += f" - {time}"
                info += result_line + "\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving one-day race results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_stage_races(rider_id: int, year: int = None) -> str:
    """Get the results of a professional cyclist in stage races, optionally filtered by year.

    This tool retrieves a comprehensive list of all stage races the rider has participated in, including
    their positions, times, and race categories. It provides a detailed overview of their performance in
    multi-day events.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get stage race results
        stage_race_results = rider.stage_races()
        
        # Check if results exist
        if stage_race_results is None or not hasattr(stage_race_results, 'results_df') or stage_race_results.results_df.empty:
            return f"No stage race results found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(stage_race_results, 'header_details') and stage_race_results.header_details and 'name' in stage_race_results.header_details:
            info += f"Stage Race Results for {stage_race_results.header_details['name']}"
            if year:
                info += f" ({year})"
            info += ":\n\n"
        else:
            info += f"Stage Race Results for Rider ID {rider_id}"
            if year:
                info += f" ({year})"
            info += ":\n\n"
        
        # Get results
        results_df = stage_race_results.results_df
        
        # Filter by year if specified
        if year:
            results_df = results_df[results_df['Year'] == year]
        
        # Sort by date (most recent first)
        results_df = results_df.sort_values('Date', ascending=False)
        
        # Group by year
        for year in results_df['Year'].unique():
            year_data = results_df[results_df['Year'] == year]
            info += f"{year}:\n"
            
            for _, row in year_data.iterrows():
                date = row.get('Date', 'N/A')
                race = row.get('Race', 'N/A')
                pos = row.get('Pos', 'N/A')
                category = row.get('CAT', 'N/A')
                time = row.get('Time', '')
                
                result_line = f"  {date} - {race} ({category}): {pos}"
                if time:
                    result_line += f" - {time}"
                info += result_line + "\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving stage race results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool()
async def get_rider_teams(rider_id: int) -> str:
    """Get information about all teams a professional cyclist has ridden for throughout their career.

    This tool retrieves a comprehensive list of all teams the rider has been a member of, including
    the years they were with each team. It provides a detailed overview of their professional career
    progression through different teams.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get team information
        teams = rider.teams()
        
        # Check if results exist
        if teams is None or not hasattr(teams, 'results_df') or teams.results_df.empty:
            return f"No team information found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(teams, 'header_details') and teams.header_details and 'name' in teams.header_details:
            info += f"Team History for {teams.header_details['name']}:\n\n"
        else:
            info += f"Team History for Rider ID {rider_id}:\n\n"
        
        # Get results
        results_df = teams.results_df
        
        # Sort by year (most recent first)
        results_df = results_df.sort_values('Year', ascending=False)
        
        # Group by team
        for team in results_df['Team'].unique():
            team_data = results_df[results_df['Team'] == team]
            info += f"{team}:\n"
            
            # Get years
            years = sorted(team_data['Year'].unique())
            if len(years) == 1:
                info += f"  {years[0]}\n"
            else:
                info += f"  {years[-1]}-{years[0]}\n"
            
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving team information for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

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