
import redis

class EventPublisher:
    def __init__(self, channel):
        self.channel = channel
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def publish(self, message):
        self.redis.publish(self.channel, message)
        print(f"[PUBLISH] {message} -> {self.channel}")
        