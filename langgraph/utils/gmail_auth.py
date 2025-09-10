import os
import pickle
import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
def get_gmail_service():
    creds = None
    token_path=pathlib.Path("credentials/token.pkl")
    credentials_path = pathlib.Path("credentials/credentials.json")

    if token_path.exists():
        with token_path.open('rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        try:

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RefreshError("No valid refresh token, starting re-authentication.")
                # flow = InstalledAppFlow.from_client_secrets_file(
                #     str(credentials_path), SCOPES)
                # creds = flow.run_local_server(port=0)
        except RefreshError:
            print("⚠️ Token expired or revoked, re-authenticating...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)


        with token_path.open('wb') as token:
            pickle.dump(creds, token)
        
    return build("gmail", "v1", credentials=creds)






