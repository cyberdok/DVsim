from collections import deque
from opcua import ua

class LoopSimulation:
    def __init__(self, client, name, source_id, dest_id, gain=10.0, delay_sec=5.0, interval_sec=1.0, reverse=False):
        self.name = name
        self.client = client
        self.source_node = client.get_node(source_id)
        self.dest_node = client.get_node(dest_id)
        self.gain = gain
        self.reverse = reverse
        self.interval = interval_sec

        # Delay buffer setup
        self.steps = int(delay_sec / interval_sec)
        self.delay_buffer = deque([0.0] * self.steps, maxlen=self.steps)

    def step(self):
        try:
            # 1. Read controller output
            output = self.source_node.get_value()

            # 2. Convert to simulated PV
            if self.reverse:
                sim_value = (100.0 - output) * self.gain
            else:
                sim_value = output * self.gain

            # 3. Clamp
            sim_value = max(0.0, min(sim_value, 1000.0))

            # 4. Apply delay
            self.delay_buffer.append(sim_value)
            delayed = self.delay_buffer[0]

            # 5. Write to simulated PV
            self.dest_node.set_value(ua.Variant(delayed, ua.VariantType.Float))

            # 6. Debug output
            print(f"[{self.name}] OUT: {output:.2f}% → PV: {delayed:.2f} kPa")

        except Exception as e:
            print(f"[{self.name}] Error: {e}")
