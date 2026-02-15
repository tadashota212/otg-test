import snappi
import time
import sys

# Define API target
api = snappi.api(location="https://172.20.20.37:8443", verify=False)

# Build configuration
cfg = api.config()

# Ports
p1 = cfg.ports.add(name="p1", location="eth1")
p3 = cfg.ports.add(name="p3", location="eth3")

# Devices
d1 = cfg.devices.add(name="d1")
d1_eth = d1.ethernets.add(name="d1_eth")
d1_eth.connection.port_name = p1.name
d1_eth.mac = "02:00:00:00:00:01"
d1_ip = d1_eth.ipv4_addresses.add(name="d1_ip", address="10.10.10.101", gateway="10.10.10.1", prefix=24)

d3 = cfg.devices.add(name="d3")
d3_eth = d3.ethernets.add(name="d3_eth")
d3_eth.connection.port_name = p3.name
d3_eth.mac = "02:00:00:00:00:03"
d3_ip = d3_eth.ipv4_addresses.add(name="d3_ip", address="10.10.10.103", gateway="10.10.10.1", prefix=24)

# Flow
f1 = cfg.flows.add(name="f1")
f1.tx_rx.device.tx_names = [d1.name]
f1.tx_rx.device.rx_names = [d3.name]
f1.size.fixed = 128
f1.rate.pps = 1000
f1.duration.continuous.gap = 12
f1.metrics.enable = True

# Push configuration
print("Pushing config...")
try:
    api.set_config(cfg)
except Exception as e:
    print(f"Error pushing config: {e}")
    sys.exit(1)

# Start Traffic
print("Starting traffic...")
ts = api.control_state()
ts.traffic.flow_transmit.state = ts.traffic.flow_transmit.START
api.set_control_state(ts)

# Monitor loop
print("Monitoring metrics... (Press Ctrl+C to stop)")
start_time = time.time()

try:
    while True:
        req = api.metrics_request()
        req.flow.flow_names = [f1.name]
        metrics = api.get_metrics(req)
        
        if metrics.flow_metrics:
            m = metrics.flow_metrics[0]
            curr_tx = m.frames_tx
            curr_rx = m.frames_rx
            loss = curr_tx - curr_rx
            print(f"[{time.time() - start_time:.1f}s] TX: {curr_tx} | RX: {curr_rx} | Loss: {loss} | Rate: {m.frames_rx_rate:.1f} pps")
        else:
            print("No flow metrics available.")
            
        time.sleep(0.5)
        if time.time() - start_time > 120: # Run for 120s
            break

except KeyboardInterrupt:
    print("\nStopping...")

print("Test complete.")
