from typing import Any
import sys
import os
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
from datetime import datetime
from FirstCyclingAPI.first_cycling_api.rider.rider import Rider
from FirstCyclingAPI.first_cycling_api.race.race import Race
from FirstCyclingAPI.first_cycling_api.api import FirstCyclingAPI

# Add the FirstCyclingAPI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "FirstCyclingAPI"))

# Import from the FirstCycling API
from first_cycling_api.rider.rider import Rider
from first_cycling_api.race.race import RaceEdition

# Initialize FastMCP server
mcp = FastMCP("firstcycling")

@mcp.tool(
    description="""Get comprehensive information about a professional cyclist including their current team, nationality, date of birth, and recent race results. 
    This tool provides a detailed overview of a rider's current status and recent performance in professional cycling races. 
    The information includes their current team affiliation, nationality, age, and their most recent race results with positions and times.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get basic info for Tadej Pogačar (ID: 16973)
    - Get basic info for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Full name and current team
    - Nationality and date of birth
    - UCI ID and social media handles
    - Last 5 race results with positions and times
    - Total number of UCI victories"""
)
async def get_rider_info(rider_id: int) -> str:
    """Get basic information about a rider.

    Args:
        rider_id (int): The unique identifier for the rider. This ID can be found on FirstCycling.com
                       in the rider's profile URL (e.g., for rider 12345, the URL would be firstcycling.com/rider/12345).

    Returns:
        str: A formatted string containing the rider's information including:
             - Full name
             - Current team (if available)
             - Nationality
             - Date of birth
             - Recent race results (last 5 races) with positions and times

    Raises:
        Exception: If the rider is not found or if there are connection issues.
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

@mcp.tool(
    description="""Retrieve the best career results of a professional cyclist, including their top finishes in various races. 
    This tool provides a comprehensive overview of a rider's most significant achievements throughout their career, 
    including their highest positions in major races, stage wins, and overall classifications. 
    Results are sorted by importance and include detailed information about each race.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get top 10 best results for Tadej Pogačar (ID: 16973)
    - Get top 5 best results for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Rider's name and career highlights
    - Top results sorted by importance
    - Race details including category and country
    - Date and position for each result"""
)
async def get_rider_best_results(rider_id: int, limit: int = 10) -> str:
    """Get the best results of a rider throughout their career.

    Args:
        rider_id (int): The unique identifier for the rider. This ID can be found on FirstCycling.com
                       in the rider's profile URL (e.g., for rider 12345, the URL would be firstcycling.com/rider/12345).
        limit (int, optional): The maximum number of results to return. Defaults to 10.
                             This parameter helps control the amount of data returned and can be adjusted
                             based on the level of detail needed. Maximum recommended value is 20.

    Returns:
        str: A formatted string containing the rider's best results, including:
             - Race name and edition
             - Date of the race
             - Position achieved
             - Time or gap to winner (if applicable)
             - Race category and type
             - Any special achievements (e.g., stage wins, points classification)

    Raises:
        Exception: If the rider is not found or if there are connection issues.
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

@mcp.tool(
    description="""Get comprehensive results for a rider in Grand Tours (Tour de France, Giro d'Italia, and Vuelta a España). 
    This tool provides detailed information about a rider's performance in cycling's most prestigious three-week races, 
    including their overall classification positions, stage wins, and special classification results. 
    The data is organized chronologically and includes all relevant race details.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get Grand Tour results for Tadej Pogačar (ID: 16973)
    - Get Grand Tour results for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Results for each Grand Tour (Tour de France, Giro, Vuelta)
    - Overall classification positions
    - Stage wins and special classification results
    - Time gaps and race details"""
)
async def get_rider_grand_tour_results(rider_id: int) -> str:
    """Get results for a rider in Grand Tours.

    Args:
        rider_id (int): The unique identifier for the rider. This ID can be found on FirstCycling.com
                       in the rider's profile URL (e.g., for rider 12345, the URL would be firstcycling.com/rider/12345).

    Returns:
        str: A formatted string containing the rider's Grand Tour results, including:
             - Race name and year
             - Overall classification position
             - Time or gap to winner
             - Stage wins (if any)
             - Points classification results
             - Mountains classification results
             - Young rider classification results (if applicable)
             - Team classification results

    Raises:
        Exception: If the rider is not found or if there are connection issues.
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

@mcp.tool(
    description="""Retrieve detailed results for a rider in cycling's five Monument races (Milan-San Remo, Tour of Flanders, 
    Paris-Roubaix, Liège-Bastogne-Liège, and Il Lombardia). These are the most prestigious one-day races in professional cycling. 
    The tool provides comprehensive information about a rider's performance in these historic races, including their positions, 
    times, and any special achievements.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get Monument results for Tadej Pogačar (ID: 16973)
    - Get Monument results for Mathieu van der Poel (ID: 16975)
    
    Returns a formatted string with:
    - Results for each Monument race
    - Position and time for each participation
    - Race details and special achievements
    - Chronological organization by year"""
)
async def get_rider_monument_results(rider_id: int) -> str:
    """Get results for a rider in the five Monument races.

    Args:
        rider_id (int): The unique identifier for the rider. This ID can be found on FirstCycling.com
                       in the rider's profile URL (e.g., for rider 12345, the URL would be firstcycling.com/rider/12345).

    Returns:
        str: A formatted string containing the rider's Monument race results, including:
             - Race name and year
             - Position achieved
             - Time or gap to winner
             - Race distance
             - Any special achievements or notable moments
             - Team performance

    Raises:
        Exception: If the rider is not found or if there are connection issues.
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

