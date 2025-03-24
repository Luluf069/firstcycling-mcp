#!/usr/bin/env python3
"""
Example script for getting a rider's best results using the FirstCycling API
"""

import sys
import os
# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from first_cycling_api.rider.rider import Rider
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

def get_rider_best_results(rider_id, debug=False):
    """Get a rider's best results from FirstCycling"""
    # Create rider instance
    rider = Rider(rider_id)
    
    # Get basic rider info
    print(f"Rider ID: {rider.ID}")

    # Debug information if enabled
    if debug:
        # Debug: Check the URL directly
        url = f"https://firstcycling.com/rider.php?r={rider_id}&high=1"
        print(f"Checking URL: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Check for tables
        tables = soup.find_all('table', {'class': 'tablesorter'})
        print(f"Found {len(tables)} tables with class 'tablesorter'")
        
        if tables:
            # Check the first table
            first_table = tables[0]
            rows = first_table.find_all('tr')
            print(f"First table has {len(rows)} rows")
            
            if len(rows) > 1:  # Header row + at least one data row
                # Try to parse directly
                try:
                    print("Table content preview:")
                    for i, row in enumerate(rows[:3]):  # Show first 3 rows
                        print(f"Row {i}: {row.get_text().strip()}")
                    
                    # Try direct pandas parsing
                    df = pd.read_html(io.StringIO(str(first_table)), decimal=',')[0]
                    print(f"Successfully parsed table with shape: {df.shape}")
                    print("Column names:", df.columns.tolist())
                    print("First few rows:")
                    print(df.head(3))
                except Exception as e:
                    print(f"Error parsing table directly: {str(e)}")
            else:
                print("Table appears to be empty or has only a header row")
    
    # Get best results
    best_results = rider.best_results()
    
    # Display information about best results
    if hasattr(best_results, 'results_df') and not best_results.results_df.empty:
        print(f"\nFound {len(best_results.results_df)} best results:")
        
        # Display the first 10 best results (or all if less than 10)
        print("\nTop 10 best results:")
        limit = min(10, len(best_results.results_df))
        for i, (_, row) in enumerate(best_results.results_df.head(limit).iterrows(), 1):
            race = row.get('Race', 'Unknown Race')
            pos = row.get('Pos', 'N/A')
            editions = row.get('Editions', '')
            cat = row.get('CAT', '')
            country = row.get('Race_Country', '')
            
            result_line = f"{i}. {pos}. {race}"
            if cat:
                result_line += f" ({cat})"
            if editions:
                result_line += f" - {editions}"
            if country:
                result_line += f" - {country}"
                
            print(result_line)
    else:
        print("No best results found for this rider.")

if __name__ == "__main__":
    # Use Mathieu van der Poel (ID: 16672) as the default example
    rider_id = 16672
    debug_mode = False
    
    # Parse command-line arguments
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--debug":
            debug_mode = True
        elif i == 0:  # First non-flag argument is rider ID
            try:
                rider_id = int(arg)
            except ValueError:
                print(f"Invalid rider ID: {arg}")
                sys.exit(1)
    
    get_rider_best_results(rider_id, debug=debug_mode) 