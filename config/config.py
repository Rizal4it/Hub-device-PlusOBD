from dotenv import load_dotenv
import os

def load_env():
    load_dotenv(override=True)

load_env()  

class Config:
    TCP_SERVER_HOST = os.getenv("TCP_SERVER_HOST", "0.0.0.0")
    TCP_SERVER_PORT = int(os.getenv("TCP_SERVER_PORT", "50000"))

    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
