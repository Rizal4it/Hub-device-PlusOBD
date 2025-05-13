import asyncio
import struct
from service.teltonika_server import TeltonikaHandler


class TeltonikaServerController:

    def __init__(self):
        self.teltonika_handler = TeltonikaHandler()  

    async def tcp_callback(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Koneksi dari {addr}")

        try:
            imei_length = await reader.readexactly(2)
            imei = await reader.readexactly(int.from_bytes(imei_length, byteorder="big"))
            imei_str = imei.decode("utf-8")
            print(f"IMEI: {imei_str}")
            writer.write(b'\x01')
            await writer.drain()
            while True:
                try:
                    raw_data = await asyncio.wait_for(reader.read(2048), timeout=20)
                    if not raw_data:
                        print("Tidak ada data setelah IMEI!")
                        break
                    
                    num_data_1 = await self.teltonika_handler.handle_raw_data(raw_data, imei_str, writer)

                    if num_data_1 is not None:
                        ack_response = struct.pack(">I", num_data_1)
                        writer.write(ack_response)
                        await writer.drain()
                        print(f"ACK dikirim dengan nilai: {num_data_1}")
                    else:
                        print("Data tidak valid, tidak mengirimkan ACK.")
                        break

                except asyncio.TimeoutError:
                    print(f"Timeout: Tidak ada data diterima dari {addr} dalam waktu yang ditentukan.")
                    break

        except asyncio.IncompleteReadError:
            print(f"Data tidak lengkap dari {addr}. Koneksi ditutup.")
        finally:
            print(f"Koneksi dari {addr} ditutup\n")
            writer.close()
            await writer.wait_closed()

teltonika_controller = TeltonikaServerController()