@mcp.tool(
    description="""Get information about a professional cyclist's team affiliations and UCI rankings throughout their career.
    This tool retrieves the rider's team history and their UCI ranking points over time. It provides a comprehensive
    overview of their professional career progression through different teams and their performance in the UCI rankings.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get team and ranking history for Tadej Pogačar (ID: 16973)
    - Get team and ranking history for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Complete team history with years
    - UCI ranking positions and points
    - Career progression timeline
    - Current team and ranking status"""
)
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

@mcp.tool(
    description="""Get the complete race history of a professional cyclist, optionally filtered by year.
    This tool retrieves a comprehensive list of all races the rider has participated in, including their
    positions, times, and race categories. It provides a detailed overview of their racing career.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get complete race history for Tadej Pogačar (ID: 16973)
    - Get 2023 race history for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - All races organized by year
    - Position and time for each race
    - Race category and details
    - Chronological organization"""
)
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

@mcp.tool(
    description="""Get the results of a professional cyclist in one-day races, optionally filtered by year.
    This tool retrieves a comprehensive list of all one-day races the rider has participated in, including
    their positions, times, and race categories. It provides a detailed overview of their performance in
    one-day events.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get all one-day race results for Tadej Pogačar (ID: 16973)
    - Get 2023 one-day race results for Mathieu van der Poel (ID: 16975)
    
    Returns a formatted string with:
    - One-day race results organized by year
    - Position and time for each race
    - Race category and details
    - Chronological organization"""
)
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

@mcp.tool(
    description="""Get the results of a professional cyclist in stage races, optionally filtered by year.
    This tool retrieves a comprehensive list of all stage races the rider has participated in, including
    their positions, times, and race categories. It provides a detailed overview of their performance in
    multi-day events.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get all stage race results for Tadej Pogačar (ID: 16973)
    - Get 2023 stage race results for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Stage race results organized by year
    - Position and time for each race
    - Race category and details
    - Chronological organization"""
)
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

@mcp.tool(
    description="""Get information about all teams a professional cyclist has ridden for throughout their career.
    This tool retrieves a comprehensive list of all teams the rider has been a member of, including
    the years they were with each team. It provides a detailed overview of their professional career
    progression through different teams.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get team history for Tadej Pogačar (ID: 16973)
    - Get team history for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Complete list of teams
    - Years spent with each team
    - Career timeline
    - Current team status"""
)
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

@mcp.tool(
    description="""Get results for a specific race in a given year.
    This tool retrieves comprehensive information about a race edition, including the general classification,
    race details, and key statistics. It provides a detailed overview of the race's outcome and structure.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get 2023 Tour de France results (ID: 17, Year: 2023)
    - Get 2023 Giro d'Italia results (ID: 18, Year: 2023)
    
    Returns a formatted string with:
    - Race name and year
    - Race details (date, category, country)
    - General classification top 10
    - Key race statistics"""
)
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

