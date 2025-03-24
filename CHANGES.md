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