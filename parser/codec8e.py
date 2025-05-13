import datetime
from utils.crc import CRC16ARC
from datetime import datetime, timezone

class ParseRawCodec8e :

    async def parse_avl_data_codec8e(self, avl_content, num_data_1, imei, crc_data, crc_received):
            try:
                if not await CRC16ARC.verify_crc(crc_data, crc_received):
                    print("CRC tidak valid untuk Codec 8 Extended.")
                    return
                print("CRC valid untuk Codec 8 Extended.")

                idx = 0
                payload = []  
                
                for i in range(num_data_1):

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