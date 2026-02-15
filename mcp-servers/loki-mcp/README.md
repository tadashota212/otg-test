# Loki MCP Server (Customized for Antigravity IDE)
 
 This directory contains a custom Loki MCP Server implementation for querying logs from the Containerlab environment.
 
 ## Setup & Usage
 
 This server is designed to run in a local Python virtual environment (venv).
 
 ### 1. Prerequisite
 Ensure you have Python 3.11+ installed.
 
 ### 2. Initialization
 Use the provided script to set up the environment and start the server:
 
 ```bash
 # Navigate to this directory
 cd mcp-servers/loki-mcp
 
 # Create and activate venv, install deps, then run
 python3 -m venv .venv
 source .venv/bin/activate
 pip install -r requirements.txt
 python3 src/loki_mcp/server.py
 ```
 
 ### 3. IDE Configuration
 In your Antigravity IDE configuration (`mcp_config.json`), configure the server as follows:
 
 ```json
 {
     "mcpServers": {
         "loki-mcp": {
             "command": "python3",
             "args": ["/path/to/otg-test-repo/mcp-servers/loki-mcp/src/loki_mcp/server.py"],
             "env": {
                 "MCP_LOG_LEVEL": "INFO",
                 "PYTHONUNBUFFERED": "1",
                 "LOKI_URL": "http://172.20.20.44:3100"
             }
         }
     }
 }
 ```
 
 *   **LOKI_URL**: Ensure this environment variable points to your deployed Loki instance.
 *   **PYTHONUNBUFFERED**: Critical for real-time JSON-RPC communication.
 
