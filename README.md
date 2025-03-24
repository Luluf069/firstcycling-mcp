# FirstCycling MCP Server

This is a Model Context Protocol (MCP) server that provides professional cycling data from FirstCycling. It allows you to retrieve information about professional cyclists, race results, and more.

## Features

The server currently exposes the following tools:

- **get_rider_info**: Retrieves information about a professional cyclist based on their FirstCycling rider ID.
- **get_race_results**: Retrieves results for a specific race in a given year based on the FirstCycling race ID.

## Requirements

- Python 3.10 or higher
- `uv` package manager (recommended)

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
   uv add "mcp[cli]" httpx
   ```

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

## License

MIT
