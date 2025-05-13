import asyncio
import struct
import json
from datetime import datetime, timezone, timedelta
from parser.codec8 import ParseRawCodec8
from parser.codec8e import ParseRawCodec8e
from parser.model_json import TeltonikaPayloadMapper
from config.mqtt import mqtt_connector


class TeltonikaHandler:
    def __init__(self):
        self.payload_mapper = TeltonikaPayloadMapper()

    async def handle_raw_data(self, raw_data: bytes, imei_str: str, writer):
        if len(raw_data) >= 8:
            data_field_length = struct.unpack(">I", raw_data[4:8])[0]
            print(f"\nData Field Length: {data_field_length} bytes")

            avl_data = raw_data[8:]
            if len(avl_data) >= data_field_length:
                codec_id = avl_data[0]
                num_data_1 = avl_data[1]

                crc_received = struct.unpack(">I", avl_data[-4:])[0]

                avl_content = avl_data[2:-5]
                crc_data = avl_data[:-4]

                if codec_id == 0x08:
                    task = asyncio.create_task(ParseRawCodec8.parse_codec8(self,avl_content, num_data_1, imei_str, crc_data, crc_received))
                elif codec_id == 0x8E:
                    task = asyncio.create_task(ParseRawCodec8e.parse_avl_data_codec8e(self,avl_content, num_data_1, imei_str, crc_data, crc_received))
                else:
                    print(f"Codec ID {hex(codec_id)} tidak dikenali.")
                    return None

                parsed_data = await task

            mqtt_payload = []
            for data in parsed_data:
                #if not await self.is_valid_avl_data(data):
                 # continue  

                mapped_data = TeltonikaPayloadMapper.map_teltonika_to_json_payload(imei_str, data)
                mqtt_payload.append(mapped_data)

            if mqtt_payload:
                mqtt_payload_json = json.dumps(mqtt_payload)
                await mqtt_connector.publish("topic/data", mqtt_payload_json)

            return num_data_1

        return None
    
    async def is_valid_avl_data(self, data: dict) -> bool:
        if data.get("latitude") == 0.0 and data.get("longitude") == 0.0:
            print(f"log not inserted. device initializing position at latitude {data['latitude']}, longitude {data['longitude']}")
            return False

        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                if timestamp >= datetime.now(timezone.utc) + timedelta(days=1):
                    print("log not inserted. timestamp on device not initialized")
                    return False
            except Exception as e:
                print(f"timestamp parse error: {e}")
                return False

        return True