@mcp.tool(
    description="""Get comprehensive overview information about a specific race.
    This tool retrieves general information about a race, including its classifications,
    history, and key details. It provides a high-level overview of the race's characteristics
    and structure.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get overview for Tour de France (ID: 17)
    - Get overview for Giro d'Italia (ID: 18)
    
    Returns a formatted string with:
    - Race name and basic details
    - Race classifications
    - Most successful riders
    - Age records (youngest/oldest winners)"""
)
async def get_race_overview(race_id: int) -> str:
    """Get comprehensive overview information about a specific race.

    This tool retrieves general information about a race, including its classifications,
    history, and key details. It provides a high-level overview of the race's characteristics
    and structure.

    Args:
        race_id: The FirstCycling race ID (e.g., 17 for Tour de France)
    """
    try:
        # Create a race instance
        race = Race(race_id)
        
        # Get race overview
        overview = race.overview()
        
        # Build information string
        info = ""
        
        # Add race name if available
        if hasattr(overview, 'race_name'):
            info += f"Race: {overview.race_name}\n\n"
        
        # Add race details if available
        if hasattr(overview, 'race_details'):
            race_details = overview.race_details
            if 'Date' in race_details:
                info += f"Date: {race_details['Date']}\n"
            if 'Category' in race_details:
                info += f"Category: {race_details['Category']}\n"
            if 'Country' in race_details:
                info += f"Country: {race_details['Country']}\n"
            if 'Distance' in race_details:
                info += f"Distance: {race_details['Distance']}\n"
            if 'Stages' in race_details:
                info += f"Number of Stages: {race_details['Stages']}\n"
        
        # Add classifications if available
        if hasattr(overview, 'classifications'):
            info += "\nClassifications:\n"
            for classification in overview.classifications:
                info += f"- {classification}\n"
        
        # Add victory table if available
        try:
            victory_table = race.victory_table()
            if hasattr(victory_table, 'results_table') and not victory_table.results_table.empty:
                info += "\nMost Successful Riders:\n"
                # Get top 5 riders
                results_df = victory_table.results_table.head(5)
                for _, row in results_df.iterrows():
                    rider = row.get('Rider', 'N/A')
                    wins = row.get('Wins', 'N/A')
                    info += f"- {rider}: {wins} wins\n"
        except:
            pass
        
        # Add youngest/oldest winners if available
        try:
            age_stats = race.youngest_oldest_winners()
            if hasattr(age_stats, 'results_table') and not age_stats.results_table.empty:
                info += "\nAge Records:\n"
                results_df = age_stats.results_table
                if 'Youngest' in results_df.columns:
                    info += f"Youngest Winner: {results_df['Youngest'].iloc[0]}\n"
                if 'Oldest' in results_df.columns:
                    info += f"Oldest Winner: {results_df['Oldest'].iloc[0]}\n"
        except:
            pass
        
        return info
    except Exception as e:
        return f"Error retrieving race overview: {str(e)}"

@mcp.tool(
    description="""Get detailed stage profiles for a specific race edition.
    This tool retrieves information about each stage of a race, including distances,
    elevation profiles, and key details about the route. It provides a comprehensive
    overview of the race's structure and challenges.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get 2023 Tour de France stage profiles (ID: 17, Year: 2023)
    - Get 2023 Giro d'Italia stage profiles (ID: 18, Year: 2023)
    
    Returns a formatted string with:
    - Stage-by-stage details
    - Distance and elevation profiles
    - Key climbs and their categories
    - Start and finish locations"""
)
async def get_race_stage_profiles(race_id: int, year: int) -> str:
    """Get detailed stage profiles for a specific race edition.

    This tool retrieves information about each stage of a race, including distances,
    elevation profiles, and key details about the route. It provides a comprehensive
    overview of the race's structure and challenges.

    Args:
        race_id: The FirstCycling race ID (e.g., 17 for Tour de France)
        year: The year of the race edition (e.g., 2023)
    """
    try:
        # Create a race edition instance
        race_edition = RaceEdition(race_id, year)
        
        # Get stage profiles
        stage_profiles = race_edition.stage_profiles()
        
        # Build information string
        info = ""
        
        # Add race name if available
        if hasattr(stage_profiles, 'race_name'):
            info += f"Race: {stage_profiles.race_name} {year}\n\n"
        
        # Add stage information if available
        if hasattr(stage_profiles, 'stages'):
            for stage in stage_profiles.stages:
                info += f"Stage {stage.get('number', 'N/A')}:\n"
                
                # Add stage details
                if 'date' in stage:
                    info += f"Date: {stage['date']}\n"
                if 'start' in stage:
                    info += f"Start: {stage['start']}\n"
                if 'finish' in stage:
                    info += f"Finish: {stage['finish']}\n"
                if 'distance' in stage:
                    info += f"Distance: {stage['distance']}\n"
                if 'type' in stage:
                    info += f"Type: {stage['type']}\n"
                
                # Add elevation information if available
                if 'elevation' in stage:
                    elevation = stage['elevation']
                    if 'start' in elevation:
                        info += f"Start Elevation: {elevation['start']}m\n"
                    if 'finish' in elevation:
                        info += f"Finish Elevation: {elevation['finish']}m\n"
                    if 'highest' in elevation:
                        info += f"Highest Point: {elevation['highest']}m\n"
                    if 'lowest' in elevation:
                        info += f"Lowest Point: {elevation['lowest']}m\n"
                    if 'climbing' in elevation:
                        info += f"Total Climbing: {elevation['climbing']}m\n"
                
                # Add key climbs if available
                if 'climbs' in stage and stage['climbs']:
                    info += "\nKey Climbs:\n"
                    for climb in stage['climbs']:
                        info += f"- {climb.get('name', 'N/A')}"
                        if 'category' in climb:
                            info += f" (Category {climb['category']})"
                        if 'distance' in climb:
                            info += f" - {climb['distance']}km"
                        if 'elevation' in climb:
                            info += f" - {climb['elevation']}m"
                        info += "\n"
                
                info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving stage profiles: {str(e)}"

