import asyncio
import logging
from config.teltonika_server import teltonika_server
from config.mqtt import mqtt_connector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting Teltonika Server...")
        await mqtt_connector.connect()
        await teltonika_server.begin()
        await teltonika_server.start_server()
    except KeyboardInterrupt:
        logger.info("System stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())