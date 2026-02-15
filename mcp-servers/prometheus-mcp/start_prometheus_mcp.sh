#!/bin/bash
cd /home/tada/.gemini/antigravity/scratch/otg-test/prometheus-mcp

# Redirect all setup output to stderr to keep stdout clean for MCP JSON-RPC
{
    # Create venv if not exists
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi

    # Activate venv
    source .venv/bin/activate

    # Ensure fastmcp is installed
    if ! pip show fastmcp >/dev/null 2>&1; then
        echo "Installing fastmcp..."
        pip install fastmcp
    fi
} >&2

export PROMETHEUS_URL="http://localhost:9091"
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# Run server
# Using exec to properly run as MCP process
exec python3 -m prometheus_mcp.server --transport stdio --port 8001
