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
            return f"No best results found for rider ID {rider_id}. Check if this rider has results on FirstCycling.com."
        
        # Build results information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(best_results, 'header_details') and best_results.header_details and best_results.header_details.get('current_team'):
            rider_name = best_results.soup.find('h1').text.strip() if best_results.soup.find('h1') else f"Rider ID {rider_id}"
            info += f"Best Results for {rider_name}:\n\n"
        else:
            info += f"Best Results for Rider ID {rider_id}:\n\n"
        
        # Get top results
        results_df = best_results.results_df.head(limit)
        
        for _, row in results_df.iterrows():
            pos = row.get('Pos', 'N/A')
            race = row.get('Race', 'N/A')
            editions = row.get('Editions', 'N/A')
            category = row.get('CAT', '')
            country = row.get('Race_Country', '')
            
            result_line = f"{pos}. {race}"
            if category:
                result_line += f" ({category})"
            if editions != 'N/A':
                result_line += f" - {editions}"
            if country:
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
        
        # Build information string
        info = ""
        
        # Get rider name
        rider_name = None
        if hasattr(grand_tour_results, 'header_details') and grand_tour_results.header_details and 'name' in grand_tour_results.header_details:
            rider_name = grand_tour_results.header_details['name']
        else:
            # Try to extract rider name from page title
            if hasattr(grand_tour_results, 'soup') and grand_tour_results.soup:
                title = grand_tour_results.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
        
        # Format title
        if rider_name:
            info += f"Grand Tour Results for {rider_name}:\n\n"
        else:
            info += f"Grand Tour Results for Rider ID {rider_id}:\n\n"
        
        # Check if we need to use standard parsing or direct HTML parsing
        if hasattr(grand_tour_results, 'results_df') and not (grand_tour_results.results_df is None or grand_tour_results.results_df.empty):
            # Use standard parsing
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
        else:
            # Direct HTML parsing
            if not hasattr(grand_tour_results, 'soup') or not grand_tour_results.soup:
                return f"No Grand Tour results found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = grand_tour_results.soup
            
            # Find Grand Tour results table
            tables = soup.find_all('table')
            gt_table = None
            
            # Look for the appropriate table that contains Grand Tour results
            # Usually it's a table with "Tour de France", "Giro d'Italia", or "Vuelta a España" mentioned
            grand_tours = ["Tour de France", "Giro d'Italia", "Vuelta a España"]
            
            for table in tables:
                for gt in grand_tours:
                    if gt in table.text:
                        gt_table = table
                        break
                if gt_table:
                    break
                
                # If not found by name, look for a table with "Race" and "Year" columns
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and "Race" in headers and "Year" in headers:
                    gt_table = table
                    break
            
            if not gt_table:
                return f"Could not find Grand Tour results table for rider ID {rider_id}."
            
            # Parse Grand Tour data
            rows = gt_table.find_all('tr')
            gt_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            race_idx = next((i for i, h in enumerate(headers) if "Race" in h), None)
            year_idx = next((i for i, h in enumerate(headers) if "Year" in h), None)
            pos_idx = next((i for i, h in enumerate(headers) if "Pos" in h), None)
            time_idx = next((i for i, h in enumerate(headers) if "Time" in h), None)
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:  # Ensure it's a data row
                    continue
                
                # Extract data
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                year_text = cols[year_idx].text.strip() if year_idx is not None and year_idx < len(cols) else "N/A"
                pos_text = cols[pos_idx].text.strip() if pos_idx is not None and pos_idx < len(cols) else "N/A"
                time_text = cols[time_idx].text.strip() if time_idx is not None and time_idx < len(cols) else ""
                
                # Only include if it's a Grand Tour
                if any(gt in race_text for gt in grand_tours):
                    gt_data.append({
                        'Race': race_text,
                        'Year': year_text,
                        'Pos': pos_text,
                        'Time': time_text
                    })
            
            # Group by race
            race_grouped = {}
            for result in gt_data:
                race = result['Race']
                if race not in race_grouped:
                    race_grouped[race] = []
                race_grouped[race].append(result)
            
            # Format output by race
            for race, results in race_grouped.items():
                info += f"{race}:\n"
                
                # Sort by year (most recent first)
                results.sort(key=lambda x: x['Year'], reverse=True)
                
                for result in results:
                    result_line = f"  {result['Year']}: {result['Pos']}"
                    if result['Time']:
                        result_line += f" - {result['Time']}"
                    info += result_line + "\n"
                
                info += "\n"
            
            if not gt_data:
                info += "No Grand Tour results found for this rider.\n"
        
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
        monument_races = {
            "Milano-Sanremo": [],
            "Paris-Roubaix": [],
            "Ronde van Vlaanderen": [],
            "Liège-Bastogne-Liège": [],
            "Il Lombardia": []
        }
        
        # Group results by monument races
        for _, row in monument_results.results_df.iterrows():
            race_name = row.get('Race', '')
            year = row.get('Year', '')
            position = row.get('Pos', '')
            
            # Check if this is one of the 5 monuments
            for monument in monument_races:
                if monument in race_name:
                    monument_races[monument].append((year, position))
                    break
        
        # Format and add results for each monument
        for monument, results in monument_races.items():
            if not results:
                continue
                
            info += f"{monument}:\n"
            
            # Sort results by year in descending order
            results.sort(key=lambda x: x[0], reverse=True)
            
            for year, position in results:
                info += f"  {year}: {position}\n"
            
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
        
        # Build information string
        info = ""
        
        # Add rider name if available from header details
        if hasattr(team_ranking, 'header_details') and team_ranking.header_details and 'name' in team_ranking.header_details:
            rider_name = team_ranking.header_details['name']
            info += f"Team and Ranking History for {rider_name}:\n\n"
        else:
            # Try to extract rider name from page title
            if hasattr(team_ranking, 'soup'):
                title = team_ranking.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
                    info += f"Team and Ranking History for {rider_name}:\n\n"
                else:
                    info += f"Team and Ranking History for Rider ID {rider_id}:\n\n"
            else:
                info += f"Team and Ranking History for Rider ID {rider_id}:\n\n"

        # Check if we need to use the default parsing or direct HTML parsing
        if hasattr(team_ranking, 'results_df') and not (team_ranking.results_df is None or team_ranking.results_df.empty):
            # Use the default parsed results
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
        else:
            # Direct HTML parsing if results_df is not available
            if not hasattr(team_ranking, 'soup'):
                return f"No team and ranking information found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = team_ranking.soup
            
            # Look for team and ranking information in tables
            tables = soup.find_all('table')
            stats_table = None
            
            # Find the table with team and ranking information
            # Usually, it's a table with "Year", "Team", "Ranking", "Points" headers
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and "Year" in headers and "Team" in headers:
                    stats_table = table
                    break
            
            if stats_table is None:
                return f"No team and ranking information could be found for rider ID {rider_id}."
            
            # Parse the table rows
            rows = stats_table.find_all('tr')
            
            # Skip the header row
            data = []
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 3:  # Ensure we have enough columns
                    year = cols[0].text.strip()
                    
                    # Extract team (might be in a link)
                    team_col = cols[1]
                    team_link = team_col.find('a')
                    team = team_link.text.strip() if team_link else team_col.text.strip()
                    
                    # Extract ranking and points 
                    # (format can vary but typically in columns 2 and 3)
                    ranking = cols[2].text.strip() if len(cols) > 2 else 'N/A'
                    points = cols[3].text.strip() if len(cols) > 3 else 'N/A'
                    
                    data.append({
                        'Year': year,
                        'Team': team,
                        'Ranking': ranking,
                        'Points': points
                    })
            
            # Sort by year (most recent first)
            data.sort(key=lambda x: x['Year'], reverse=True)
            
            # Build the information string
            for item in data:
                info += f"{item['Year']}:\n"
                info += f"  Team: {item['Team']}\n"
                
                if item['Ranking'] != 'N/A' or item['Points'] != 'N/A':
                    info += "  UCI Ranking: "
                    if item['Ranking'] != 'N/A':
                        info += f"{item['Ranking']}"
                    if item['Points'] != 'N/A':
                        info += f" ({item['Points']} points)"
                    info += "\n"
                
                info += "\n"
            
            if not data:
                return f"No team and ranking information could be parsed for rider ID {rider_id}."
        
        return info
    except Exception as e:
        return f"An error occurred while getting team and ranking information for rider ID {rider_id}: {str(e)}"

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
        
        # Build information string
        info = ""
        
        # Get rider name
        rider_name = None
        if hasattr(race_history, 'header_details') and race_history.header_details and 'name' in race_history.header_details:
            rider_name = race_history.header_details['name']
        else:
            # Try to extract rider name from page title
            if hasattr(race_history, 'soup') and race_history.soup:
                title = race_history.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
        
        # Format title
        if rider_name:
            info += f"Race History for {rider_name}"
        else:
            info += f"Race History for Rider ID {rider_id}"
        
        if year:
            info += f" ({year})"
        info += ":\n\n"
        
        # Check if we need to use standard parsing or direct HTML parsing
        if hasattr(race_history, 'results_df') and not (race_history.results_df is None or race_history.results_df.empty):
            # Use standard parsing
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
        else:
            # Direct HTML parsing
            if not hasattr(race_history, 'soup') or not race_history.soup:
                return f"No race history found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = race_history.soup
            
            # Find race history table
            tables = soup.find_all('table')
            race_table = None
            
            # Look for the appropriate table that contains race history
            # Usually has headers for date, race, position, etc.
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and ("Date" in headers or "Race" in headers):
                    race_table = table
                    break
            
            if not race_table:
                return f"Could not find race history table for rider ID {rider_id}."
            
            # Parse race data
            rows = race_table.find_all('tr')
            race_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            date_idx = next((i for i, h in enumerate(headers) if "Date" in h), None)
            race_idx = next((i for i, h in enumerate(headers) if "Race" in h), None)
            pos_idx = next((i for i, h in enumerate(headers) if "Pos" in h), None)
            cat_idx = next((i for i, h in enumerate(headers) if "CAT" in h), None)
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:  # Ensure it's a data row
                    continue
                
                # Extract data
                date_text = cols[date_idx].text.strip() if date_idx is not None and date_idx < len(cols) else "N/A"
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                pos_text = cols[pos_idx].text.strip() if pos_idx is not None and pos_idx < len(cols) else "N/A"
                cat_text = cols[cat_idx].text.strip() if cat_idx is not None and cat_idx < len(cols) else "N/A"
                
                # Extract year from date (format may vary, but often includes year)
                race_year = None
                if date_text != "N/A":
                    # Try common date formats to extract year
                    if len(date_text) >= 4:
                        try:
                            # If year is last part (e.g., "01.01.2023")
                            race_year = int(date_text[-4:])
                        except:
                            # If year is first part (e.g., "2023-01-01")
                            try:
                                race_year = int(date_text[:4])
                            except:
                                pass
                
                if race_year:
                    # Skip if a specific year was requested and this race is from a different year
                    if year and race_year != year:
                        continue
                    
                    race_data.append({
                        'Year': race_year,
                        'Date': date_text,
                        'Race': race_text,
                        'Pos': pos_text,
                        'CAT': cat_text
                    })
            
            # Group by year
            year_grouped = {}
            for race in race_data:
                year_val = race['Year']
                if year_val not in year_grouped:
                    year_grouped[year_val] = []
                year_grouped[year_val].append(race)
            
            # Sort years (most recent first)
            for year_val in sorted(year_grouped.keys(), reverse=True):
                races = year_grouped[year_val]
                info += f"{year_val}:\n"
                
                for race in races:
                    result_line = f"  {race['Date']} - {race['Race']} ({race['CAT']}): {race['Pos']}"
                    info += result_line + "\n"
                
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

