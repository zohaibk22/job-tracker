# langgraph/utils/gmail_auth.py
import os
import pickle
import pathlib
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google. auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    token_path = pathlib.Path(os.getenv("TOKEN_PATH", "credentials/token.pkl"))
    credentials_path = pathlib.Path(os.getenv("CREDS_PATH", "credentials/credentials.json"))
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

    if token_path.exists():
        with token_path. open('rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing expired Gmail token...")
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
                
                # Save refreshed token
                with token_path.open('wb') as token:
                    pickle.dump(creds, token)
                    
            except RefreshError as e: 
                print(f"❌ Token refresh failed: {e}")
                
                if is_ci:
                    print("\n" + "="*60)
                    print("⚠️  GMAIL TOKEN REFRESH FAILED IN CI")
                    print("="*60)
                    print("\nYour refresh token is expired or revoked.")
                    print("\n📋 TO FIX:")
                    print("1. Run authentication locally:")
                    print("   cd langgraph")
                    print("   python3 -c 'from utils.gmail_auth import get_gmail_service; get_gmail_service()'")
                    print("\n2. Encode the new token:")
                    print("   base64 credentials/token.pkl | tr -d '\\n'")
                    print("\n3. Update GitHub Secret GMAIL_TOKEN_PKL_BASE64 with the output")
                    print("="*60 + "\n")
                    raise RuntimeError("Gmail token refresh failed.  Manual re-authentication required. ") from e
                else: 
                    # Local environment - attempt browser auth
                    print("⚠️ Attempting browser-based re-authentication...")
                    raise RefreshError("No valid refresh token, starting re-authentication.")
        else:
            if is_ci:
                print("\n" + "="*60)
                print("❌ NO VALID GMAIL CREDENTIALS FOUND IN CI")
                print("="*60)
                print("\nNo valid refresh token available.")
                print("\n📋 TO FIX:  Follow steps above to generate and upload a new token.")
                print("="*60 + "\n")
                raise RuntimeError("No valid Gmail credentials.  Manual authentication required.")
            else:
                raise RefreshError("No valid refresh token, starting re-authentication.")

        # Browser-based auth (only runs locally)
        if not is_ci:
            print("⚠️ Starting browser-based authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
            
            with token_path.open('wb') as token:
                pickle.dump(creds, token)
                
            # Print the base64 for GitHub secret
            with token_path.open('rb') as token:
                token_b64 = base64.b64encode(token.read()).decode('utf-8')
                print("\n" + "="*60)
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print("="*60)
                print("\n📋 UPDATE GITHUB SECRET 'GMAIL_TOKEN_PKL_BASE64' WITH:")
                print(f"\n{token_b64}\n")
                print("="*60 + "\n")

    return build("gmail", "v1", credentials=creds)
