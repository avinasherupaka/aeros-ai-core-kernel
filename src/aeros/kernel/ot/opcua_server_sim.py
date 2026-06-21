import asyncio

from asyncua import Server


async def run_opcua_server(endpoint: str = "opc.tcp://0.0.0.0:4840/freeopcua/server/") -> None:
    server = Server()
    await server.init()
    server.set_endpoint(endpoint)

    idx = await server.register_namespace("areos.opcua.sim")
    objects = server.nodes.objects
    metrics = await objects.add_object(idx, "CompressionRoomMetrics")

    rh = await metrics.add_variable(idx, "RelativeHumidity", 45.0)
    temp = await metrics.add_variable(idx, "Temperature", 23.0)
    dp = await metrics.add_variable(idx, "DifferentialPressure", 15.0)
    ahu = await metrics.add_variable(idx, "AHUStatus", "RUNNING")
    press = await metrics.add_variable(idx, "TabletPressState", "EXECUTE")

    await rh.set_writable()
    await temp.set_writable()
    await dp.set_writable()
    await ahu.set_writable()
    await press.set_writable()

    async with server:
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_opcua_server())
