from utils.gmail_auth import get_gmail_service
from datetime import datetime, timedelta
import base64
import email
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")


def current_epoch_window(tz=NY):
    start_local = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)
    return int(start_local.timestamp()), int(end_local.timestamp())

def get_today_date_query():
    today, tomorrow = current_epoch_window()
    # Gmail query: after today 00:00, before tomorrow 00:00
    return f"category:primary in:inbox after:{today} before:{tomorrow}"


def fetch_today_emails(max_results=10):
    service = get_gmail_service()
    query = get_today_date_query()
    print(f"Querying emails with query: {query}")

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query, maxResults=10).execute()
    
    messages = results.get('messages', [])
    if not messages:
        return []
    
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == "Date"), datetime.today())

        body = ''

        payload = msg_data['payload']
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        emails.append({
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'id': msg_data.get("id")  # Include email ID if needed
        })

    return emails