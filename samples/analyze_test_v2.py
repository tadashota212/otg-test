import json
from datetime import datetime

def analyze():
    with open("otg_log_results.json", "r") as f:
        data = json.load(f)

    if not data: return

    deltas = []
    for i in range(1, len(data)):
        t2 = datetime.fromisoformat(data[i]["time"])
        tx_diff = data[i]["tx"] - data[i-1]["tx"]
        rx_diff = data[i]["rx"] - data[i-1]["rx"]
        loss = tx_diff - rx_diff
        if loss > 0:
            deltas.append((t2, loss))

    if not deltas:
        print("No loss.")
        return

    print("Loss Timeline (Top 20 events):")
    for t, l in sorted(deltas, key=lambda x: x[1], reverse=True)[:20]:
        print(f"{t.isoformat()} : {l} packets")

    # Group by second to see bursts
    bursts = {}
    for t, l in deltas:
        sec = t.replace(microsecond=0).isoformat()
        bursts[sec] = bursts.get(sec, 0) + l
    
    print("\nLoss by second:")
    for sec in sorted(bursts.keys()):
        print(f"{sec} : {bursts[sec]} packets")

if __name__ == "__main__":
    analyze()
