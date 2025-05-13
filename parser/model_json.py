import json
from typing import Dict, Any

class TeltonikaPayloadMapper:
    
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

        # Nilai default untuk payload
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
