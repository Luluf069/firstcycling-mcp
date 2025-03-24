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
import re

# Add the FirstCyclingAPI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "FirstCyclingAPI"))

# Import from the FirstCycling API
from first_cycling_api.rider.rider import Rider
from first_cycling_api.race.race import RaceEdition

# Initialize FastMCP server
mcp = FastMCP("firstcycling")

@mcp.tool(
    description="""Search for professional cyclists by name. This tool helps find riders by their name, 
    returning a list of matching riders with their IDs and basic information. This is useful when you need 
    a rider's ID for other operations but only know their name.
    
    Example usage:
    - Search for "Tadej Pogacar" to find Tadej Pogačar's ID
    - Search for "Van Aert" to find Wout van Aert's ID
    
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
             - Rider name
             - Nationality
             - Current team
    """
    try:
        # Search for riders using the Rider.search method
        riders = Rider.search(query)
        
        if not riders:
            return f"No riders found matching the query '{query}'."
        
        # Build results string
        info = f"Found {len(riders)} riders matching '{query}':\n\n"
        
        for rider in riders:
            info += f"ID: {rider['id']}\n"
            info += f"Name: {rider['name']}\n"
            if rider.get('nationality'):
                info += f"Nationality: {rider['nationality'].upper()}\n"
            if rider.get('team'):
                info += f"Team: {rider['team']}\n"
            info += "\n"
        
        return info
    except Exception as e:
        return f"Error searching for riders: {str(e)}"

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
        
        # Use direct HTML parsing approach to handle cases where the regular parsing fails
        try:
            # Try to get rider year results using standard method
            year_results = rider.year_results()
            
            # Check if results exist
            if year_results is None or not hasattr(year_results, 'results_df') or year_results.results_df.empty:
                raise Exception("No results found using standard method")
            
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
            
        except Exception as parsing_error:
            # If standard parsing method fails, use direct HTML parsing
            # Get raw HTML for the rider page
            url = f"https://firstcycling.com/rider.php?r={rider_id}"
            response = requests.get(url)
            
            if response.status_code != 200:
                return f"Failed to retrieve data for rider ID {rider_id}. Status code: {response.status_code}"
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if the page indicates the rider doesn't exist
            if "not found" in soup.text.lower() or "no results found" in soup.text.lower():
                return f"Rider ID {rider_id} does not exist on FirstCycling.com."
            
            # Build rider information string
            info = ""
            
            # Get rider name from the heading
            name_element = soup.find('h1')
            if name_element:
                rider_name = name_element.text.strip()
                info += f"Name: {rider_name}\n"
            else:
                info += f"Rider ID: {rider_id}\n"
            
            # Get current team - typically in a div after the rider name
            team_element = soup.find('span', class_='blue')
            if team_element:
                team_name = team_element.text.strip()
                info += f"Team: {team_name}\n"
            
            # Try to find the sidebar details (nationality, birth date, etc.)
            sidebar = soup.find('div', class_='rp-info')
            if sidebar:
                detail_rows = sidebar.find_all('tr')
                for row in detail_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].text.strip().rstrip(':')
                        value = cells[1].text.strip()
                        if key and value:
                            info += f"{key}: {value}\n"
            
            # Try to find recent results
            tables = soup.find_all('table')
            results_table = None
            
            # Look for a table that has race results
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and ('Date' in headers or 'Race' in headers):
                    results_table = table
                    break
            
            if results_table:
                # Get the headers to identify column positions
                headers = [th.text.strip() for th in results_table.find_all('th')]
                date_idx = headers.index('Date') if 'Date' in headers else None
                race_idx = headers.index('Race') if 'Race' in headers else None
                pos_idx = headers.index('Pos') if 'Pos' in headers else None
                
                if date_idx is not None and race_idx is not None and pos_idx is not None:
                    # Extract up to 5 recent results
                    rows = results_table.find_all('tr')[1:6]  # Skip header row, take up to 5 rows
                    
                    if rows:
                        info += "\nRecent Results:\n"
                        for i, row in enumerate(rows):
                            cells = row.find_all('td')
                            if len(cells) > max(date_idx, race_idx, pos_idx):
                                date = cells[date_idx].text.strip()
                                race = cells[race_idx].text.strip()
                                pos = cells[pos_idx].text.strip()
                                info += f"{i+1}. {date} - {race}: {pos}\n"
            
            # Try to find victories count
            # This can be tricky with direct parsing, often in a different section
            victories_section = soup.find(text=lambda text: text and 'victories' in text.lower())
            if victories_section:
                # Try to extract the number from text like "X UCI victories"
                victory_text = victories_section.strip()
                victory_match = re.search(r'(\d+)\s+UCI\s+victories', victory_text, re.IGNORECASE)
                if victory_match:
                    victories_count = victory_match.group(1)
                    info += f"\nUCI Victories: {victories_count}\n"
            
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
                        except Exception:
                            # If year is first part (e.g., "2023-01-01")
                            try:
                                race_year = int(date_text[:4])
                            except Exception:
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
    This tool retrieves detailed information about a rider's performance in one-day races 
    (classics and one-day events). It provides comprehensive data about positions, times, 
    and race categories. Results can be filtered by a specific year.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get one-day race results for Mathieu van der Poel (ID: 16672)
    - Get 2023 one-day race results for Wout van Aert (ID: 16948)
    
    Returns a formatted string with:
    - Results in one-day races organized by year
    - Position and time for each race
    - Race category and details
    - Chronological organization"""
)
async def get_rider_one_day_races(rider_id: int, year: int = None) -> str:
    """Get a rider's results in one-day races, optionally filtered by year.

    This tool retrieves detailed information about a rider's performance in one-day races 
    (classics and one-day events). It provides comprehensive data about positions, times, 
    and race categories. Results can be filtered by a specific year.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16672 for Mathieu van der Poel)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.
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
            
            # Sort by year (most recent first)
            results_df = results_df.sort_values('Year', ascending=False)
            
            # Group by year
            for year_val in results_df['Year'].unique():
                year_data = results_df[results_df['Year'] == year_val]
                info += f"{year_val}:\n"
                
                # Sort by date within year
                year_data = year_data.sort_values('Date', ascending=False)
                
                for _, row in year_data.iterrows():
                    date = row.get('Date', 'N/A')
                    race = row.get('Race', 'N/A')
                    pos = row.get('Pos', 'N/A')
                    category = row.get('CAT', 'N/A')
                    
                    info += f"  {date} - {race} ({category}): {pos}\n"
                
                info += "\n"
        else:
            # Direct HTML parsing
            if not hasattr(one_day_results, 'soup') or not one_day_results.soup:
                return f"No one-day race results found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = one_day_results.soup
            
            # Find one-day races results table
            tables = soup.find_all('table')
            results_table = None
            
            # Look for the appropriate table that contains one-day races results
            for table in tables:
                # Check table headers to find the right one
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and "Race" in headers and ("Date" in headers or "Year" in headers):
                    results_table = table
                    break
            
            if not results_table:
                return f"Could not find one-day race results table for rider ID {rider_id}."
            
            # Parse one-day races data
            rows = results_table.find_all('tr')
            race_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            # Find the indices of key columns
            year_idx = next((i for i, h in enumerate(headers) if "Year" in h), None)
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
                race_year = cols[year_idx].text.strip() if year_idx is not None and year_idx < len(cols) else None
                
                # If we don't have a year column, try to extract from date
                if race_year is None and date_idx is not None and date_idx < len(cols):
                    date_text = cols[date_idx].text.strip()
                    # Try to extract year from date format (e.g., 01.01.2023 or 2023-01-01)
                    try:
                        if len(date_text) >= 4:
                            if date_text[-4:].isdigit():
                                race_year = date_text[-4:]
                            elif date_text[:4].isdigit():
                                race_year = date_text[:4]
                    except Exception:
                        pass
                
                # If we still don't have a year, use the next row
                if race_year is None or not race_year.isdigit():
                    continue
                
                # Convert year to int for comparison
                race_year_int = int(race_year)
                
                # Skip if a specific year was requested and this race is from a different year
                if year and race_year_int != year:
                    continue
                
                date_text = cols[date_idx].text.strip() if date_idx is not None and date_idx < len(cols) else "N/A"
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                pos_text = cols[pos_idx].text.strip() if pos_idx is not None and pos_idx < len(cols) else "N/A"
                cat_text = cols[cat_idx].text.strip() if cat_idx is not None and cat_idx < len(cols) else "N/A"
                
                race_data.append({
                    'Year': race_year_int,
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
                
                # Sort by date within year (can be complex due to different date formats)
                # For now, just display as is
                for race in races:
                    info += f"  {race['Date']} - {race['Race']} ({race['CAT']}): {race['Pos']}\n"
                
                info += "\n"
            
            if not race_data:
                info += "No one-day race results found for this rider.\n"
        
        return info
    except Exception as e:
        return f"Error retrieving one-day race results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

@mcp.tool(
    description="""Get a rider's results in stage races, optionally filtered by year.
    This tool retrieves detailed information about a rider's performance in stage races
    (multi-day races like Tour de France, Giro d'Italia, etc.). It provides comprehensive data 
    about positions, times, and race categories. Results can be filtered by a specific year.
    
    Note: If you don't know the rider's ID, use the search_rider tool first to find it by name.
    
    Example usage:
    - Get stage race results for Tadej Pogačar (ID: 16973)
    - Get 2023 stage race results for Jonas Vingegaard (ID: 16974)
    
    Returns a formatted string with:
    - Results in stage races organized by year
    - Position and time for each race
    - Race category and details
    - Chronological organization"""
)
async def get_rider_stage_races(rider_id: int, year: int = None) -> str:
    """Get a rider's results in stage races, optionally filtered by year.

    This tool retrieves detailed information about a rider's performance in stage races
    (multi-day races like Tour de France, Giro d'Italia, etc.). It provides comprehensive data 
    about positions, times, and race categories. Results can be filtered by a specific year.

    Args:
        rider_id: The FirstCycling rider ID (e.g., 16973 for Tadej Pogačar)
        year: Optional year to filter results (e.g., 2023). If not provided, returns all years.
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
            
            # Sort by year (most recent first)
            results_df = results_df.sort_values('Year', ascending=False)
            
            # Group by year
            for year_val in results_df['Year'].unique():
                year_data = results_df[results_df['Year'] == year_val]
                info += f"{year_val}:\n"
                
                # Sort by date within year
                year_data = year_data.sort_values('Date', ascending=False)
                
                for _, row in year_data.iterrows():
                    date = row.get('Date', 'N/A')
                    race = row.get('Race', 'N/A')
                    pos = row.get('Pos', 'N/A')
                    category = row.get('CAT', 'N/A')
                    
                    info += f"  {date} - {race} ({category}): {pos}\n"
                
                info += "\n"
        else:
            # Direct HTML parsing
            if not hasattr(stage_results, 'soup') or not stage_results.soup:
                return f"No stage race results found for rider ID {rider_id}. This rider ID may not exist."
            
            soup = stage_results.soup
            
            # Find stage races results table
            tables = soup.find_all('table')
            results_table = None
            
            # Look for the appropriate table that contains stage races results
            for table in tables:
                # Check table headers to find the right one
                headers = [th.text.strip() for th in table.find_all('th')]
                if len(headers) >= 3 and "Race" in headers and ("Date" in headers or "Year" in headers):
                    results_table = table
                    break
            
            if not results_table:
                return f"Could not find stage race results table for rider ID {rider_id}."
            
            # Parse stage races data
            rows = results_table.find_all('tr')
            race_data = []
            
            # Get column indices from header row
            headers = [th.text.strip() for th in rows[0].find_all('th')]
            
            # Find the indices of key columns
            year_idx = next((i for i, h in enumerate(headers) if "Year" in h), None)
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
                race_year = cols[year_idx].text.strip() if year_idx is not None and year_idx < len(cols) else None
                
                # If we don't have a year column, try to extract from date
                if race_year is None and date_idx is not None and date_idx < len(cols):
                    date_text = cols[date_idx].text.strip()
                    # Try to extract year from date format (e.g., 01.01.2023 or 2023-01-01)
                    try:
                        if len(date_text) >= 4:
                            if date_text[-4:].isdigit():
                                race_year = date_text[-4:]
                            elif date_text[:4].isdigit():
                                race_year = date_text[:4]
                    except Exception:
                        pass
                
                # If we still don't have a year, use the next row
                if race_year is None or not race_year.isdigit():
                    continue
                
                # Convert year to int for comparison
                race_year_int = int(race_year)
                
                # Skip if a specific year was requested and this race is from a different year
                if year and race_year_int != year:
                    continue
                
                date_text = cols[date_idx].text.strip() if date_idx is not None and date_idx < len(cols) else "N/A"
                race_text = cols[race_idx].text.strip() if race_idx is not None and race_idx < len(cols) else "N/A"
                pos_text = cols[pos_idx].text.strip() if pos_idx is not None and pos_idx < len(cols) else "N/A"
                cat_text = cols[cat_idx].text.strip() if cat_idx is not None and cat_idx < len(cols) else "N/A"
                
                race_data.append({
                    'Year': race_year_int,
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
                
                # Sort by date within year (can be complex due to different date formats)
                # For now, just display as is
                for race in races:
                    info += f"  {race['Date']} - {race['Race']} ({race['CAT']}): {race['Pos']}\n"
                
                info += "\n"
            
            if not race_data:
                info += "No stage race results found for this rider.\n"
        
        return info
    except Exception as e:
        return f"Error retrieving stage race results for rider ID {rider_id}: {str(e)}. The rider ID may not exist or there might be a connection issue."

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 