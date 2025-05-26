import asyncio
from config.teltonika_server import teltonika_server
from config.mqtt import mqtt_connector


async def main():
    try:
        await mqtt_connector.connect()
        await teltonika_server.begin()
        await teltonika_server.start_server()
    except KeyboardInterrupt:
        print("stop system")

asyncio.run(main())