import time
from collections import deque
from opcua import Client, ua

# --- Configuration ---
SERVER_URL = "opc.tcp://10.10.10.3:9409/DvOpcUaServer"
SOURCE_NODE_ID = "ns=2;s=0:ZZZ/AO1/OUT.CV"           # Replace with actual OUT node if different
DEST_NODE_ID   = "ns=2;s=0:ZZZ/AI1/SIMULATE.SVALUE"  # Destination simulated transmitter input

PROCESS_DELAY_SEC = 5.0      # Delay in seconds between output and input effect
LOOP_INTERVAL_SEC = 1.0      # Loop interval in seconds
REVERSE_ACTING = False       # Set to True to invert output → PV relationship

# --- Setup delay buffer ---
delay_steps = int(PROCESS_DELAY_SEC / LOOP_INTERVAL_SEC)
delay_buffer = deque([0.0] * delay_steps, maxlen=delay_steps)

client = Client(SERVER_URL)

try:
    client.connect()
    print(f"Connected to OPC UA server at {SERVER_URL}")

    source_node = client.get_node(SOURCE_NODE_ID)
    dest_node = client.get_node(DEST_NODE_ID)

    while True:
        try:
            # 1. Read controller output (%)
            output_pct = source_node.get_value()
            print(f"Controller Output: {output_pct:.2f}%")

            # 2. Scale to PV range (0–1000 kPa), reverse if needed
            
            # Reverse acting logic
            if REVERSE_ACTING:
                simulated_pv = (100.0 - output_pct) * 10.0
            else:
                simulated_pv = output_pct * 10.0

            # Clamp to 0–1000 kPa
            simulated_pv = max(0.0, min(simulated_pv, 1000.0))

            # 3. Add to delay buffer
            delay_buffer.append(simulated_pv)

            # 4. Output the delayed value
            delayed_value = delay_buffer[0]
            print(f"Simulated PV (delayed): {delayed_value:.2f} kPa")

            # 5. Write to SIMULATE.SVALUE
            dest_node.set_value(ua.Variant(delayed_value, ua.VariantType.Float))

        except Exception as loop_err:
            print(f"Loop error: {loop_err}")

        time.sleep(LOOP_INTERVAL_SEC)

except Exception as conn_err:
    print(f"Connection error: {conn_err}")

finally:
    client.disconnect()
    print("Disconnected.")
