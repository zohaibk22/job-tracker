import os
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional


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
    return message_id in id_col


def write_to_sheet(email_data: dict, sheet_data_cache: Optional[dict] = None) -> str:
    """
    Writes email data to a Google Sheet.

    Args:
        email_data (dict): A dictionary containing email information. Expected keys include
            'submission_date', 'company', and 'job_title'.
        sheet_data_cache (dict): Optional cached sheet data to avoid redundant API calls.

    Functionality:
        - Initializes a Google Sheets client.
        - Opens the target sheet using a predefined SHEET_ID and SHEET_NAME.
        - Extracts the submission date from email_data or uses the current date if not provided.
        - Prepares a row with the date, company, and job title.
        - Appends the row to the sheet using 'USER_ENTERED' value input option.
        
    """
    client = init_sheet_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    email_id: str = email_data.get('email_id', '')
    
    # Use cached data if available, otherwise check sheet
    if sheet_data_cache and email_id in sheet_data_cache.get('email_ids', set()):
        return f"Duplicate: {email_data.get('company', '')} - {email_data.get('job_title', '')}"
    elif not sheet_data_cache and is_duplicate(email_id, sheet):
        return f"Duplicate: {email_data.get('company', '')} - {email_data.get('job_title', '')}"

    date_str: str = email_data.get('submission_date') or datetime.now().date().isoformat()
    row: list = [
        date_str,
        email_data.get('company', ''),
        email_data.get('job_title', ''),
        email_data.get('status', 'test'),  # Default to 'New' if status is not provided
        email_id  # Include email ID if needed
    ]
    try:
     
        sheet.append_row(row, value_input_option='USER_ENTERED')
        return f"applied to {email_data.get('company', '')} - {email_data.get('job_title', '')}"

    except gspread.exceptions.APIError as e:
        print(f"❌ Error writing to Google Sheet: {e}")
        raise e
