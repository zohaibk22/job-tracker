import yagmail
from dotenv import load_dotenv
import os
import time
from datetime import datetime as dt


from subscriber import RedisSubscriber
import traceback
load_dotenv()

class EmailNotificationSubscriber(RedisSubscriber):

    def format_email_content(self, message):
        """Format the message data into structured HTML email content."""
        timestamp = dt.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Build HTML email structure (single line to prevent yagmail from converting newlines to <br>)
        html_content = f'<html><head><style>body {{font-family: Arial, sans-serif; line-height: 1.6; color: #333;}} .header {{background-color: #4CAF50; color: white; padding: 20px; text-align: center;}} .content {{padding: 20px; background-color: #f9f9f9;}} .section {{background-color: white; margin: 15px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}} .label {{font-weight: bold; color: #4CAF50;}} .timestamp {{color: #666; font-size: 0.9em; font-style: italic;}} .item {{padding: 10px; margin: 5px 0; background-color: #f5f5f5; border-left: 3px solid #4CAF50;}} .footer {{text-align: center; padding: 20px; color: #666; font-size: 0.85em;}}</style></head><body><div class="header"><h2>Job Application Status Update</h2></div><div class="content"><div class="section"><p class="timestamp">Received: {timestamp}</p></div><div class="section"><h3 class="label">Message Details:</h3>'
        
        # Add message items
        if isinstance(message, (list, tuple)):
            html_content += f"<p><strong>Total Items:</strong> {len(message)}</p>"
            for idx, item in enumerate(message, 1):
                html_content += f'<div class="item"><strong>Item {idx}:</strong> {item}</div>'
        elif isinstance(message, dict):
            for key, value in message.items():
                html_content += f'<div class="item"><strong>{key}:</strong> {value}</div>'
        else:
            html_content += f'<div class="item">{message}</div>'
        
        # Close HTML structure
        html_content += '</div></div><div class="footer"><p>This is an automated notification from your job application monitoring system.</p></div></body></html>'
        
        return html_content

    def handle_message(self, message):
        email_content = f"New message received: {message}"
        sender_email= os.getenv('SENDER_EMAIL')
        receiver_email = os.getenv('RECEIVER_EMAIL')
        subject = f"Zohaib Job Application Status for {dt.now().strftime('%Y-%m-%d')}"
        
        # Format the content into structured HTML
        content = self.format_email_content(message)

        try:
            yag = yagmail.SMTP(user=sender_email, password=os.getenv("SENDER_EMAIL_PASSWORD"))
            yag.send(to=receiver_email, subject=subject, contents=content)
            print(f"Email sent successfully to {receiver_email}")
        
        except Exception as e:
            print(f"Failed to send email notification.\n"
              f"Sender: {sender_email}\n"
              f"Receiver: {receiver_email}\n"
              f"Subject: {subject}\n"
              f"Error: {e}")
            traceback.print_exc()
            return