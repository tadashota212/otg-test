import argparse
import logging
import sys
import traceback
from typing import Annotated, Any, Dict, List, Literal, Optional

# --- AGGRESSIVE MCP-SAFE LOGGING REDIRECTION ---
# Patch logging.StreamHandler to prevent ANY library from writing to stdout.
# This is critical for MCP servers where stdout is reserved for JSON-RPC.
_original_stream_handler_init = logging.StreamHandler.__init__
def _patched_stream_handler_init(self, stream=None):
    if stream is sys.stdout or stream is None:
        # Default to stderr if stdout or None is requested
        stream = sys.stderr
    _original_stream_handler_init(self, stream)
logging.StreamHandler.__init__ = _patched_stream_handler_init

# Force global logging to stderr
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
    force=True
)

# Silence specific known offenders
for name in ["snappi", "snappi.snappi", "urllib3"]:
    l = logging.getLogger(name)
    l.handlers = []
    l.propagate = True # Let it go to our stderr-configured root logger

# ---------------------------------------------

from fastmcp import FastMCP
from pydantic import Field

from otg_mcp.client import OtgClient
from otg_mcp.config import Config
from otg_mcp.models import (
    CaptureResponse,
    ConfigResponse,
    ControlResponse,
    HealthStatus,
    MetricsResponse,
)

logger = logging.getLogger("otg_mcp_server")

class OtgMcpServer:
    def __init__(self, config_file: str):
        try:
            self.config = Config(config_file)
            self.mcp = FastMCP("otg-mcp", log_level="ERROR") 
            self.client = OtgClient(config=self.config)
            self._register_tools()
        except Exception as e:
            sys.stderr.write(f"CRITICAL INIT ERROR: {e}\n")
            raise

    def _register_tools(self):
        @self.mcp.tool()
        async def get_available_targets() -> Dict[str, Any]:
            """Get all available traffic generator targets."""
            return await self.client.get_available_targets()

        @self.mcp.tool()
        async def get_metrics(
            flow_names: Optional[List[str]] = None,
            port_names: Optional[List[str]] = None,
            target: Optional[str] = None,
        ) -> MetricsResponse:
            """Get metrics from the traffic generator."""
            return await self.client.get_metrics(flow_names, port_names, target)

        @self.mcp.tool()
        async def start_traffic(target: str) -> ControlResponse:
            """Start traffic generation."""
            return await self.client.start_traffic(target)

        @self.mcp.tool()
        async def stop_traffic(target: str) -> ControlResponse:
            """Stop traffic generation."""
            return await self.client.stop_traffic(target)

        @self.mcp.tool()
        async def set_config(config: Dict[str, Any], target: str) -> ConfigResponse:
            """Set the configuration of the traffic generator."""
            return await self.client.set_config(config, target)

        @self.mcp.tool()
        async def get_config(target: str) -> ConfigResponse:
            """Get the current configuration of the traffic generator."""
            return await self.client.get_config(target)

        @self.mcp.tool()
        async def health(target: Optional[str] = None) -> HealthStatus:
            """Check the health of targets."""
            return await self.client.health(target)

        @self.mcp.tool()
        async def start_capture(port_name: List[str], target: str) -> CaptureResponse:
            """Start packet capture on specified ports."""
            return await self.client.start_capture(port_name, target)

        @self.mcp.tool()
        async def stop_capture(port_name: List[str], target: str) -> CaptureResponse:
            """Stop packet capture on specified ports."""
            return await self.client.stop_capture(port_name, target)

        @self.mcp.tool()
        async def get_capture(port_name: str, target: str, output_dir: Optional[str] = None) -> str:
            """Get packet capture from a port."""
            return await self.client.get_capture(port_name=port_name, target=target, output_dir=output_dir)

    def run(self, transport: str = "stdio"):
        self.mcp.run(transport=transport)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", required=True)
    parser.add_argument("--transport", default="stdio")
    args = parser.parse_args()
    
    try:
        server = OtgMcpServer(args.config_file)
        server.run(args.transport)
    except Exception as e:
        sys.stderr.write(f"FATAL ERROR: {e}\n{traceback.format_exc()}\n")
        sys.exit(1)
