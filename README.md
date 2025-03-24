# FirstCycling MCP Server

This is a Model Context Protocol (MCP) server that provides professional cycling data from FirstCycling. It allows you to retrieve comprehensive information about professional cyclists, race results, race details, and historical cycling data.

## Features

This MCP server offers rich access to professional cycling data, providing tools for:

- Finding information about professional cyclists
- Retrieving race results and details
- Exploring historical race data
- Analyzing rider performance and career progression
- Accessing information about cycling teams and competitions

## Requirements

- Python 3.10 or higher
- `uv` package manager (recommended)
- Dependencies as listed in `pyproject.toml`, including:
  - mcp
  - beautifulsoup4
  - lxml
  - pandas
  - slumber
  - and other packages for web scraping and data processing

## Setup

1. Clone this repository
2. Create and activate a virtual environment:
   ```
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```
   uv pip install -e .
   ```

## FirstCycling API

This server uses the [FirstCycling API](https://github.com/Lsdefine/first-cycling-api), which has been integrated directly into the project. The API provides methods to fetch data from the FirstCycling website through web scraping.

### Common FirstCycling IDs

#### Riders

- Tadej Pogačar: 16973
- Jonas Vingegaard: 21527
- Remco Evenepoel: 23697
- Primož Roglič: 18655
- Mathieu van der Poel: 16672
- Wout van Aert: 19077

#### Races

- Tour de France: 17
- Giro d'Italia: 13
- Vuelta a España: 23
- Paris-Roubaix: 30
- Tour of Flanders: 29
- Milan-San Remo: 4
- Liège-Bastogne-Liège: 11
- Il Lombardia: 10

## MCP Tools

The server exposes the following tools through the Model Context Protocol:

### Rider Information

| Tool | Description |
|------|-------------|
| `get_rider_info` | Get basic biographical information about a rider including nationality, birthdate, weight, height, and current team |
| `get_rider_best_results` | Retrieve a rider's best career results, sorted by importance |
| `get_rider_grand_tour_results` | Get a rider's results in Grand Tours (Tour de France, Giro d'Italia, Vuelta a España) |
| `get_rider_monument_results` | Retrieve a rider's results in cycling's Monument classics |
| `get_rider_team_and_ranking` | Get a rider's team history and UCI ranking evolution over time |
| `get_rider_race_history` | Retrieve a rider's complete race participation history, optionally filtered by year |
| `get_rider_one_day_races` | Get a rider's results in one-day races, optionally filtered by year |
| `get_rider_stage_races` | Get a rider's results in multi-day stage races, optionally filtered by year |
| `get_rider_teams` | Retrieve the complete team history of a rider throughout their career |
| `get_rider_victories` | Get a list of a rider's career victories, with optional filters for WorldTour or UCI races |

### Race Information

| Tool | Description |
|------|-------------|
| `get_race_results` | Retrieve results for a specific race edition by race ID and year |
| `get_race_overview` | Get general information about a race including history, records, and past winners |
| `get_race_stage_profiles` | Retrieve stage profiles and details for multi-stage races |
| `get_race_startlist` | Get the startlist for a specific race edition with detailed or basic team information |
| `get_race_victory_table` | Retrieve the all-time victory table for a race showing riders with most wins |
| `get_race_year_by_year` | Get year-by-year results for a race with optional classification filter |
| `get_race_youngest_oldest_winners` | Retrieve information about the youngest and oldest winners of a race |
| `get_race_stage_victories` | Get information about stage victories in multi-stage races |

### Search Tools

| Tool | Description |
|------|-------------|
| `search_rider` | Search for riders by name, returning their IDs and basic information |
| `search_race` | Search for races by name, returning their IDs and basic information |

## Usage

### Development Mode

You can test the server with MCP Inspector by running:

```
uv run mcp dev firstcycling.py
```

This will start the server and open the MCP Inspector in your browser, allowing you to test the available tools.

### Integration with Claude for Desktop

To integrate this server with Claude for Desktop:

1. Edit the Claude for Desktop config file, located at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the server to your configuration:
   ```json
   {
     "mcpServers": {
       "firstcycling": {
         "command": "uv",
         "args": ["--directory", "/path/to/server/directory", "run", "firstcycling.py"]
       }
     }
   }
   ```

3. Restart Claude for Desktop

## Real-World Use Cases

With this MCP server, you can use Claude to:

### Rider Analysis

- **Performance Tracking**: "How has Tadej Pogačar performed in the Tour de France over the years? Use rider ID 16973."
- **Career Progression**: "Show me the team history and career progression of Wout van Aert (ID 19077)."
- **Specialization Analysis**: "What are Mathieu van der Poel's (ID 16672) results in Monument classics?"
- **Victory Analysis**: "List all WorldTour victories for Jonas Vingegaard (ID 21527)."
- **Historical Comparison**: "Compare the Grand Tour results of Primož Roglič (ID 18655) and Jonas Vingegaard (ID 21527)."

### Race Research

- **Recent Results**: "Show me the results of the 2023 Paris-Roubaix (race ID 30)."
- **Historical Context**: "Who are the youngest and oldest winners of the Tour of Flanders (ID 29)?"
- **Team Analysis**: "Get the startlist for the 2023 Tour de France (race ID 17) with detailed team information."
- **Race Statistics**: "Show me the victory table for Liège-Bastogne-Liège (ID 11). Who has won it the most times?"
- **Stage Information**: "Can you show me the stage profiles for the 2023 Giro d'Italia (race ID 13)?"

### Sports Journalism

- "Create a detailed profile of Remco Evenepoel (ID 23697) for a cycling magazine article."
- "Write a preview for the upcoming Tour de France based on the recent results of top contenders like Tadej Pogačar and Jonas Vingegaard."
- "Analyze the evolution of Tom Pidcock's career based on his race results and team history."

### Cycling Education

- "Explain what makes the Monument classics special using data about their history and winners."
- "Create an educational summary about Grand Tours and their significance in professional cycling."
- "Describe the typical career progression of a professional cyclist using examples from the data."

## License

MIT

## MCP Integration

This API is now integrated with the Model Context Protocol (MCP), allowing AI assistants like Claude to directly access cycling data. The MCP server exposes tools for querying race information and results from firstcycling.com.

### Available Tools

| Tool | Description |
|------|-------------|
| `search_race` | Find races by name with optional year and category filters |
| `get_race_details` | Get comprehensive information about a specific race |
| `get_race_results` | Retrieve results for a race edition |
| `get_race_startlist` | Get the startlist for a race edition |

### Natural Language Queries

Users can interact with the FirstCycling API through natural language. Here are some example queries:

- "Who won the Tour de France in 2023?"
- "Show me the results of Paris-Roubaix 2022"
- "When is the next edition of Milan-San Remo?"
- "What was the podium at the Giro d'Italia last year?"
- "Show me the startlist for the upcoming Tour of Flanders"
- "Who has won the most stages in the Vuelta a España?"
- "Compare the routes of the Tour de France between 2022 and 2023"
- "Find WorldTour races happening in May this year"

The MCP server automatically identifies the appropriate tool to use and parameters to pass based on your question.

### Getting Started with MCP

To use the MCP server with Claude Desktop:

1. Ensure you have the latest version of [Claude Desktop](https://claude.ai/download) installed
2. Add this MCP server to your Claude Desktop configuration
3. Start asking questions about cycling races and results

For developers looking to integrate with this MCP server, see our [developer documentation](./docs/mcp-integration.md).
