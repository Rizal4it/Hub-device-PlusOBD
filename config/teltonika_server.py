import asyncio
from config.config import Config
from controller.teltonika_server import teltonika_controller


class TeltonikaServer:
    async def begin(self):
        self.server = await asyncio.start_server(teltonika_controller.tcp_callback, Config.TCP_SERVER_HOST, Config.TCP_SERVER_PORT)

    async def start_server(self):
        if self.server:
            async with self.server:
                print(f"Server berjalan di {Config.TCP_SERVER_HOST} dengan port {Config.TCP_SERVER_PORT}")
                await self.server.serve_forever()

    async def close_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()


teltonika_server = TeltonikaServer()
