import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Chess Vision Service (AVS) started.")
    try:
        while True:
            logger.info("AVS heartbeat - waiting for camera feed...")
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Chess Vision Service stopping...")

if __name__ == "__main__":
    main()
