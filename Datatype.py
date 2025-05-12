from opcua import Client

# Define your server and node here
SERVER_URL = "opc.tcp://10.10.10.3:9409/DvOpcUaServer"
NODE_ID = "ns=2;s=0:ZZZ/AI1/SIMULATE.SVALUE"  # Change this to your tag

client = Client(SERVER_URL)

try:
    client.connect()
    print(f"Connected to OPC UA server at {SERVER_URL}")

    node = client.get_node(NODE_ID)
    data_type = node.get_data_type_as_variant_type()
    print(f"Data type for node {NODE_ID}: {data_type.name}")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.disconnect()
    print("Disconnected.")
