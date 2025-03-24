# FirstCycling API Examples

This directory contains example scripts that demonstrate how to use the FirstCycling API.

## Available Examples

### 1. `rider_victories.py`

This script demonstrates how to retrieve a rider's career victories using the API.

#### Usage:

```bash
python rider_victories.py [rider_id] [--debug]
```

Where:
- `rider_id` is the unique ID of the rider on FirstCycling.com (e.g., 16672 for Mathieu van der Poel)
- `--debug` is an optional flag to print debug information

#### Example Output:

```
Rider ID: 16672
Found 43 career victories:

Victories by year:
2024: 4 wins
2023: 9 wins
...

Victories by category:
1.UWT: 19
NC: 5
...

Most recent 10 victories:
2024-03-09: Milano-Sanremo (1.UWT)
2024-03-02: Strade Bianche (1.UWT)
...
```

### 2. `rider_best_results.py`

This script demonstrates how to retrieve a rider's best career results using the API.

#### Usage:

```bash
python rider_best_results.py [rider_id] [--debug]
```

Where:
- `rider_id` is the unique ID of the rider on FirstCycling.com (e.g., 16672 for Mathieu van der Poel)
- `--debug` is an optional flag to print debug information

#### Example Output:

```
Rider ID: 16672
Found 7 best results:

Top 10 best results:
1. 1st. Ronde van Vlaanderen - 20', 22', 24'
2. 1st. Paris-Roubaix - 23', 24'
3. 1st. Milano-Sanremo - 23', 25'
4. 1st. World Championship RR - 23'
5. 1st. Renewi Tour - 20'
6. 1st. Dwars door Vlaanderen - 19', 22'
7. 1st. Tour de France | 1 Stage
```

## Notes on Data Availability

- Some riders may show "No victories found" or "No best results found" due to incomplete data on the FirstCycling website.
- You can use the `--debug` flag to get more information about what data is being returned from the API.

## How to Run the Examples

1. Make sure you have installed the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run an example script:
   ```bash
   python rider_victories.py 16672
   ```

## Finding Rider IDs

The rider ID can be found in the URL of the rider's profile on FirstCycling.com.

Examples:
- Mathieu van der Poel: https://firstcycling.com/rider.php?r=16672
- Tadej Pogačar: https://firstcycling.com/rider.php?r=25026
- Wout van Aert: https://firstcycling.com/rider.php?r=16276 