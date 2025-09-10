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