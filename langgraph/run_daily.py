from main import main 
import os, base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

 # or your one-shot function

cred_dir = Path('/app/credentials')
cred_dir.mkdir(parents=True, exist_ok=True)

cred_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
if cred_json:
    (cred_dir / 'credentials.json').write_text(cred_json)

cred_service_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
if cred_service_json:
    (cred_dir / 'service_account.json').write_text(cred_service_json)

token_b64 = os.getenv('GMAIL_TOKEN_PKL_BASE64')
if token_b64:
    with open(cred_dir / 'token.pkl', 'wb') as f:
        f.write(base64.b64decode(token_b64))


if __name__ == "__main__":
    main()