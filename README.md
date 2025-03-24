# MCP Weather Server

A simple MCP (Model Context Protocol) server that provides weather information from the US National Weather Service API.

## Features

This server exposes two tools:

1. `get_alerts` - Get weather alerts for a US state
2. `get_forecast` - Get weather forecast for a specific location by latitude/longitude

## Installation

### Requirements

- Python 3.10 or higher
- `uv` package manager (recommended)

### Setup

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   uv add "mcp[cli]" httpx
   ```

## Usage

### Development Mode

To test the server with the MCP Inspector:

```bash
uv run mcp dev weather.py
```

This will open the MCP Inspector in your browser, allowing you to test the tools.

### Integration with Claude for Desktop

To use this server with Claude for Desktop:

1. Edit your Claude for Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add this server to the `mcpServers` section:

   ```json
   {
       "mcpServers": {
           "weather": {
               "command": "uv",
               "args": [
                   "--directory",
                   "/ABSOLUTE/PATH/TO/THIS/FOLDER",
                   "run",
                   "weather.py"
               ]
           }
       }
   }
   ```

3. Restart Claude for Desktop

## Example Queries

Once connected to Claude, you can ask:

- "What are the active weather alerts in California?"
- "What's the forecast for San Francisco? (Latitude 37.7749, Longitude -122.4194)"

## License

MIT
