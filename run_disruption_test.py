import snappi
import time
import requests
import json
from datetime import datetime, timezone

# Configuration
OTG_API = "https://172.20.20.37:8443"
PROMETHEUS_URL = "http://172.20.20.42:9090"
LOKI_URL = "http://172.20.20.44:3100" # clab-otg-test-loki address in clab network? 
# Wait, let's check loki address. Clab-otg-test-loki mgmt-ipv4: 172.20.20.44
# Actually from docker inspect it might be different, but let's use the one in clab.

def get_otg_metrics():
    api = snappi.api(location=OTG_API, verify=False)
    req = api.metrics_request()
    req.flow.flow_names = ["f1"]
    metrics = api.get_metrics(req)
    if metrics.flow_metrics:
        m = metrics.flow_metrics[0]
        return {
            "tx": m.frames_tx,
            "rx": m.frames_rx,
            "tx_rate": m.frames_tx_rate,
            "rx_rate": m.frames_rx_rate,
            "time": datetime.now(timezone.utc).isoformat()
        }
    return None

def test_disruption():
    test_results = []
    
    print("Baseline monitoring (10s)...")
    for _ in range(20):
        m = get_otg_metrics()
        if m: test_results.append(m)
        time.sleep(0.5)

    disrupt_time = datetime.now(timezone.utc).isoformat()
    print(f"DISRUPTION START: {disrupt_time}")
    # Run shutdown command via docker
    import subprocess
    subprocess.run(["docker", "exec", "clab-otg-test-leaf1", "FastCli", "-p", "15", "-c", "conf t", "-c", "interface Ethernet1", "-c", "shutdown"], check=True)
    
    print("Monitoring during disruption (20s)...")
    for _ in range(40):
        m = get_otg_metrics()
        if m: test_results.append(m)
        time.sleep(0.5)

    recover_time = datetime.now(timezone.utc).isoformat()
    print(f"RECOVERY START: {recover_time}")
    subprocess.run(["docker", "exec", "clab-otg-test-leaf1", "FastCli", "-p", "15", "-c", "conf t", "-c", "interface Ethernet1", "-c", "no shutdown"], check=True)

    print("Monitoring after recovery (20s)...")
    for _ in range(40):
        m = get_otg_metrics()
        if m: test_results.append(m)
        time.sleep(0.5)

    # Save data
    with open("/app/test_run_data.json", "w") as f:
        json.dump({
            "disrupt_time": disrupt_time,
            "recover_time": recover_time,
            "metrics": test_results
        }, f, indent=2)

if __name__ == "__main__":
    test_disruption()
