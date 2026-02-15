# Prometheus MCP Server (Customized for Antigravity IDE)

This directory contains a custom Prometheus MCP Server implementation for querying metrics from the Containerlab environment.

## Setup & Usage

This server is designed to run in a local Python virtual environment (venv).

### 1. Prerequisite
Ensure you have Python 3.11+ installed.

### 2. Initialization
Use the provided script to set up the environment and start the server:

```bash
# Navigate to this directory
cd mcp-servers/prometheus-mcp

# The startup script will handle venv activation and execution
./start_prometheus_mcp.sh
```

### 3. IDE Configuration
In your Antigravity IDE configuration (`mcp_config.json`), configure the server as follows:

```json
{
    "mcpServers": {
        "prometheus-mcp": {
            "command": "python3",
            "args": ["/absolute/path/to/otg-test/mcp-servers/prometheus-mcp/src/prometheus_mcp/server.py"],
            "env": {
                "MCP_LOG_LEVEL": "INFO",
                "PYTHONUNBUFFERED": "1",
                "PROMETHEUS_URL": "http://172.20.20.42:9090"
            }
        }
    }
}
```

*   **PROMETHEUS_URL**: Ensure this environment variable points to your deployed Prometheus instance.
*   **PYTHONUNBUFFERED**: Critical for real-time JSON-RPC communication.

