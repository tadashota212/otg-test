import json
from datetime import datetime

def analyze():
    with open("otg_log_results.json", "r") as f:
        data = json.load(f)

    if not data:
        print("No data found.")
        return

    print(f"Total entries: {len(data)}")
    
    # Calculate differentials
    deltas = []
    for i in range(1, len(data)):
        t1 = datetime.fromisoformat(data[i-1]["time"])
        t2 = datetime.fromisoformat(data[i]["time"])
        dt = (t2 - t1).total_seconds()
        
        tx_diff = data[i]["tx"] - data[i-1]["tx"]
        rx_diff = data[i]["rx"] - data[i-1]["rx"]
        
        loss = tx_diff - rx_diff
        deltas.append({
            "time": data[i]["time"],
            "dt": dt,
            "tx_diff": tx_diff,
            "rx_diff": rx_diff,
            "loss": loss
        })

    # Find disruption window
    # Search for non-zero loss
    disrupt_points = [d for d in deltas if d["loss"] > 5] # Small threshold for jitter
    
    if not disrupt_points:
        print("No significant packet loss detected.")
        return

    first_loss = disrupt_points[0]
    last_loss = disrupt_points[-1]
    
    total_loss = sum(d["loss"] for d in deltas if d["loss"] > 0)
    
    print(f"First loss detected at: {first_loss['time']}")
    print(f"Last loss detected at: {last_loss['time']}")
    print(f"Disruption duration (approx): {(datetime.fromisoformat(last_loss['time']) - datetime.fromisoformat(first_loss['time'])).total_seconds():.3f}s")
    print(f"Total packet loss: {total_loss} packets")
    
    # Estimate convergence time
    # This is tricky without knowing exactly when the shutdown was triggered.
    # But usually the first loss point is the trigger.
    # The recovery is when RX rate stabilizes.
    
    # Search for recovery after first loss
    # ...
    
if __name__ == "__main__":
    analyze()
