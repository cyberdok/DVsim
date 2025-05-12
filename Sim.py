from opcua import Client
import time

from LoopSimulation import LoopSimulation

# Connect once
client = Client("opc.tcp://10.10.10.3:9409/DvOpcUaServer")
client.connect()

# Create one simulation loop
loop = LoopSimulation(
    client,
    name="Loop1",
    source_id="ns=2;s=0:ZZZ/AO1/OUT.CV",
    dest_id="ns=2;s=0:ZZZ/AI1/SIMULATE.SVALUE",
    gain=10.0,
    delay_sec=5.0,
    interval_sec=1.0,
    reverse=False
)

# Main loop
try:
    while True:
        loop.step()
        time.sleep(loop.interval)
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.disconnect()
