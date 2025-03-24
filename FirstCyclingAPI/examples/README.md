# FirstCycling API Examples

This directory contains example scripts demonstrating how to use the FirstCycling API package.

## Available Examples

### Rider Victories (`rider_victories.py`)

This script demonstrates how to fetch and analyze a rider's career victories.

**Usage:**
```
python rider_victories.py [rider_id] [--debug]
```

If no rider ID is provided, it defaults to Mathieu van der Poel (ID: 16672).

**Example Output:**
```
Rider ID: 16672

Found 286 career victories:

Victories by year:
2012: 7 wins
2013: 23 wins
...

Victories by category:
CX: C1: 77
CX: CDM: 49
...

Most recent 10 victories:
2025-03-22: Milano-Sanremo (1.UWT)
2025-03-04: Le Samyn (1.1)
...
```

**Notes on Data Availability:**
- Some riders may show "No victories found" even if they are successful riders. The FirstCycling website data is not always complete or may be structured differently for some riders.
- If you encounter issues with a specific rider, you can use the `--debug` flag to see more details about what's being retrieved.

## Running Examples

To run the examples:

1. Make sure you're in the FirstCyclingAPI directory
2. Run the example script with Python 3:
   ```
   python3 examples/rider_victories.py
   ```

## Finding Rider IDs

Rider IDs can be found in the URL of a rider's profile on FirstCycling.com. For example:
- Mathieu van der Poel: https://firstcycling.com/rider.php?r=16672 (ID: 16672)
- Tadej Pogačar: https://firstcycling.com/rider.php?r=25026 (ID: 25026)
- Wout van Aert: https://firstcycling.com/rider.php?r=16276 (ID: 16276)
- Peter Sagan: https://firstcycling.com/rider.php?r=9593 (ID: 9593) 