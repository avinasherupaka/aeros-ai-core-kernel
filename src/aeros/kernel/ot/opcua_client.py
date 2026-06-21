import asyncio

from asyncua import Client


async def read_node_value(endpoint: str, node_id: str):
    async with Client(url=endpoint) as client:
        node = client.get_node(node_id)
        return await node.read_value()


if __name__ == "__main__":
    print(asyncio.run(read_node_value("opc.tcp://localhost:4840/freeopcua/server/", "i=85")))
