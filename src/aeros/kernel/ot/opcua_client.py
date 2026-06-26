"""
OPC UA client for Areos.

Reads tags from a running OPC UA server (e.g. the local simulator).
In the target AWS architecture, Greengrass OPC UA collector components
perform this role, forwarding tag values to AWS IoT Core MQTT topics.

Run against the local simulator:
    # Terminal 1: start server
    python -m aeros.kernel.ot.opcua_server_sim

    # Terminal 2: read tags
    python -m aeros.kernel.ot.opcua_client
"""

import asyncio

from asyncua import Client


COMPRESSION_ROOM_TAGS = {
    "RelativeHumidity": "ns=2;i=3",
    "Temperature": "ns=2;i=4",
    "DifferentialPressure": "ns=2;i=5",
    "AHUStatus": "ns=2;i=6",
    "TabletPressState": "ns=2;i=7",
}


async def read_node_value(endpoint: str, node_id: str):
    """Read a single tag value from an OPC UA server."""
    async with Client(url=endpoint) as client:
        node = client.get_node(node_id)
        return await node.read_value()


async def browse_and_read_metrics(endpoint: str = "opc.tcp://localhost:4840/freeopcua/server/") -> dict:
    """Browse the CompressionRoomMetrics object and read all child variables."""
    results = {}
    async with Client(url=endpoint) as client:
        root = client.nodes.root
        objects = client.nodes.objects
        children = await objects.get_children()
        for child in children:
            name = (await child.read_browse_name()).Name
            if name == "CompressionRoomMetrics":
                variables = await child.get_children()
                for var in variables:
                    var_name = (await var.read_browse_name()).Name
                    try:
                        value = await var.read_value()
                        results[var_name] = value
                    except Exception:
                        results[var_name] = None
    return results


if __name__ == "__main__":
    import json

    endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    print(f"[opcua-client] Connecting to {endpoint}")
    try:
        readings = asyncio.run(browse_and_read_metrics(endpoint))
        print("[opcua-client] CompressionRoomMetrics:")
        for tag, value in readings.items():
            print(f"  {tag:<30} = {value}")
    except Exception as exc:
        print(f"[opcua-client] ERROR: {exc}")
        print("[opcua-client] Ensure the OPC UA server is running:")
        print("  python -m aeros.kernel.ot.opcua_server_sim")
