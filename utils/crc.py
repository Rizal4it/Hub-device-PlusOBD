import asyncio

class CRC16ARC:
   
    polynomial = 0xA001
    initial_value = 0x0000
    final_xor = 0x0000

    @staticmethod
    async def compute_crc(data: bytes) -> int:
        crc = CRC16ARC.initial_value  
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ (CRC16ARC.polynomial if crc & 1 else 0)
            await asyncio.sleep(0)
        return crc ^ CRC16ARC.final_xor
    
    @staticmethod
    async def verify_crc(data: bytes, expected_crc: int) -> bool:
        calculated_crc = await CRC16ARC.compute_crc(data)
        return calculated_crc == expected_crc