@mcp.tool(
    description="""Get a rider's results in one-day races, optionally filtered by year.
    This tool provides detailed information about a professional cyclist's performance in one-day races,
    including their positions, race details, and achievements. One-day races are important events 
    in the cycling calendar that take place within a single day.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get one-day race results for Mathieu van der Poel (ID: 16975)
    - Get 2023 one-day race results for Wout van Aert (ID: 16976)
    
    Returns a formatted string with:
    - Results organized by year
    - Race name, date, and category
    - Position and time for each race
    - Comprehensive list of all one-day race participations"""
)
async def get_rider_one_day_races(rider_id: int, year: int = None) -> str:
    """Get a rider's results in one-day races, optionally filtered by year.

    This tool provides detailed information about a professional cyclist's performance in one-day races,
    including their positions, race details, and achievements. One-day races are important events 
    in the cycling calendar that take place within a single day.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16975 for Mathieu van der Poel)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.

    Returns:
        str: A formatted string containing the rider's one-day race results, including:
             - Race name and date
             - Position achieved
             - Race category and details
             - Results organized by year
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get one-day races results
        one_day_results = rider.one_day_races()
        
        # Build information string
        info = ""
        
        # Get rider name
        rider_name = None
        if hasattr(one_day_results, 'header_details') and one_day_results.header_details and 'name' in one_day_results.header_details:
            rider_name = one_day_results.header_details['name']
        else:
            # Try to extract rider name from page title
            if hasattr(one_day_results, 'soup') and one_day_results.soup:
                title = one_day_results.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
        
        # Format title
        if rider_name:
            info += f"One-Day Race Results for {rider_name}"
        else:
            info += f"One-Day Race Results for Rider ID {rider_id}"
        
        if year:
            info += f" ({year})"
        info += ":\n\n"
        
        # Check if we need to use standard parsing or direct HTML parsing
        if hasattr(one_day_results, 'results_df') and not (one_day_results.results_df is None or one_day_results.results_df.empty):
            # Use standard parsing
            results_df = one_day_results.results_df
            
            # Filter by year if specified
            if year:
                results_df = results_df[results_df['Year'] == year]
            
            # Sort by date (most recent first)
            if 'Date' in results_df.columns:
                results_df = results_df.sort_values('Date', ascending=False)
            elif 'Year' in results_df.columns:
                results_df = results_df.sort_values('Year', ascending=False)
            
            # Group by year
            if 'Year' in results_df.columns:
                for year_val in results_df['Year'].unique():
                    year_data = results_df[results_df['Year'] == year_val]
                    info += f"{year_val}:\n"
                    
                    for _, row in year_data.iterrows():
                        date = row.get('Date', 'N/A')
                        race = row.get('Race', 'N/A')
                        pos = row.get('Pos', 'N/A')
                        category = row.get('CAT', 'N/A')
                        time = row.get('Time', '')
                        
                        result_line = f"  {date} - {race}"
                        if category and category != 'N/A':
                            result_line += f" ({category})"
                        result_line += f": {pos}"
                        if time:
                            result_line += f" - {time}"
                        info += result_line + "\n"
                    
                    info += "\n"
            else:
                # If no Year column, just list all results
                for _, row in results_df.iterrows():
                    date = row.get('Date', 'N/A')
                    race = row.get('Race', 'N/A')
                    pos = row.get('Pos', 'N/A')
                    category = row.get('CAT', 'N/A')
                    time = row.get('Time', '')
                    
                    result_line = f"  {date} - {race}"
                    if category and category != 'N/A':
                        result_line += f" ({category})"
                    result_line += f": {pos}"
                    if time:
                        result_line += f" - {time}"
                    info += result_line + "\n"
        else:
            # Direct HTML parsing
            if not hasattr(one_day_results, 'soup') or not one_day_results.soup:
                return f"No one-day race results found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = one_day_results.soup
            
            # Find one-day races table
            tables = soup.find_all('table')
            races_table = None
            
            # Look for the table with one-day race results
            # Usually has headers like Date, Race, Position, etc.
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and (("Date" in headers or "Race" in headers) and "Pos" in headers):
                    races_table = table
                    break
            
            if not races_table:
                return f"Could not find one-day race results table for rider ID {rider_id}."
            
            # Parse race data
            rows = races_table.find_all('tr')
            race_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            date_idx = next((i for i, h in enumerate(headers) if "Date" in h), None)
            race_idx = next((i for i, h in enumerate(headers) if "Race" in h), None)
            pos_idx = next((i for i, h in enumerate(headers) if "Pos" in h), None)
            cat_idx = next((i for i, h in enumerate(headers) if "CAT" in h), None)
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:  # Ensure it's a data row
                    continue
                
                # Extract data
                date_text = cols[date_idx].text.strip() if date_idx is not None and date_idx < len(cols) else "N/A"
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                pos_text = cols[pos_idx].text.strip() if pos_idx is not None and pos_idx < len(cols) else "N/A"
                cat_text = cols[cat_idx].text.strip() if cat_idx is not None and cat_idx < len(cols) else "N/A"
                
                # Extract year from date (format may vary, but often includes year)
                race_year = None
                if date_text != "N/A":
                    # Try common date formats to extract year
                    if len(date_text) >= 4:
                        try:
                            # If year is last part (e.g., "01.01.2023")
                            race_year = int(date_text[-4:])
                        except:
                            # If year is first part (e.g., "2023-01-01")
                            try:
                                race_year = int(date_text[:4])
                            except:
                                pass
                
                if race_year:
                    # Skip if a specific year was requested and this race is from a different year
                    if year and race_year != year:
                        continue
                    
                    race_data.append({
                        'Year': race_year,
                        'Date': date_text,
                        'Race': race_text,
                        'Pos': pos_text,
                        'CAT': cat_text
                    })
            
            # Group by year
            year_grouped = {}
            for race in race_data:
                year_val = race['Year']
                if year_val not in year_grouped:
                    year_grouped[year_val] = []
                year_grouped[year_val].append(race)
            
            # Sort years (most recent first)
            for year_val in sorted(year_grouped.keys(), reverse=True):
                races = year_grouped[year_val]
                info += f"{year_val}:\n"
                
                for race in races:
                    result_line = f"  {race['Date']} - {race['Race']}"
                    if race['CAT'] and race['CAT'] != 'N/A':
                        result_line += f" ({race['CAT']})"
                    result_line += f": {race['Pos']}"
                    info += result_line + "\n"
                
                info += "\n"
            
            if not race_data:
                info += "No one-day race results found for this rider.\n"
        
        return info
    except Exception as e:
        return f"Error retrieving one-day race results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get a rider's results in multi-day stage races, optionally filtered by year.
    This tool provides detailed information about a professional cyclist's performance in stage races,
    which are cycling competitions that take place over multiple days with different stages. It includes
    overall classifications, stage results, and special achievements in these events.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get stage race results for Tadej Pogačar (ID: 16973)
    - Get 2023 stage race results for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Results organized by year
    - Race name, date, and category
    - Overall position and time
    - Notable stage results
    - Comprehensive list of all stage race participations"""
)
async def get_rider_stage_races(rider_id: int, year: int = None) -> str:
    """Get a rider's results in multi-day stage races, optionally filtered by year.

    This tool provides detailed information about a professional cyclist's performance in stage races,
    which are cycling competitions that take place over multiple days with different stages. It includes
    overall classifications, stage results, and special achievements in these events.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.

    Returns:
        str: A formatted string containing the rider's stage race results, including:
             - Race name and date
             - Overall position and time
             - Notable stage results
             - Results organized by year
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get stage races results
        stage_results = rider.stage_races()
        
        # Build information string
        info = ""
        
        # Get rider name
        rider_name = None
        if hasattr(stage_results, 'header_details') and stage_results.header_details and 'name' in stage_results.header_details:
            rider_name = stage_results.header_details['name']
        else:
            # Try to extract rider name from page title
            if hasattr(stage_results, 'soup') and stage_results.soup:
                title = stage_results.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
        
        # Format title
        if rider_name:
            info += f"Stage Race Results for {rider_name}"
        else:
            info += f"Stage Race Results for Rider ID {rider_id}"
        
        if year:
            info += f" ({year})"
        info += ":\n\n"
        
        # Check if we need to use standard parsing or direct HTML parsing
        if hasattr(stage_results, 'results_df') and not (stage_results.results_df is None or stage_results.results_df.empty):
            # Use standard parsing
            results_df = stage_results.results_df
            
            # Filter by year if specified
            if year:
                results_df = results_df[results_df['Year'] == year]
            
            # Sort by date (most recent first)
            if 'Date' in results_df.columns:
                results_df = results_df.sort_values('Date', ascending=False)
            elif 'Year' in results_df.columns:
                results_df = results_df.sort_values('Year', ascending=False)
            
            # Group by year
            if 'Year' in results_df.columns:
                for year_val in results_df['Year'].unique():
                    year_data = results_df[results_df['Year'] == year_val]
                    info += f"{year_val}:\n"
                    
                    for _, row in year_data.iterrows():
                        date = row.get('Date', 'N/A')
                        race = row.get('Race', 'N/A')
                        pos = row.get('Pos', 'N/A')
                        category = row.get('CAT', 'N/A')
                        time = row.get('Time', '')
                        
                        result_line = f"  {date} - {race}"
                        if category and category != 'N/A':
                            result_line += f" ({category})"
                        result_line += f": {pos}"
                        if time:
                            result_line += f" - {time}"
                        info += result_line + "\n"
                    
                    info += "\n"
            else:
                # If no Year column, just list all results
                for _, row in results_df.iterrows():
                    date = row.get('Date', 'N/A')
                    race = row.get('Race', 'N/A')
                    pos = row.get('Pos', 'N/A')
                    category = row.get('CAT', 'N/A')
                    time = row.get('Time', '')
                    
                    result_line = f"  {date} - {race}"
                    if category and category != 'N/A':
                        result_line += f" ({category})"
                    result_line += f": {pos}"
                    if time:
                        result_line += f" - {time}"
                    info += result_line + "\n"
        else:
            # Direct HTML parsing
            if not hasattr(stage_results, 'soup') or not stage_results.soup:
                return f"No stage race results found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = stage_results.soup
            
            # Find stage races table
            tables = soup.find_all('table')
            races_table = None
            
            # Look for the table with stage race results
            # Usually has headers like Date, Race, Position, etc.
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and (("Date" in headers or "Race" in headers) and "Pos" in headers):
                    races_table = table
                    break
            
            if not races_table:
                return f"Could not find stage race results table for rider ID {rider_id}."
            
            # Parse race data
            rows = races_table.find_all('tr')
            race_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            date_idx = next((i for i, h in enumerate(headers) if "Date" in h), None)
            race_idx = next((i for i, h in enumerate(headers) if "Race" in h), None)
            pos_idx = next((i for i, h in enumerate(headers) if "Pos" in h), None)
            cat_idx = next((i for i, h in enumerate(headers) if "CAT" in h), None)
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:  # Ensure it's a data row
                    continue
                
                # Extract data
                date_text = cols[date_idx].text.strip() if date_idx is not None and date_idx < len(cols) else "N/A"
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                pos_text = cols[pos_idx].text.strip() if pos_idx is not None and pos_idx < len(cols) else "N/A"
                cat_text = cols[cat_idx].text.strip() if cat_idx is not None and cat_idx < len(cols) else "N/A"
                
                # Extract year from date (format may vary, but often includes year)
                race_year = None
                if date_text != "N/A":
                    # Try common date formats to extract year
                    if len(date_text) >= 4:
                        try:
                            # If year is last part (e.g., "01.01.2023")
                            race_year = int(date_text[-4:])
                        except:
                            # If year is first part (e.g., "2023-01-01")
                            try:
                                race_year = int(date_text[:4])
                            except:
                                pass
                
                if race_year:
                    # Skip if a specific year was requested and this race is from a different year
                    if year and race_year != year:
                        continue
                    
                    race_data.append({
                        'Year': race_year,
                        'Date': date_text,
                        'Race': race_text,
                        'Pos': pos_text,
                        'CAT': cat_text
                    })
            
            # Group by year
            year_grouped = {}
            for race in race_data:
                year_val = race['Year']
                if year_val not in year_grouped:
                    year_grouped[year_val] = []
                year_grouped[year_val].append(race)
            
            # Sort years (most recent first)
            for year_val in sorted(year_grouped.keys(), reverse=True):
                races = year_grouped[year_val]
                info += f"{year_val}:\n"
                
                for race in races:
                    result_line = f"  {race['Date']} - {race['Race']}"
                    if race['CAT'] and race['CAT'] != 'N/A':
                        result_line += f" ({race['CAT']})"
                    result_line += f": {race['Pos']}"
                    info += result_line + "\n"
                
                info += "\n"
            
            if not race_data:
                info += "No stage race results found for this rider.\n"
        
        return info
    except Exception as e:
        return f"Error retrieving stage race results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Retrieve the complete team history of a rider throughout their career. This tool provides 
    a chronological list of all teams a rider has been a part of, including the years they rode for each team.
    It helps track a cyclist's career progression through different teams.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get team history for Tadej Pogačar (ID: 16973)
    - Get team history for Mathieu van der Poel (ID: 16975)
    
    Returns a formatted string with:
    - Complete chronological list of teams
    - Years with each team
    - Current team affiliation
    - Career timeline overview"""
)
async def get_rider_teams(rider_id: int) -> str:
    """Retrieve the complete team history of a rider throughout their career.

    This tool provides a chronological list of all teams a rider has been a part of, 
    including the years they rode for each team. It helps track a cyclist's career progression 
    through different teams.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)

    Returns:
        str: A formatted string containing the rider's team history:
             - Team names with years of affiliation
             - Current team highlighted
             - Complete chronological progression
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get teams information
        teams = rider.teams()
        
        # Build information string
        info = ""
        
        # Get rider name
        rider_name = None
        if hasattr(teams, 'header_details') and teams.header_details and 'name' in teams.header_details:
            rider_name = teams.header_details['name']
        else:
            # Try to extract rider name from page title
            if hasattr(teams, 'soup') and teams.soup:
                title = teams.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
        
        # Format title
        if rider_name:
            info += f"Team History for {rider_name}:\n\n"
        else:
            info += f"Team History for Rider ID {rider_id}:\n\n"
        
        # Check if we need to use standard parsing or direct HTML parsing
        if hasattr(teams, 'results_df') and not (teams.results_df is None or teams.results_df.empty):
            # Use standard parsing
            results_df = teams.results_df
            
            # Sort by year (most recent first)
            if 'Year' in results_df.columns:
                results_df = results_df.sort_values('Year', ascending=False)
            
            # List teams by year
            for _, row in results_df.iterrows():
                year = row.get('Year', 'N/A')
                team = row.get('Team', 'N/A')
                info += f"{year}: {team}\n"
        else:
            # Direct HTML parsing
            if not hasattr(teams, 'soup') or not teams.soup:
                return f"No team history found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = teams.soup
            
            # Find teams table
            tables = soup.find_all('table')
            teams_table = None
            
            # Look for the table with team history
            # Usually has headers like Year, Team, etc.
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 2 and "Year" in headers and "Team" in headers:
                    teams_table = table
                    break
            
            if not teams_table:
                return f"Could not find team history table for rider ID {rider_id}."
            
            # Parse team data
            rows = teams_table.find_all('tr')
            team_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            year_idx = next((i for i, h in enumerate(headers) if "Year" in h), None)
            team_idx = next((i for i, h in enumerate(headers) if "Team" in h), None)
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 2:  # Ensure it's a data row
                    continue
                
                # Extract data
                year_text = cols[year_idx].text.strip() if year_idx is not None and year_idx < len(cols) else "N/A"
                
                # Extract team (might be in a link)
                team_col = cols[team_idx] if team_idx is not None and team_idx < len(cols) else None
                if team_col:
                    team_link = team_col.find('a')
                    team_text = team_link.text.strip() if team_link else team_col.text.strip()
                else:
                    team_text = "N/A"
                
                team_data.append({
                    'Year': year_text,
                    'Team': team_text
                })
            
            # Sort by year (most recent first)
            team_data.sort(key=lambda x: x['Year'], reverse=True)
            
            # Build the information string
            for team in team_data:
                info += f"{team['Year']}: {team['Team']}\n"
            
            if not team_data:
                info += "No team history found for this rider.\n"
        
        return info
    except Exception as e:
        return f"Error retrieving team history for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get a list of a rider's career victories, with optional filters for WorldTour or UCI races.
    This tool provides comprehensive information about all races a professional cyclist has won throughout 
    their career. It includes race details, dates, and categories of victories, offering insights into 
    the rider's achievements and specialties.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get all victories for Tadej Pogačar (ID: 16973)
    - Get UCI victories for Mathieu van der Poel (ID: 16975)
    - Get WorldTour victories for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - List of all career victories
    - Race details, dates, and categories
    - Optional filtering for WorldTour or UCI races
    - Count of total victories by type"""
)
async def get_rider_victories(rider_id: int, world_tour: bool = False, uci: bool = False) -> str:
    """Get a list of a rider's career victories, with optional filters for WorldTour or UCI races.

    This tool provides comprehensive information about all races a professional cyclist has won throughout 
    their career. It includes race details, dates, and categories of victories, offering insights into 
    the rider's achievements and specialties.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        world_tour: If True, only include WorldTour victories
        uci: If True, only include UCI-classified victories

    Returns:
        str: A formatted string containing the rider's victories:
             - Race names, dates, and categories
             - Classification by race type and importance
             - Total count of victories
    """
    try:
        # Create a rider instance
        rider = Rider(rider_id)
        
        # Get victories information
        victories = rider.victories(world_tour=world_tour, uci=uci)
        
        # Build information string
        info = ""
        
        # Get rider name
        rider_name = None
        if hasattr(victories, 'header_details') and victories.header_details and 'name' in victories.header_details:
            rider_name = victories.header_details['name']
        else:
            # Try to extract rider name from page title
            if hasattr(victories, 'soup') and victories.soup:
                title = victories.soup.find('title')
                if title and '|' in title.text:
                    rider_name = title.text.split('|')[0].strip()
        
        # Format title based on filter options
        if rider_name:
            info += f"Victories for {rider_name}"
        else:
            info += f"Victories for Rider ID {rider_id}"
        
        if world_tour:
            info += " (WorldTour races only)"
        elif uci:
            info += " (UCI races only)"
        info += ":\n\n"
        
        # Check if we need to use standard parsing or direct HTML parsing
        if hasattr(victories, 'results_df') and not (victories.results_df is None or victories.results_df.empty):
            # Use standard parsing
            results_df = victories.results_df
            
            # Sort by date (most recent first)
            if 'Date' in results_df.columns:
                results_df = results_df.sort_values('Date', ascending=False)
            elif 'Year' in results_df.columns:
                results_df = results_df.sort_values('Year', ascending=False)
            
            # Group by year if available
            if 'Year' in results_df.columns:
                for year in results_df['Year'].unique():
                    year_data = results_df[results_df['Year'] == year]
                    info += f"{year}:\n"
                    
                    for _, row in year_data.iterrows():
                        date = row.get('Date', 'N/A')
                        race = row.get('Race', 'N/A')
                        category = row.get('CAT', 'N/A')
                        
                        result_line = f"  {date} - {race}"
                        if category and category != 'N/A':
                            result_line += f" ({category})"
                        info += result_line + "\n"
                    
                    info += "\n"
            else:
                # If no Year column, just list all victories
                for _, row in results_df.iterrows():
                    date = row.get('Date', 'N/A')
                    race = row.get('Race', 'N/A')
                    category = row.get('CAT', 'N/A')
                    
                    result_line = f"  {date} - {race}"
                    if category and category != 'N/A':
                        result_line += f" ({category})"
                    info += result_line + "\n"
            
            # Add total count
            info += f"\nTotal victories: {len(results_df)}\n"
        else:
            # Direct HTML parsing
            if not hasattr(victories, 'soup') or not victories.soup:
                return f"No victories found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = victories.soup
            
            # Find victories table
            tables = soup.find_all('table')
            victories_table = None
            
            # Look for the table with victories
            # Usually has headers like Date, Race, Category, etc.
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 2 and (("Date" in headers or "Race" in headers)):
                    victories_table = table
                    break
            
            if not victories_table:
                return f"Could not find victories table for rider ID {rider_id}."
            
            # Parse victory data
            rows = victories_table.find_all('tr')
            victory_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            date_idx = next((i for i, h in enumerate(headers) if "Date" in h), None)
            race_idx = next((i for i, h in enumerate(headers) if "Race" in h), None)
            cat_idx = next((i for i, h in enumerate(headers) if "CAT" in h), None)
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 2:  # Ensure it's a data row
                    continue
                
                # Extract data
                date_text = cols[date_idx].text.strip() if date_idx is not None and date_idx < len(cols) else "N/A"
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                cat_text = cols[cat_idx].text.strip() if cat_idx is not None and cat_idx < len(cols) else "N/A"
                
                # Extract year from date (format may vary, but often includes year)
                victory_year = None
                if date_text != "N/A":
                    # Try common date formats to extract year
                    if len(date_text) >= 4:
                        try:
                            # If year is last part (e.g., "01.01.2023")
                            victory_year = date_text[-4:]
                        except:
                            # If year is first part (e.g., "2023-01-01")
                            try:
                                victory_year = date_text[:4]
                            except:
                                pass
                
                # Apply filters if needed
                if world_tour and not (cat_text and "UWT" in cat_text):
                    continue
                
                if uci and not (cat_text and any(c in cat_text for c in ["UWT", "1.", "2.", "CC", "WC"])):
                    continue
                
                victory_data.append({
                    'Year': victory_year or "Unknown",
                    'Date': date_text,
                    'Race': race_text,
                    'CAT': cat_text
                })
            
            # Group by year
            year_grouped = {}
            for victory in victory_data:
                year_val = victory['Year']
                if year_val not in year_grouped:
                    year_grouped[year_val] = []
                year_grouped[year_val].append(victory)
            
            # Sort years (most recent first)
            for year_val in sorted(year_grouped.keys(), reverse=True):
                victories_list = year_grouped[year_val]
                info += f"{year_val}:\n"
                
                for victory in victories_list:
                    result_line = f"  {victory['Date']} - {victory['Race']}"
                    if victory['CAT'] and victory['CAT'] != 'N/A':
                        result_line += f" ({victory['CAT']})"
                    info += result_line + "\n"
                
                info += "\n"
            
            # Add total count
            info += f"Total victories: {len(victory_data)}\n"
            
            if not victory_data:
                info += "No victories found for this rider with the specified filters.\n"
        
        return info
    except Exception as e:
        return f"Error retrieving victories for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 