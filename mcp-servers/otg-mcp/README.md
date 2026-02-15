# OTG MCP Server (Customized for Antigravity IDE)

This directory contains a customized version of the OTG MCP Server, originally based on [h4ndzdatm0ld/otg-mcp](https://github.com/h4ndzdatm0ld/otg-mcp).

## Modifications

To ensure stable integration with Antigravity IDE and proper JSON-RPC communication over stdio, the following key modifications have been applied to the original codebase:

1.  **Stdout Protection**:
    *   Monkey-patched `logging.StreamHandler` in `server.py` to force *all* logs to `stderr`.
    *   This prevents libraries like `snappi` from polluting `stdout`, which is reserved exclusively for JSON-RPC messages.

2.  **Tool Registration**:
    *   Refactored `server.py` to use explicit `@mcp.tool()` decorators instead of dynamic registration.
    *   Fixed parameter ordering in `get_metrics` to match the client implementation.

3.  **Client Logging**:
    *   Updated `client.py` to pass a custom logger to `snappi.api()`, preventing it from creating default handlers.

## Setup & Usage

This server is designed to run in a local Python virtual environment (venv).

### 1. Prerequisite
Ensure you have Python 3.11+ installed.

### 2. Initialization
Use the provided script to set up the environment and start the server:

```bash
# Navigate to this directory
cd mcp-servers/otg-mcp

# The startup script will handle venv activation and execution
./start_mcp.sh
```

### 3. IDE Configuration
In your Antigravity IDE configuration (`mcp_config.json`), configure the server as follows:

```json
{
    "mcpServers": {
        "otg-mcp": {
            "command": "python3",
            "args": ["/absolute/path/to/otg-test/mcp-servers/otg-mcp/src/otg_mcp/server.py"],
            "env": {
                "MCP_LOG_LEVEL": "INFO",
                "PYTHONUNBUFFERED": "1"
            }
        }
    }
}
```

*   **Note**: `PYTHONUNBUFFERED="1"` is critical for ensuring real-time communication between the IDE and the Python process.

## Configuration File

The server requires a JSON configuration file (default: `otg-mcp-config.json`) defining the target traffic generator:

```json
{
    "targets": {
        "172.20.20.37:8443": {
            "ports": {
                "p1": { "location": "eth1", "name": "p1" },
                "p2": { "location": "eth2", "name": "p2" }
            }
        }
    }
}
```
