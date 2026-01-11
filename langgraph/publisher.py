import redis
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, channel):
        self.channel = channel
        self.redis = redis.Redis.from_url(os.getenv('REDIS_URL'))

    def publish(self, message):
        self.redis.publish(self.channel, message)
        logger.info(f"[PUBLISH] {message} -> {self.channel}")
        