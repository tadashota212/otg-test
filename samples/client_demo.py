import subprocess
import json
import sys
import os
import time

def run_demo():
    # Locate the start_mcp.sh script (assumed to be in parent directory of repo_prep)
    # repo_prep/samples/client_demo.py -> ../../start_mcp.sh
    script_dir = os.path.dirname(os.path.abspath(__file__))
    start_script = os.path.abspath(os.path.join(script_dir, '../../start_mcp.sh'))

    if not os.path.exists(start_script):
        print(f"Error: Start script not found at {start_script}")
        return

    print(f"Starting MCP Server via: {start_script}")
    
    # Start the MCP Server process
    # We pipe stdin/stdout to communicate via JSON-RPC
    process = subprocess.Popen(
        [start_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=1  # Line buffered
    )

    try:
        # 1. Initialize Request
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "python-demo-client", "version": "1.0"}
            }
        }
        
        print("\n[Client] Sending 'initialize' request...")
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()

        # Read Initialize Response
        while True:
            line = process.stdout.readline()
            if not line: break
            try:
                resp = json.loads(line)
                print(f"[Server] Received response: {json.dumps(resp, indent=2)}")
                if resp.get("id") == 1:
                    break
            except json.JSONDecodeError:
                print(f"[Server Log] {line.strip()}")

        # 2. Initialized Notification
        process.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }) + "\n")
        process.stdin.flush()

        # 3. List Tools Request
        list_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        print("\n[Client] Sending 'tools/list' request...")
        process.stdin.write(json.dumps(list_req) + "\n")
        process.stdin.flush()

        # Read Tools List Response
        while True:
            line = process.stdout.readline()
            if not line: break
            try:
                resp = json.loads(line)
                # Print abbreviated response for readability
                if resp.get("id") == 2:
                    tools = resp.get("result", {}).get("tools", [])
                    print(f"[Server] Received {len(tools)} tools:")
                    for tool in tools:
                        print(f" - {tool['name']}: {tool.get('description', '')[:50]}...")
                    break
                else:
                    print(f"[Server] Received: {json.dumps(resp)}")

            except json.JSONDecodeError:
                print(f"[Server Log] {line.strip()}")

        print("\n[Client] Demo completed successfully.")

    except Exception as e:
        print(f"Error during demo: {e}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    run_demo()
