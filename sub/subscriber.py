import redis
from abc import ABC, abstractmethod

from dotenv import load_dotenv
import os
load_dotenv()

class RedisSubscriber(ABC):
    def __init__(self, channel):
        self.channel = channel
        self.redis = redis.Redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379/0'))
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel)

    @abstractmethod
    def handle_message(self, message):
        """Override this method for custom logic."""
        print(f"Custom handling of message: {message}")

    def listen(self):
        print(f"Listening for messages on channel: {self.channel}")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                print(f"Received message: {message['data']}")
                self.handle_message(message['data'].decode('utf-8'))