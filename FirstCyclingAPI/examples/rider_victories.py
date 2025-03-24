#!/usr/bin/env python3
"""
Example script for getting a rider's victories using the FirstCycling API
"""

import sys
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# Add the parent directory to the Python path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from first_cycling_api.rider.rider import Rider

def get_rider_victories(rider_id, debug=False):
    """Get a rider's victories from FirstCycling"""
    rider = Rider(rider_id)
    
    # Get basic rider info
    print(f"Rider ID: {rider.ID}")
    
    if debug:
        # Direct check of the victories page for debugging
        url = f"https://firstcycling.com/rider.php?r={rider_id}&high=1&k=1"
        print(f"Directly checking URL: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for tables
        tables = soup.find_all('table', {'class': "sortTabell tablesorter"})
        print(f"Found {len(tables)} tables with class 'sortTabell tablesorter'")
        
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
    
    # Get all victories using the API
    victories = rider.victories()
    
    # Display information about victories
    if hasattr(victories, 'results_df') and not victories.results_df.empty:
        print(f"\nFound {len(victories.results_df)} career victories:")
        
        # Group by year to count victories per year
        victories_by_year = victories.results_df.groupby('Year').size()
        print("\nVictories by year:")
        for year, count in victories_by_year.items():
            print(f"{year}: {count} wins")
        
        # Check for specific race categories
        if 'CAT' in victories.results_df.columns:
            categories = victories.results_df['CAT'].value_counts()
            print("\nVictories by category:")
            for category, count in categories.items():
                print(f"{category}: {count}")
                
        # Display the first 10 victories
        print("\nMost recent 10 victories:")
        # Sort by date (newest first) and show the first 10
        if 'Date_Formatted' in victories.results_df.columns:
            recent_victories = victories.results_df.sort_values('Date_Formatted', ascending=False).head(10)
            # Display in a readable format
            for _, row in recent_victories.iterrows():
                print(f"{row['Date_Formatted']}: {row['Race']} ({row['CAT']})")
    else:
        print("No victories found for this rider.")

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
    
    get_rider_victories(rider_id, debug=debug_mode) 