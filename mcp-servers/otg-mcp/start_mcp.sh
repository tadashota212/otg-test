#!/bin/bash
# MINIMAL start_mcp.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/otg-mcp"
export PYTHONPATH="$SCRIPT_DIR/otg-mcp/src:$PYTHONPATH"
exec "$SCRIPT_DIR/otg-mcp/.venv/bin/python3" -m otg_mcp.server \
    --config-file "$SCRIPT_DIR/otg-mcp-config.json" \
    --transport stdio \
    2>> "$SCRIPT_DIR/mcp_debug.log"
