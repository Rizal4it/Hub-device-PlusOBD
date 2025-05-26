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
            "engine_load": get_value(data_avl, 31, 0),  # Engine Load (sebelumnya 52)
            "coolant_temp": get_value(data_avl, 32, 0),  # Engine Coolant Temperature (sebelumnya 72)
            "short_fuel_trim": get_value(data_avl, 33, 0),
            "fuel_pressure": get_value(data_avl, 34, 0),
            "intake_map": get_value(data_avl, 35, 0),
            "engine_rpm": get_value(data_avl, 36, 0),  # RPM
            "vehicle_speed": get_value(data_avl, 37, 0),  # Vehicle Speed (sebelumnya 24)
            "timing_advance": get_value(data_avl, 38, 0),
            "intake_air_temp": get_value(data_avl, 39, 0),  # Intake Air Temperature (sebelumnya 73)
            "maf": get_value(data_avl, 40, 0),
            "throttle_position": get_value(data_avl, 41, 0),  # Throttle Position
            "run_time_since_engine_start": get_value(data_avl, 42, 0),
            "distance_traveled_mil_on": get_value(data_avl, 43, 0),
            "relative_fuel_rail_pressure": get_value(data_avl, 44, 0),
            "direct_fuel_rail_pressure": get_value(data_avl, 45, 0),
            "commanded_egr": get_value(data_avl, 46, 0),
            "egr_error": get_value(data_avl, 47, 0),
            # Parameter OBD yang baru ditambahkan
            "number_of_dtc": get_value(data_avl, 30, 0),
            "distance_traveled_since_codes_clear": get_value(data_avl, 49, 0),
            "control_module_voltage": get_value(data_avl, 51, 0),  # Control Module Voltage (sebelumnya 200)
            "absolute_load_value": get_value(data_avl, 52, 0),
            "ambient_air_temperature": get_value(data_avl, 53, 0),
            "time_run_with_mil_on": get_value(data_avl, 54, 0),
            "time_since_trouble_codes_cleared": get_value(data_avl, 55, 0),
            "fuel_type": get_value(data_avl, 759, 0),
            "hybrid_battery_pack_remaining_life": get_value(data_avl, 57, 0),
            "engine_oil_temperature": get_value(data_avl, 58, 0),
            "fuel_injection_timing": get_value(data_avl, 59, 0),
            "fuel_rate": get_value(data_avl, 60, 0),
            "data_payload": data_avl  # Menyertakan data_avl yang asli dalam payload
        }

        return payload
