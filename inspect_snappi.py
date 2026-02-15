import snappi
try:
    api = snappi.api()
    cfg = api.config()
    lag = cfg.lags.add(name="l1")
    lp = lag.ports.add(port_name="p1")
    print(f"Type of lp.ethernet: {type(lp.ethernet)}")
    try:
        lp.ethernet = "eth1"
    except Exception as e:
        print(f"Set ethernet error: {e}")

    try:
        print(f"Dir of lp.ethernet: {dir(lp.ethernet)}")
    except Exception as e:
        print(f"Dir ethernet error: {e}")
except Exception as e:
    print(e)