@mcp.tool(
    description="""Get the startlist for a specific race edition.
    This tool retrieves the list of riders and teams participating in a race.
    It can provide either a basic startlist or an extended version with additional details.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get basic startlist for 2023 Tour de France (ID: 17, Year: 2023)
    - Get extended startlist for 2023 Giro d'Italia (ID: 18, Year: 2023, extended=True)
    
    Returns a formatted string with:
    - Race name and year
    - Teams and their riders
    - Extended information (if requested):
      - Rider nationality
      - Age
      - UCI ranking"""
)
async def get_race_startlist(race_id: int, year: int, extended: bool = False) -> str:
    """Get the startlist for a specific race edition.

    This tool retrieves the list of riders and teams participating in a race.
    It can provide either a basic startlist or an extended version with additional details.

    Args:
        race_id: The FirstCycling race ID (e.g., 17 for Tour de France)
        year: The year of the race edition (e.g., 2023)
        extended: Whether to get the extended startlist with additional details (default: False)
    """
    try:
        # Create a race edition instance
        race_edition = RaceEdition(race_id, year)
        
        # Get startlist (normal or extended)
        startlist = race_edition.startlist_extended() if extended else race_edition.startlist()
        
        # Build information string
        info = ""
        
        # Add race name if available
        if hasattr(startlist, 'race_name'):
            info += f"Race: {startlist.race_name} {year}\n\n"
        
        # Add startlist information if available
        if hasattr(startlist, 'startlist'):
            # Group riders by team
            teams = {}
            for rider in startlist.startlist:
                team = rider.get('team', 'Unknown Team')
                if team not in teams:
                    teams[team] = []
                teams[team].append(rider)
            
            # Format output by team
            for team, riders in teams.items():
                info += f"\n{team}:\n"
                for rider in riders:
                    info += f"- {rider.get('name', 'N/A')}"
                    if extended:
                        if 'nationality' in rider:
                            info += f" ({rider['nationality']})"
                        if 'age' in rider:
                            info += f" - Age: {rider['age']}"
                        if 'uci_rank' in rider:
                            info += f" - UCI Rank: {rider['uci_rank']}"
                    info += "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving startlist: {str(e)}"

