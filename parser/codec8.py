import asyncio
import struct
from datetime import datetime, timezone
from utils.crc import CRC16ARC

class ParseRawCodec8:
    async def parse_codec8(self, avl_content, num_data_1, imei, crc_data, crc_received):
        if not await CRC16ARC.verify_crc(crc_data, crc_received):
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
                "timestamp": timestamp.isoformat(),  
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
