from subscriber import RedisSubscriber
class EmailNotificationSubscriber(RedisSubscriber):

    def handle_message(self, message):
        # Process the message and send an email notification
        email_content = f"New message received: {message}"
        self.email_service.send_email(email_content)