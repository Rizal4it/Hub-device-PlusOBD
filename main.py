import asyncio
import binascii
import struct
from datetime import datetime, timezone
import json
from mqtt import mqtt_connector
from typing import Dict, Any


class CRC16ARC:
    def __init__(self, polynomial=0xA001, initial_value=0x0000, final_xor=0x0000):
        self.polynomial = polynomial
        self.initial_value = initial_value
        self.final_xor = final_xor

    async def compute_crc(self, data: bytes) -> int:
        crc = self.initial_value
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ (self.polynomial if crc & 1 else 0)
            await asyncio.sleep(0)
        return crc ^ self.final_xor

    async def verify_crc(self, data: bytes, expected_crc: int) -> bool:
        calculated_crc = await self.compute_crc(data)
        return calculated_crc == expected_crc


class TeltonikaRawReader:

    def __init__(self, host="0.0.0.0", port=50020):
        self.host = host
        self.port = port
        self.crc = CRC16ARC()


    async def parse_avl_datacodec8(self, avl_content, num_data_1, imei, crc_data, crc_received):
        if not await self.crc.verify_crc(crc_data, crc_received):
            print(" CRC tidak valid untuk Codec 8.")
            return
        print("CRC valid untuk Codec 8.")


        payload = []
        offset = 0
        for i in range(num_data_1):
            if offset + 26 > len(avl_content):
                print(f"Data AVL ke-{i+1} tidak lengkap, berhenti parsing.")
                break

            timestamp_raw = struct.unpack(">Q", avl_content[offset:offset+8])[0]
            timestamp = datetime.fromtimestamp(timestamp_raw / 1000, tz=timezone.utc)

            priority = avl_content[offset+8]
            longitude = struct.unpack(">i", avl_content[offset+9:offset+13])[0] / 10000000
            latitude = struct.unpack(">i", avl_content[offset+13:offset+17])[0] / 10000000
            altitude = struct.unpack(">H", avl_content[offset+17:offset+19])[0]
            angle = struct.unpack(">H", avl_content[offset+19:offset+21])[0]
            satellites = avl_content[offset+21]
            speed = struct.unpack(">H", avl_content[offset+22:offset+24])[0]

            print(f"\nRecord {i+1} (IMEI: {imei}):")
            print(f"  Latitude: {latitude}")
            print(f"  Longitude: {longitude}")
            print(f"  Altitude: {altitude} m")
            print(f"  Angle: {angle}°")
            print(f"  Satellites: {satellites}")
            print(f"  Speed: {speed} km/h")

            data_record = {
            "imei": imei,
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "angle": angle,
            "satellites": satellites,
            "speed": speed
            }

            payload.append(data_record)

            offset += 26

        return payload
   
    async def parse_avl_data_codec8e(self, avl_content, num_data_1, imei, crc_data, crc_received):
        try:
            if not await self.crc.verify_crc(crc_data, crc_received):
                print("CRC tidak valid untuk Codec 8 Extended.")
                return
            print("CRC valid untuk Codec 8 Extended.")

            idx = 0
            payload = []  
            
            # Parsing setiap data
            for i in range(num_data_1):
                # Parsing timestamp

                timestamp_raw = int.from_bytes(avl_content[idx:idx+8], "big")
                timestamp = datetime.fromtimestamp(timestamp_raw / 1000, tz=timezone.utc)

                idx += 8

                # Parsing data lainnya
                priority = avl_content[idx]
                idx += 1

                longitude = int.from_bytes(avl_content[idx:idx+4], "big", signed=True) / 10**7
                idx += 4

                latitude = int.from_bytes(avl_content[idx:idx+4], "big", signed=True) / 10**7
                idx += 4

                altitude = int.from_bytes(avl_content[idx:idx+2], "big")
                idx += 2

                angle = int.from_bytes(avl_content[idx:idx+2], "big")
                idx += 2

                satellites = avl_content[idx]
                idx += 1

                speed = int.from_bytes(avl_content[idx:idx+2], "big")
                idx += 2

                event_io_id = int.from_bytes(avl_content[idx:idx+2], "big")
                idx += 2

                total_io = int.from_bytes(avl_content[idx:idx+2], "big")
                idx += 2

                # Menyusun data record ke dalam dictionary
                data_record = {
                    "imei": imei,
                    "timestamp": timestamp.isoformat(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude,
                    "angle": angle,
                    "satellites": satellites,
                    "speed": speed,
                    "event_io_id": event_io_id,
                    "total_io": total_io,
                    "io_data": [] 
                }

                # Parsing data IO berdasarkan tipe dan ukuran (1B, 2B, 4B, 8B)
                for io_type, size in [("1B", 1), ("2B", 2), ("4B", 4), ("8B", 8)]:
                    count = int.from_bytes(avl_content[idx:idx+2], "big")
                    idx += 2
                    io_list = []  # List untuk menyimpan data IO
                    for _ in range(count):
                        io_id = int.from_bytes(avl_content[idx:idx+2], "big")
                        value = int.from_bytes(avl_content[idx+2:idx+2+size], "big")
                        io_list.append({"io_id": io_id, "value": value})
                        idx += 2 + size
                    data_record["io_data"].append({io_type: io_list})

                # Parsing NX AVL Data
                count = int.from_bytes(avl_content[idx:idx+2], "big")
                idx += 2
                nx_data_list = [] 
                for _ in range(count):
                    io_id = int.from_bytes(avl_content[idx:idx+2], "big")
                    val_len = int.from_bytes(avl_content[idx+2:idx+4], "big")
                    value = int.from_bytes(avl_content[idx+4:idx+4+val_len], "big")
                    nx_data_list.append({"io_id": io_id, "value": value, "length": val_len})
                    idx += 4 + val_len
                data_record["nx_data"] = nx_data_list

                # Menambahkan record yang sudah diparse ke payload
                payload.append(data_record)


                print(f"\nExtended Record {i+1} (IMEI: {imei})")
                print(f"  Timestamp (UTC): {timestamp}")
                print(f"  Latitude: {latitude}")
                print(f"  Longitude: {longitude}")
                print(f"  Altitude: {altitude} m")
                print(f"  Angle: {angle}°")
                print(f"  Satellites: {satellites}")
                print(f"  Speed: {speed} km/h")
                print(f"  Event IO ID: {event_io_id}")
                print(f"  Total IO Elements: {total_io}")
                for io_type in ["1B", "2B", "4B", "8B"]:
                    for io in data_record["io_data"]:
                        if io_type in io:
                            for item in io[io_type]:
                                print(f"    IO ID: {item['io_id']}, Value: {item['value']}")
                for nx_item in data_record["nx_data"]:
                    print(f"    NX IO ID: {nx_item['io_id']}, Value: {nx_item['value']} (Length: {nx_item['length']})")

            return payload

        except Exception as e:
            print(f" Error saat parsing Codec 8 Extended: {e}")

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"\nKoneksi dari {addr}")

        try:
            imei_length = await reader.readexactly(2)
            imei = await reader.readexactly(int.from_bytes(imei_length, byteorder="big"))
            imei_str = imei.decode("utf-8")
            print(f"IMEI: {imei_str}")

            writer.write(b'\x01')
            await writer.drain()

            while True:
                raw_data = await reader.read(2048)
                if not raw_data:
                    print("Tidak ada data setelah IMEI!")
                    break

                print("\nData diterima (hex):")
                print(binascii.hexlify(raw_data).decode())

                if len(raw_data) >= 8:
                    data_field_length = struct.unpack(">I", raw_data[4:8])[0]
                    print(f"\nData Field Length: {data_field_length} bytes")

                    avl_data = raw_data[8:]
                    if len(avl_data) >= data_field_length:
                        codec_id = avl_data[0]
                        num_data_1 = avl_data[1]
                        num_data_2 = avl_data[-5]
                        crc_received = struct.unpack(">I", avl_data[-4:])[0]

                        print(f"Codec ID: {hex(codec_id)}")
                        print(f"Number of Data 1: {num_data_1}")
                        print(f"Number of Data 2: {num_data_2}")
                        print(f"CRC Diterima: {hex(crc_received)}")

                        avl_content = avl_data[2:-5]
                        crc_data = avl_data[:-4]

                        if codec_id == 0x08:
                            task = asyncio.create_task(self.parse_avl_datacodec8(avl_content, num_data_1, imei_str, crc_data, crc_received))
                        elif codec_id == 0x8E:
                            task = asyncio.create_task(self.parse_avl_data_codec8e(avl_content, num_data_1, imei_str, crc_data, crc_received))                       
                        else:
                            print(f"Codec ID {hex(codec_id)} tidak dikenali.")

                        parsed_data = await task
                        mqtt_payload = []
                        for avl_data in parsed_data:
                            mapped_data = self.map_teltonika_to_json_payload(imei_str, avl_data)
                            mqtt_payload.append(mapped_data)

                        mqtt_payload_json = json.dumps(mqtt_payload)
                        await mqtt_connector.publish("topic/data", mqtt_payload_json)

                        ack_response = struct.pack(">I", num_data_1)
                        writer.write(ack_response)
                        print( num_data_1)
                        await writer.drain()
                    else:
                        print("Data AVL tidak cukup panjang!")
        except asyncio.IncompleteReadError:
            print(f"Data tidak lengkap dari {addr}. Koneksi ditutup.")
        except Exception as e:
            print(f"Error: {e}")

        print(f"Koneksi dari {addr} ditutup\n")
        writer.close()
        await writer.wait_closed()
    

    @staticmethod
    def map_teltonika_to_json_payload(imei: str, data_avl: Dict[str, Any]) -> Dict[str, Any]:
        def get_value(io_map, key, default=0):
            if isinstance(key, int):
                for io_group in io_map.get("io_data", []):
                    for io_type, io_values in io_group.items():
                        for io in io_values:
                            if io.get('io_id') == key:
                                return io.get('value', default)
            return io_map.get(key, default)

        # Nilai default
        payload = {
            "imei": imei,
            "timestamp": data_avl.get("timestamp", "1970-01-01T00:00:00+00:00"),
            "latitude": data_avl.get("latitude", 0.0),
            "longitude": data_avl.get("longitude", 0.0),
            "altitude": data_avl.get("altitude", 0),
            "angle": data_avl.get("angle", 0),
            "speed": data_avl.get("speed", 0),
            "battery_voltage": get_value(data_avl, 67, 0),  # Ambil nilai dari io_id 67
            "power_input": get_value(data_avl, 66, 0),  # Ambil nilai dari io_id 66
            "fuel_level": get_value(data_avl, 9, 0),  # Ambil nilai dari io_id 9
            "total_odometer": get_value(data_avl, 16, 0),  # Ambil nilai dari io_id 16
            "fuel_used_gps": get_value(data_avl, 12, 0),  # Ambil nilai dari io_id 12
            "fuel_rate_gps": get_value(data_avl, 13, 0),  # Ambil nilai dari io_id 13
            "operate_status": bool(get_value(data_avl, 1, 0)),  # Ambil nilai dari io_id 1
            "digital_input_2": bool(get_value(data_avl, 2, 0)),  # Ambil nilai dari io_id 2
            "gsm_signal": get_value(data_avl, 21, 0),  # Ambil nilai dari io_id 21
            "ignition_on_counter": get_value(data_avl, 449, 0),  # Ambil nilai dari io_id 449
            "data_payload": data_avl  # Menyertakan data_avl yang asli dalam payload
        }

        return payload




    async def start_server(self):
        await mqtt_connector.connect()
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"Server berjalan di {addr}")
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    server = TeltonikaRawReader()