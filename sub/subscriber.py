import redis

# def send_email_notification(message):
#     print(f"Sending email notification: {message}")
          


class RedisSubscriber:
    def __init__(self, channel):
        self.channel = channel
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel)

    def handle_message(self, message):
        """Override this method for custom logic."""
        print(f"Custom handling of message: {message}")

    def listen(self):
        print(f"Listening for messages on channel: {self.channel}")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                print(f"Received message: {message['data']}")
                self.handle_message(message['data'].decode('utf-8'))