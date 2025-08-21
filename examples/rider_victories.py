#!/usr/bin/env python3
"""
Example script for getting a rider's victories using the FirstCycling API
"""

from first_cycling_api.rider.rider import Rider
import pandas as pd
import sys

def get_rider_victories(rpip install pandaspip install pandaspip install pandaspip install pandasider_id):
    """Get a rider's victories from FirstCycling"""
    rider = Rider(rider_id)
    
    # Get basic rider info
    print(f"Rider ID: {rider.ID}")
    
    # Get all victories
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
    
    # Allow command-line argument for rider ID
    if len(sys.argv) > 1:
        try:
            rider_id = int(sys.argv[1])
        except ValueError:
            print(f"Invalid rider ID: {sys.argv[1]}")
            sys.exit(1)
    
    get_rider_victories(rider_id) 