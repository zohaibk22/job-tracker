import yagmail
from dotenv import load_dotenv
import os
import time
from datetime import datetime as dt


from subscriber import RedisSubscriber
import traceback
load_dotenv()

class EmailNotificationSubscriber(RedisSubscriber):

    def handle_message(self, message):
        email_content = f"New message received: {message}"
        print(email_content)
        sender_email= os.getenv('SENDER_EMAIL')
        receiver_email = os.getenv('RECEIVER_EMAIL')
        subject = f"Zohaib Job Application Status for {dt.now().strftime('%Y-%m-%d')}"
        content = message

        try:
            yag = yagmail.SMTP(user=sender_email, password=os.getenv("SENDER_EMAIL_PASSWORD"))
            yag.send(to=receiver_email, subject=subject, contents=content)
        
        except Exception as e:
            print(f"Failed to send email notification.\n"
              f"Sender: {sender_email}\n"
              f"Receiver: {receiver_email}\n"
              f"Subject: {subject}\n"
              f"Error: {e}")
            traceback.print_exc()
            return