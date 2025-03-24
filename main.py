import subprocess
import sys
from pathlib import Path

def main():
    """Run the FirstCycling MCP server."""
    server_path = Path(__file__).parent / "firstcycling.py"
    
    try:
        # Run the server using MCP dev mode
        subprocess.run([sys.executable, "-m", "mcp.cli", "dev", str(server_path)], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
