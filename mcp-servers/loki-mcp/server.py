from mcp.server.fastmcp import FastMCP
import httpx
from datetime import datetime, timedelta, timezone

# Initialize the MCP server
# This server exposes tools to interact with Loki for log querying
mcp = FastMCP("loki-mcp")

# Loki service URL (default to localhost, but configurable via env var if modified)
LOKI_URL = "http://loki:3100"

@mcp.tool()
async def query(query: str, limit: int = 100, direction: str = "BACKWARD", time_rfc3339: str = None) -> str:
    """
    Execute a LogQL query (instant vector) against Loki.
    
    Args:
        query: LogQL query string.
        limit: Max entries to return.
        direction: Sort order ("FORWARD" or "BACKWARD").
        time_rfc3339: Evaluation timestamp (optional).
    """
    params = {
        "query": query,
        "limit": limit,
        "direction": direction,
    }
    if time_rfc3339:
        params["time"] = time_rfc3339

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{LOKI_URL}/loki/api/v1/query", params=params)
            resp.raise_for_status()
            data = resp.json()
            
            # Format results
            result = data.get("data", {}).get("result", [])
            output = []
            for stream in result:
                labels = stream.get("stream", {})
                values = stream.get("values", [])
                for v in values:
                    ts_ns = int(v[0])
                    ts_dt = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc)
                    log_line = v[1]
                    output.append(f"[{ts_dt.isoformat()}] {labels} {log_line}")
            
            return "\n".join(output) if output else "No logs found."
            
        except httpx.HTTPError as e:
            return f"Error querying Loki: {str(e)}"

@mcp.tool()
async def query_range(query: str, start: str, end: str, limit: int = 100, direction: str = "BACKWARD", step: str = None) -> str:
    """
    Execute a LogQL range query against Loki.
    
    Args:
        query: LogQL query string.
        start: Start timestamp (RFC3339 or Unix timestamp).
        end: End timestamp (RFC3339 or Unix timestamp).
        limit: Max entries to return.
        direction: Sort order ("FORWARD" or "BACKWARD").
        step: Query resolution step width (e.g., 15s).
    """
    params = {
        "query": query,
        "start": start,
        "end": end,
        "limit": limit,
        "direction": direction,
    }
    if step:
        params["step"] = step

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
            resp.raise_for_status()
            data = resp.json()

            # Format results
            result = data.get("data", {}).get("result", [])
            output = []
            for stream in result:
                labels = stream.get("stream", {}) # For logs
                values = stream.get("values", [])
                for v in values:
                    ts_ns = int(v[0])
                    ts_dt = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc)
                    log_line = v[1]
                    output.append(f"[{ts_dt.isoformat()}] {labels} {log_line}")
            
            return "\n".join(output) if output else "No logs found."
            
        except httpx.HTTPError as e:
            return f"Error querying Loki: {str(e)}"

if __name__ == "__main__":
    # Run the server using stdio, suitable for local integration
    # For container usage like otg-mcp, user might wrap this or use mcp run loki_mcp.py
    mcp.run()
