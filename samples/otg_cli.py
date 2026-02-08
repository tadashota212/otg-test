#!/usr/bin/env python3
"""
Interactive CLI for OTG MCP Server
Usage: python3 otg_cli.py
"""
import subprocess
import json
import sys

class OtgCli:
    def __init__(self):
        self.request_id = 0
        self.process = None
        
    def start_server(self):
        """Start the MCP server process"""
        script_path = "/home/tada/.gemini/antigravity/scratch/ceos-otg/start_mcp.sh"
        print(f"Starting MCP Server: {script_path}")
        
        self.process = subprocess.Popen(
            [script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Initialize
        self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "otg-cli", "version": "1.0"}
        })
        
        # Send initialized notification
        self._send_notification("notifications/initialized")
        
        print("✓ MCP Server connected\n")
    
    def _send_request(self, method, params=None):
        """Send a JSON-RPC request and return the response"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        if params:
            request["params"] = params
        
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        # Read response
        while True:
            line = self.process.stdout.readline()
            if not line:
                return None
            try:
                response = json.loads(line)
                if response.get("id") == self.request_id:
                    return response.get("result")
            except json.JSONDecodeError:
                continue
    
    def _send_notification(self, method, params=None):
        """Send a JSON-RPC notification (no response expected)"""
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            notification["params"] = params
        
        self.process.stdin.write(json.dumps(notification) + "\n")
        self.process.stdin.flush()
    
    def list_tools(self):
        """List available tools"""
        result = self._send_request("tools/list")
        if result and "tools" in result:
            print("Available Tools:")
            for tool in result["tools"]:
                print(f"  • {tool['name']}: {tool.get('description', 'No description')[:60]}...")
            print()
    
    def call_tool(self, tool_name, arguments):
        """Call a specific tool"""
        result = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return result
    
    def health_check(self, target=None):
        """Perform health check"""
        print(f"Checking health for target: {target or 'all targets'}...")
        result = self.call_tool("health", {"target": target})
        print(json.dumps(result, indent=2))
    
    def get_targets(self):
        """Get available targets"""
        print("Getting available targets...")
        result = self.call_tool("get_available_targets", {})
        print(json.dumps(result, indent=2))
    
    def start_traffic(self, target):
        """Start traffic generation"""
        print(f"Starting traffic on target: {target}...")
        result = self.call_tool("start_traffic", {"target": target})
        print(json.dumps(result, indent=2))
    
    def stop_traffic(self, target):
        """Stop traffic generation"""
        print(f"Stopping traffic on target: {target}...")
        result = self.call_tool("stop_traffic", {"target": target})
        print(json.dumps(result, indent=2))
    
    def get_metrics(self, target=None, flow_names=None, port_names=None):
        """Get metrics"""
        print(f"Getting metrics from target: {target or 'default'}...")
        args = {}
        if target:
            args["target"] = target
        if flow_names:
            args["flow_names"] = flow_names
        if port_names:
            args["port_names"] = port_names
        
        result = self.call_tool("get_metrics", args)
        print(json.dumps(result, indent=2))
    
    def interactive_mode(self):
        """Run interactive command loop"""
        print("\n=== OTG Interactive CLI ===")
        print("Commands:")
        print("  list          - List available tools")
        print("  targets       - Get available targets")
        print("  health [target] - Health check")
        print("  start <target> - Start traffic")
        print("  stop <target>  - Stop traffic")
        print("  metrics [target] - Get metrics")
        print("  quit          - Exit")
        print()
        
        while True:
            try:
                cmd = input("otg> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                
                if command == "quit":
                    break
                elif command == "list":
                    self.list_tools()
                elif command == "targets":
                    self.get_targets()
                elif command == "health":
                    target = parts[1] if len(parts) > 1 else None
                    self.health_check(target)
                elif command == "start":
                    if len(parts) < 2:
                        print("Usage: start <target>")
                    else:
                        self.start_traffic(parts[1])
                elif command == "stop":
                    if len(parts) < 2:
                        print("Usage: stop <target>")
                    else:
                        self.stop_traffic(parts[1])
                elif command == "metrics":
                    target = parts[1] if len(parts) > 1 else None
                    self.get_metrics(target)
                else:
                    print(f"Unknown command: {command}")
                
                print()
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

def main():
    cli = OtgCli()
    try:
        cli.start_server()
        cli.interactive_mode()
    finally:
        cli.cleanup()
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
