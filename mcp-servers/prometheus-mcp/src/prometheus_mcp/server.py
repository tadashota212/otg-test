from fastmcp import FastMCP
import urllib.request
import urllib.parse
import json
import logging
import argparse
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

mcp = FastMCP("prometheus-mcp")

PROMETHEUS_URL = "http://localhost:9091"

@mcp.tool()
def query(query: str, time_rfc3339: str = None) -> str:
    """Execute a PromQL query (instant vector) against Prometheus.
    
    Args:
        query: PromQL query string.
        time_rfc3339: Evaluation timestamp in RFC3339 format (optional).
    """
    base_url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {"query": query}
    if time_rfc3339:
        params["time"] = time_rfc3339
        
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                return f"Error: HTTP {response.status}"
            data = json.loads(response.read().decode())
            if data["status"] != "success":
                return f"Error from Prometheus: {data.get('error')}"
            return json.dumps(data["data"], indent=2)
    except Exception as e:
        return f"Failed to query Prometheus: {str(e)}"

@mcp.tool()
def query_range(query: str, start: str, end: str, step: str) -> str:
    """Execute a PromQL range query against Prometheus.
    
    Args:
        query: PromQL query string.
        start: Start timestamp (RFC3339 or Unix timestamp).
        end: End timestamp (RFC3339 or Unix timestamp).
        step: Query resolution step width in duration format (e.g., 15s).
    """
    base_url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": step
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                return f"Error: HTTP {response.status}"
            data = json.loads(response.read().decode())
            if data["status"] != "success":
                return f"Error from Prometheus: {data.get('error')}"
            return json.dumps(data["data"], indent=2)
    except Exception as e:
        return f"Failed to query Prometheus: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Prometheus MCP Server")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on (SSE)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to listen on (SSE)")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse"], default="sse", help="Transport mode")
    parser.add_argument("--prometheus-url", type=str, default="http://localhost:9091", help="Prometheus URL")
    
    args = parser.parse_args()
    
    global PROMETHEUS_URL
    PROMETHEUS_URL = args.prometheus_url
    
    if args.transport == "sse":
        mcp.settings.port = args.port
        mcp.settings.host = args.host
    
    mcp.run(transport=args.transport)

if __name__ == "__main__":
    main()
