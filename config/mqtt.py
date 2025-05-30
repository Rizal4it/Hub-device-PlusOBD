import asyncio
import time
import aiomqtt
from config.config import Config

class MQTTConnector:
    def __init__(self):
        self.host = Config.MQTT_HOST
        self.port = Config.MQTT_PORT
        self.client = None  
        self.connected = asyncio.Event()  

    async def connect(self):
        while True:
            try:
                self.client = aiomqtt.Client(self.host, port=self.port)
                await self.client.__aenter__()  
                self.connected.set()
                print(f"Terhubung ke MQTT Broker: {self.host}:{self.port}")
                return  
            except aiomqtt.MqttError as e:
                print(f"Gagal terhubung ke MQTT: {e}. Mencoba lagi dalam 5 detik...")
                self.connected.clear()
                await asyncio.sleep(5)

    import time  # Tambahkan import ini
    async def publish(self, topic, payload):
        await self.connected.wait()  
        try:
            start_time = time.time()  # Catat waktu sebelum publish
            await self.client.publish(topic, payload)
            end_time = time.time()  # Catat waktu setelah publish
            print(f"Published: {payload} to topic: {topic}")
            print(f"Time taken to publish: {end_time - start_time} seconds")  # Log waktu yang diambil
        except aiomqtt.MqttError as e:
            print(f"MQTT error saat publish: {e}")

mqtt_connector = MQTTConnector()