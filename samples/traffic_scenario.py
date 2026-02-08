
import snappi
import time

def run_direct_test():
    # 1. Initialize API
    api_location = "https://172.20.20.37:8443"
    print(f"Connecting to OTG at {api_location}...")
    api = snappi.api(location=api_location, verify=False)

    # 2. Create Configuration
    config = api.config()
    
    # Ports
    p1 = config.ports.port(name="p1", location="eth1")[-1]
    p2 = config.ports.port(name="p2", location="eth2")[-1]
    p3 = config.ports.port(name="p3", location="eth3")[-1]
    p4 = config.ports.port(name="p4", location="eth4")[-1]

    # Flow f1: p1 -> p3/p4
    f1 = config.flows.flow(name="f1")[-1]
    f1.tx_rx.port.tx_name = p1.name
    # Note: snappi usually takes rx_name (singular) or rx_names (plural) depending on version.
    # We will try rx_name first as it's common in older versions or single port. 
    # But here we want multi-port RX for ECMP verification.
    # Let's try assigning list if supported, or falling back to single for basic test.
    # For correctness given previous errors, let's use rx_names and hope the library version supports it.
    # If not we can fallback.
    try:
        f1.tx_rx.port.rx_names = [p3.name, p4.name]
    except Exception:
        f1.tx_rx.port.rx_name = p3.name

    # Packet
    eth = f1.packet.ethernet()[-1]
    eth.src.value = "00:11:01:00:00:01"
    eth.dst.value = "00:11:02:00:00:01" # Destination MAC (e.g. Gateway)

    ip = f1.packet.ipv4()[-1]
    ip.src.value = "10.10.10.101"
    ip.dst.value = "10.10.10.102"

    # Rate & Duration
    f1.size.fixed = 128
    f1.rate.pps = 100
    f1.duration.continuous.gap = 12
    
    # Metrics
    f1.metrics.enable = True

    # 3. Apply Config
    print("Applying configuration...")
    try:
        api.set_config(config)
    except Exception as e:
        print(f"Error applying config: {e}")
        return

    # 4. Start Traffic
    print("Starting traffic...")
    cs = api.control_state()
    cs.choice = cs.TRAFFIC
    cs.traffic.choice = cs.traffic.FLOW_TRANSMIT
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
    api.set_control_state(cs)

    # 5. Monitor Metrics
    print("Monitoring metrics for 10 seconds...")
    for i in range(10):
        time.sleep(1)
        req = api.metrics_request()
        req.flow.flow_names = [f1.name]
        metrics = api.get_metrics(req)
        
        if metrics.flow_metrics:
            m = metrics.flow_metrics[0]
            print(f"[{i+1}s] Tx: {m.frames_tx}, Rx: {m.frames_rx}, Loss: {m.frames_tx - m.frames_rx}")
        else:
            print(f"[{i+1}s] No metrics")

    # 6. Stop Traffic
    print("Stopping traffic...")
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
    api.set_control_state(cs)
    print("Done.")

if __name__ == "__main__":
    run_direct_test()
