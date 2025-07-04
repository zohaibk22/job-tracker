import os
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


SCOPE=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CRED_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "credentials/service_account.json")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")

def init_sheet_client():
    """
    Initialize the Google Sheets client using service account credentials.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, SCOPE)
    client = gspread.authorize(credentials)
    return client

def is_duplicate(message_id: str, sheet) -> bool:

    id_col = sheet.col_values(5)
    print(id_col, "-----ID COL-----")
    return message_id in id_col


def write_to_sheet(email_data: dict) -> None:
    """
    Writes email data to a Google Sheet.

    Args:
        email_data (dict): A dictionary containing email information. Expected keys include
            'submission_date', 'company', and 'job_title'.

    Functionality:
        - Initializes a Google Sheets client.
        - Opens the target sheet using a predefined SHEET_ID and SHEET_NAME.
        - Extracts the submission date from email_data or uses the current date if not provided.
        - Prepares a row with the date, company, and job title.
        - Appends the row to the sheet using 'USER_ENTERED' value input option.
    """
    print("IN GOOGLE SHEETS INPUT AGENT 🚀")
    client = init_sheet_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    email_id: str = email_data.get('email_id', '')
    if is_duplicate(email_id, sheet):
        print(f"Email with ID {email_id} already exists in the sheet. Skipping write.")
        return

    date_str: str = email_data.get('submission_date') or datetime.now().date().isoformat()
    row: list = [
        date_str,
        email_data.get('company', ''),
        email_data.get('job_title', ''),
        email_data.get('status', 'test'),  # Default to 'New' if status is not provided
        email_id  # Include email ID if needed
    ]

    print(f"--------------📄 Writing to Google Sheet: {row} -------------")

    try:
     
        sheet.append_row(row, value_input_option='USER_ENTERED')

    except gspread.exceptions.APIError as e:
        print(f"❌ Error writing to Google Sheet: {e}")
        raise e
