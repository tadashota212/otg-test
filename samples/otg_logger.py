import snappi
import time
import json
from datetime import datetime, timezone

OTG_API = "https://172.20.20.37:8443"

def get_otg_metrics(api):
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

def main():
    api = snappi.api(location=OTG_API, verify=False)
    results = []
    print("Starting OTG Logger...")
    try:
        while True:
            m = get_otg_metrics(api)
            if m:
                results.append(m)
                # print(f"{m['time']} RX: {m['rx']}")
            time.sleep(0.1) # 100ms interval
    except KeyboardInterrupt:
        pass
    finally:
        with open("/app/otg_log.json", "w") as f:
            json.dump(results, f, indent=2)
        print("Logged data saved.")

if __name__ == "__main__":
    main()
