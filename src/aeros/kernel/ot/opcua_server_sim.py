"""
OPC UA server simulator for the Areos compression-room scenario.

Simulates a BMS/EMS OPC UA server exposing real-time process values for
AHU-03 / Compression Room 1.  In the target AWS architecture this would be
replaced by a real BMS OPC UA endpoint collected by Greengrass components.

Local AWS Greengrass equivalent: OPC UA collector component reading live tags.

Run:
    python -m aeros.kernel.ot.opcua_server_sim

The server starts on opc.tcp://0.0.0.0:4840 and updates values every second.
"""

import asyncio

from asyncua import Server


async def run_opcua_server(endpoint: str = "opc.tcp://0.0.0.0:4840/freeopcua/server/") -> None:
    server = Server()
    await server.init()
    server.set_endpoint(endpoint)
    await server.set_server_name("Areos OSD Compression Room Sim")

    idx = await server.register_namespace("areos.opcua.sim")
    objects = server.nodes.objects
    metrics = await objects.add_object(idx, "CompressionRoomMetrics")

    rh = await metrics.add_variable(idx, "RelativeHumidity", 45.0)
    temp = await metrics.add_variable(idx, "Temperature", 23.0)
    dp = await metrics.add_variable(idx, "DifferentialPressure", 15.0)
    ahu_status = await metrics.add_variable(idx, "AHUStatus", "RUNNING")
    press_state = await metrics.add_variable(idx, "TabletPressState", "EXECUTE")

    await rh.set_writable()
    await temp.set_writable()
    await dp.set_writable()
    await ahu_status.set_writable()
    await press_state.set_writable()

    print(f"[opcua-server] Endpoint : {endpoint}")
    print("[opcua-server] Namespace: areos.opcua.sim")
    print("[opcua-server] Tags exposed:")
    print("  - CompressionRoomMetrics/RelativeHumidity")
    print("  - CompressionRoomMetrics/Temperature")
    print("  - CompressionRoomMetrics/DifferentialPressure")
    print("  - CompressionRoomMetrics/AHUStatus")
    print("  - CompressionRoomMetrics/TabletPressState")
    print("[opcua-server] Running — press Ctrl-C to stop")

    minute = 0
    async with server:
        while True:
            await asyncio.sleep(1)
            # Simulate the humidity excursion profile (1 s ≈ 1 min in sim time)
            if 20 <= (minute % 60) < 42:
                await rh.write_value(63.0)
                await ahu_status.write_value("ALARM")
            else:
                await rh.write_value(49.0)
                await ahu_status.write_value("RUNNING")
            minute += 1


if __name__ == "__main__":
    asyncio.run(run_opcua_server())
