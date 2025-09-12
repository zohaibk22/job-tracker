import redis
from dotenv import load_dotenv
import os

class EventPublisher:
    def __init__(self, channel):
        self.channel = channel
        self.redis = redis.Redis.from_url(os.getenv('REDIS_URL'))

    def publish(self, message):
        self.redis.publish(self.channel, message)
        print(f"[PUBLISH] {message} -> {self.channel}")
        