@mcp.tool(
    description="""Get the victories achieved by a professional cyclist.
    This tool retrieves all victories or filtered victories (World Tour or UCI races only) for a rider.
    It provides details such as the race name, date, and race category.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get all victories for Tadej Pogačar (ID: 16973)
    - Get World Tour victories for Jonas Vingegaard (ID: 16974, world_tour=True)
    - Get UCI victories for Mathieu van der Poel (ID: 16975, uci=True)
    
    Returns a formatted string with:
    - List of victories organized by date
    - Race details and category
    - Country and date information
    - Filtered results if specified"""
)
async def get_rider_victories(rider_id: int, world_tour: bool = False, uci: bool = False) -> str:
    """Get the victories achieved by a professional cyclist.

    This tool retrieves all victories or filtered victories (World Tour or UCI races only) for a rider.
    It provides details such as the race name, date, and race category.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        world_tour: If True, only return World Tour victories (default: False)
        uci: If True, only return UCI victories (default: False)
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get victories with optional filters
        victories = rider.victories(world_tour=world_tour, uci=uci)
        
        # Check if results exist
        if victories is None or not hasattr(victories, 'results_df') or victories.results_df.empty:
            return f"No victories found for rider ID {rider_id}. This rider ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(victories, 'header_details') and victories.header_details and 'name' in victories.header_details:
            info += f"Victories for {victories.header_details['name']}:\n\n"
        else:
            info += f"Victories for Rider ID {rider_id}:\n\n"
        
        # Add filter information if applicable
        if world_tour:
            info += "(World Tour races only)\n"
        elif uci:
            info += "(UCI races only)\n"
        info += "\n"
        
        # Get all victories
        results_df = victories.results_df
        
        # Sort by date (most recent first)
        results_df = results_df.sort_values('Date', ascending=False)
        
        for _, row in results_df.iterrows():
            date = row.get('Date', 'N/A')
            race = row.get('Race', 'N/A')
            category = row.get('CAT', 'N/A')
            country = row.get('Race_Country', 'N/A')
            
            result_line = f"{race} ({category})"
            if date != 'N/A':
                result_line += f" - {date}"
            if country != 'N/A':
                result_line += f" - {country}"
            info += result_line + "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving victories for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get the all-time victory table for a race.
    This tool retrieves a comprehensive list of all winners of a race throughout its history,
    including details such as the year, winner's name, and team.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get victory table for Tour de France (ID: 17)
    - Get victory table for Giro d'Italia (ID: 18)
    
    Returns a formatted string with:
    - Complete list of winners
    - Year and winner details
    - Team and country information
    - Chronological organization"""
)
async def get_race_victory_table(race_id: int) -> str:
    """Get the all-time victory table for a race.

    This tool retrieves a comprehensive list of all winners of a race throughout its history,
    including details such as the year, winner's name, and team.

    Args:
        race_id: The FirstCycling race ID (e.g., 6 for Tour of the Basque Country)
    """
    try:
        # Create a race instance
        race = Race(race_id)
        
        # Get victory table
        victory_table = race.victory_table()
        
        # Check if results exist
        if victory_table is None or not hasattr(victory_table, 'results_df') or victory_table.results_df.empty:
            return f"No victory table found for race ID {race_id}. This race ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add race name if available from header details
        if hasattr(victory_table, 'header_details') and victory_table.header_details and 'name' in victory_table.header_details:
            info += f"Victory Table for {victory_table.header_details['name']}:\n\n"
        else:
            info += f"Victory Table for Race ID {race_id}:\n\n"
        
        # Get all victories
        results_df = victory_table.results_df
        
        # Sort by year (most recent first)
        results_df = results_df.sort_values('Year', ascending=False)
        
        for _, row in results_df.iterrows():
            year = row.get('Year', 'N/A')
            rider = row.get('Rider', 'N/A')
            team = row.get('Team', 'N/A')
            country = row.get('Rider_Country', 'N/A')
            
            result_line = f"{year}: {rider}"
            if team != 'N/A':
                result_line += f" ({team})"
            if country != 'N/A':
                result_line += f" - {country}"
            info += result_line + "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving victory table for race ID {race_id}: {str(e)}. The race ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get year-by-year statistics for a race.
    This tool retrieves comprehensive statistics for a race across all years, optionally filtered
    by a specific classification (e.g., general classification, points classification, etc.).
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get year-by-year stats for Tour de France (ID: 17)
    - Get year-by-year stats for Giro d'Italia (ID: 18, classification_num=1)
    
    Returns a formatted string with:
    - Year-by-year results
    - Winner and team information
    - Classification details
    - Country information"""
)
async def get_race_year_by_year(race_id: int, classification_num: int = None) -> str:
    """Get year-by-year statistics for a race.

    This tool retrieves comprehensive statistics for a race across all years, optionally filtered
    by a specific classification (e.g., general classification, points classification, etc.).

    Args:
        race_id: The FirstCycling race ID (e.g., 6 for Tour of the Basque Country)
        classification_num: Classification number to filter results (optional)
    """
    try:
        # Create a race instance
        race = Race(race_id)
        
        # Get year-by-year statistics
        year_stats = race.year_by_year(classification_num)
        
        # Check if results exist
        if year_stats is None or not hasattr(year_stats, 'results_df') or year_stats.results_df.empty:
            return f"No year-by-year statistics found for race ID {race_id}. This race ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add race name if available from header details
        if hasattr(year_stats, 'header_details') and year_stats.header_details and 'name' in year_stats.header_details:
            info += f"Year-by-Year Statistics for {year_stats.header_details['name']}:\n\n"
        else:
            info += f"Year-by-Year Statistics for Race ID {race_id}:\n\n"
        
        # Get all statistics
        results_df = year_stats.results_df
        
        # Sort by year (most recent first)
        results_df = results_df.sort_values('Year', ascending=False)
        
        for _, row in results_df.iterrows():
            year = row.get('Year', 'N/A')
            rider = row.get('Rider', 'N/A')
            team = row.get('Team', 'N/A')
            country = row.get('Rider_Country', 'N/A')
            
            result_line = f"{year}: {rider}"
            if team != 'N/A':
                result_line += f" ({team})"
            if country != 'N/A':
                result_line += f" - {country}"
            info += result_line + "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving year-by-year statistics for race ID {race_id}: {str(e)}. The race ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get the youngest and oldest winners of a race.
    This tool retrieves information about the youngest and oldest riders to have won a race,
    including their age at the time of victory and other relevant details.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get age records for Tour de France (ID: 17)
    - Get age records for Giro d'Italia (ID: 18)
    
    Returns a formatted string with:
    - Youngest winner details
    - Oldest winner details
    - Age and year information
    - Team and country details"""
)
async def get_race_youngest_oldest_winners(race_id: int) -> str:
    """Get the youngest and oldest winners of a race.

    This tool retrieves information about the youngest and oldest riders to have won a race,
    including their age at the time of victory and other relevant details.

    Args:
        race_id: The FirstCycling race ID (e.g., 6 for Tour of the Basque Country)
    """
    try:
        # Create a race instance
        race = Race(race_id)
        
        # Get youngest and oldest winners
        winners = race.youngest_oldest_winners()
        
        # Check if results exist
        if winners is None or not hasattr(winners, 'results_df') or winners.results_df.empty:
            return f"No winner information found for race ID {race_id}. This race ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add race name if available from header details
        if hasattr(winners, 'header_details') and winners.header_details and 'name' in winners.header_details:
            info += f"Youngest and Oldest Winners for {winners.header_details['name']}:\n\n"
        else:
            info += f"Youngest and Oldest Winners for Race ID {race_id}:\n\n"
        
        # Get all winners
        results_df = winners.results_df
        
        # Sort by age
        results_df = results_df.sort_values('Age')
        
        # Get youngest winner
        youngest = results_df.iloc[0]
        info += "Youngest Winner:\n"
        info += f"Year: {youngest.get('Year', 'N/A')}\n"
        info += f"Rider: {youngest.get('Rider', 'N/A')}\n"
        info += f"Age: {youngest.get('Age', 'N/A')}\n"
        info += f"Team: {youngest.get('Team', 'N/A')}\n"
        info += f"Country: {youngest.get('Rider_Country', 'N/A')}\n\n"
        
        # Get oldest winner
        oldest = results_df.iloc[-1]
        info += "Oldest Winner:\n"
        info += f"Year: {oldest.get('Year', 'N/A')}\n"
        info += f"Rider: {oldest.get('Rider', 'N/A')}\n"
        info += f"Age: {oldest.get('Age', 'N/A')}\n"
        info += f"Team: {oldest.get('Team', 'N/A')}\n"
        info += f"Country: {oldest.get('Rider_Country', 'N/A')}\n"
        
        return info
    except Exception as e:
        return f"Error retrieving youngest and oldest winners for race ID {race_id}: {str(e)}. The race ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get the all-time stage victories for a race.
    This tool retrieves a comprehensive list of all stage winners in a race's history,
    including details such as the year, stage number, winner's name, and team.
    
    Note: If you don't know the race's ID, use the search_race tool first to find it by name.
    
    Example usage:
    - Get stage victories for Tour de France (ID: 17)
    - Get stage victories for Giro d'Italia (ID: 18)
    
    Returns a formatted string with:
    - Complete list of stage winners
    - Year and stage number
    - Winner and team details
    - Country information"""
)
async def get_race_stage_victories(race_id: int) -> str:
    """Get the all-time stage victories for a race.

    This tool retrieves a comprehensive list of all stage winners in a race's history,
    including details such as the year, stage number, winner's name, and team.

    Args:
        race_id: The FirstCycling race ID (e.g., 6 for Tour of the Basque Country)
    """
    try:
        # Create a race instance
        race = Race(race_id)
        
        # Get stage victories
        stage_victories = race.stage_victories()
        
        # Check if results exist
        if stage_victories is None or not hasattr(stage_victories, 'results_df') or stage_victories.results_df.empty:
            return f"No stage victories found for race ID {race_id}. This race ID may not exist."
        
        # Build results information string
        info = ""
        
        # Add race name if available from header details
        if hasattr(stage_victories, 'header_details') and stage_victories.header_details and 'name' in stage_victories.header_details:
            info += f"Stage Victories for {stage_victories.header_details['name']}:\n\n"
        else:
            info += f"Stage Victories for Race ID {race_id}:\n\n"
        
        # Get all stage victories
        results_df = stage_victories.results_df
        
        # Sort by year and stage number (most recent first)
        results_df = results_df.sort_values(['Year', 'Stage'], ascending=[False, True])
        
        for _, row in results_df.iterrows():
            year = row.get('Year', 'N/A')
            stage = row.get('Stage', 'N/A')
            rider = row.get('Rider', 'N/A')
            team = row.get('Team', 'N/A')
            country = row.get('Rider_Country', 'N/A')
            
            result_line = f"{year} Stage {stage}: {rider}"
            if team != 'N/A':
                result_line += f" ({team})"
            if country != 'N/A':
                result_line += f" - {country}"
            info += result_line + "\n"
        
        return info
    except Exception as e:
        return f"Error retrieving stage victories for race ID {race_id}: {str(e)}. The race ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Search for professional cyclists by name. This tool helps find riders by their name, 
    returning a list of matching riders with their IDs, nationalities, and current teams. This is useful 
    when you know a rider's name but need their ID for other operations.
    
    Example usage:
    - Search for "pogacar" to find Tadej Pogačar
    - Search for "vingegaard" to find Jonas Vingegaard
    
    Returns a formatted string with:
    - List of matching riders
    - Each rider's ID, name, nationality, and current team
    - Number of matches found"""
)
async def search_rider(query: str) -> str:
    """Search for riders by name.

    Args:
        query (str): The search query string to find riders by name.

    Returns:
        str: A formatted string containing matching riders with their details:
             - Rider ID
             - Full name
             - Nationality
             - Current team (if available)
    """
    try:
        # Search for riders
        riders = Rider.search(query)
        
        if not riders:
            return f"No riders found matching the query '{query}'."
        
        # Build results string
        info = f"Found {len(riders)} riders matching '{query}':\n\n"
        
        for rider in riders:
            info += f"ID: {rider['id']}\n"
            info += f"Name: {rider['name']}\n"
            if rider['nationality']:
                info += f"Nationality: {rider['nationality'].upper()}\n"
            if rider['team']:
                info += f"Team: {rider['team']}\n"
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error searching for riders: {str(e)}"

@mcp.tool(
    description="""Search for cycling races by name. This tool helps find races by their name, 
    returning a list of matching races with their IDs and countries. This is useful when you know 
    a race's name but need its ID for other operations.
    
    Example usage:
    - Search for "tour" to find Tour de France and other tours
    - Search for "giro" to find Giro d'Italia
    
    Returns a formatted string with:
    - List of matching races
    - Each race's ID, name, and country
    - Number of matches found"""
)
async def search_race(query: str) -> str:
    """Search for races by name.

    Args:
        query (str): The search query string to find races by name.

    Returns:
        str: A formatted string containing matching races with their details:
             - Race ID
             - Race name
             - Country
    """
    try:
        # Search for races
        races = Race.search(query)
        
        if not races:
            return f"No races found matching the query '{query}'."
        
        # Build results string
        info = f"Found {len(races)} races matching '{query}':\n\n"
        
        for race in races:
            info += f"ID: {race['id']}\n"
            info += f"Name: {race['name']}\n"
            if race['country']:
                info += f"Country: {race['country'].upper()}\n"
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error searching for races: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 