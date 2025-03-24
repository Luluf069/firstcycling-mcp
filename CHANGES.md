# Changes to FirstCycling API

## Fix for Rider Victories Endpoint

### Issue
The `victories` method in the `Rider` class was not properly retrieving riders' victories data from FirstCycling.com. The method was returning a generic `RiderEndpoint` object without properly parsing the victories table.

### Changes Made

1. Created a new `RiderVictories` class that extends `RiderEndpoint` to specifically handle the victories data format
2. Updated the `victories` method to use the new `RiderVictories` class
3. Added robust parsing of the victories table, including:
   - Proper handling of "No data" responses
   - Better date formatting (combining year and date information)
   - Error handling for column mismatches and other parsing issues
4. Fixed an issue in the `parse_table` function to properly handle tables with "No data" content
5. Added a StringIO wrapper to pandas.read_html to fix FutureWarning deprecation notices
6. Added a debug mode to the example script to help diagnose issues

### Example Usage
```python
from first_cycling_api.rider.rider import Rider

# Initialize a rider by ID
rider = Rider(16672)  # Mathieu van der Poel

# Get victories
victories = rider.victories()

# Access the victories data
if hasattr(victories, 'results_df') and not victories.results_df.empty:
    print(f"Found {len(victories.results_df)} victories")
    print(victories.results_df)
else:
    print("No victories found for this rider")
```

### Known Limitations
- The victories endpoint appears to return "No data" for some riders like Tadej Pogačar and Wout van Aert on FirstCycling.com, even though they are successful riders with many victories. This appears to be a limitation of the data source rather than the API implementation.
- The date formatting is based on assumptions about the data format and may not be correct for all riders.

## API Enhancements

### 1. Rider Victories

- Added new `RiderVictories` class extending `RiderEndpoint`
- Updated `victories` method to use the new class
- Enhanced parsing of the victories table, including:
  - Handling "No data" responses
  - Improved date formatting
  - Error handling for column mismatches
- Fixed `parse_table` function to handle tables with "No data" content
- Added StringIO wrapper to `pandas.read_html` to resolve FutureWarning issues

Example usage:
```python
rider = Rider(16672)  # Mathieu van der Poel
victories = rider.victories()
if not victories.results_df.empty:
    print(f"Found {len(victories.results_df)} victories")
else:
    print("No victories found")
```

Known limitations:
- Some rider pages on FirstCycling show "No data" for victories even for riders who have career wins
- Date formatting assumes YYYY-MM-DD format
- Some date fields might be formatted as strings, others as numeric values

### 2. Rider Best Results

- Added new `RiderBestResults` class extending `RiderEndpoint`
- Updated `best_results` method to use the new class
- Implemented custom parsing for the best results table which has a different structure
- Added proper error handling for:
  - Empty tables
  - "No data" responses
  - Tables with unexpected formats
- Created an example script (`examples/rider_best_results.py`) to demonstrate usage

Example usage:
```python
rider = Rider(16672)  # Mathieu van der Poel
best_results = rider.best_results()
if not best_results.results_df.empty:
    print(f"Found {len(best_results.results_df)} best results")
    # Access specific data
    for _, row in best_results.results_df.head(3).iterrows():
        print(f"{row['Pos']}. {row['Race']} - {row['Editions']}")
else:
    print("No best results found")
```

Key differences in the best results table:
- Uses class 'tablesorter' instead of 'sortTabell tablesorter'
- Contains an 'Editions' column showing years of achievements
- No date column, focuses on position and race name 