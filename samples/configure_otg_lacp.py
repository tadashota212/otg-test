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

# LAGs (match cEOS Port-Channel 5)
lag1 = cfg.lags.add(name="lag1")
lag1.protocol.lacp.actor_key = 1
lag1.protocol.lacp.actor_system_priority = 1
lag1.protocol.lacp.actor_system_id = "00:00:00:00:00:01"
lp1 = lag1.ports.add(port_name=p1.name)
lp1.ethernet.name = "eth_p1"
lp1.ethernet.mac = "00:11:00:00:00:01"

lag3 = cfg.lags.add(name="lag3") 
lag3.protocol.lacp.actor_key = 3
lag3.protocol.lacp.actor_system_priority = 1
lag3.protocol.lacp.actor_system_id = "00:00:00:00:00:03"
lp3 = lag3.ports.add(port_name=p3.name)
lp3.ethernet.name = "eth_p3"
lp3.ethernet.mac = "00:11:00:00:00:03"

# Devices (Network Layers)
d1 = cfg.devices.add(name="d1")
d1_eth = d1.ethernets.add(name="d1_eth")
d1_eth.connection.lag_name = lag1.name
d1_eth.mac = "02:00:00:00:00:01"
d1_ip = d1_eth.ipv4_addresses.add(name="d1_ip", address="10.10.10.101", gateway="10.10.10.1", prefix=24)

d3 = cfg.devices.add(name="d3")
d3_eth = d3.ethernets.add(name="d3_eth")
d3_eth.connection.lag_name = lag3.name
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

# Start Protocols (LACP)
print("Starting protocols...")
ps = api.control_state()
ps.protocol.all.state = ps.protocol.all.START
api.set_control_state(ps)

# Wait for LACP
print("Waiting for LACP negotiation...")
time.sleep(10)

# Start Traffic
print("Starting traffic...")
ts = api.control_state()
ts.traffic.flow_transmit.state = ts.traffic.flow_transmit.START
api.set_control_state(ts)

# Monitor loop
print("Monitoring metrics... (Press Ctrl+C to stop)")
start_time = time.time()
params = {
    'start_time': start_time,
    'prev_tx': 0,
    'prev_rx': 0
}

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
            
        time.sleep(1)
        if time.time() - start_time > 60: # Run for 60s
            break

except KeyboardInterrupt:
    print("\nStopping...")

print("Test complete.")
