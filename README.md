# FirstCycling MCP Server

This is a Model Context Protocol (MCP) server that provides professional cycling data from FirstCycling. It allows you to retrieve information about professional cyclists, race results, and more.

## Features

The server currently exposes the following tools:

- **get_rider_info**: Retrieves information about a professional cyclist based on their FirstCycling rider ID.
- **get_race_results**: Retrieves results for a specific race in a given year based on the FirstCycling race ID.

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

### API Features

- Rider information (profile, results)
- Race results and information
- Rankings

### Common FirstCycling IDs

#### Riders

- Tadej Pogačar: 16973
- Jonas Vingegaard: 21527
- Remco Evenepoel: 23697
- Primož Roglič: 10635

#### Races

- Tour de France: 17
- Giro d'Italia: 13
- Vuelta a España: 23
- Paris-Roubaix: 30
- Tour of Flanders: 29

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
     "proxyServers": {
       "firstcycling": {
         "command": ["python", "-m", "mcp.transport.subprocess", "firstcycling.py"]
       }
     }
   }
   ```

3. Restart Claude for Desktop

## Example Queries

Once connected to Claude, you can ask:

- "Who is Tadej Pogačar? Get his rider information with ID 16973."
- "Show me the results of the 2023 Tour de France (race ID 17)."
- "Get rider profile for Remco Evenepoel (ID 23697)."
- "What were the results of Paris-Roubaix (ID 30) in 2024?"

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
