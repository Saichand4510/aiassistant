from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    # 🔥 For Render (ENV)
    creds_json = os.getenv("GOOGLE_CREDS")

    if creds_json:
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
    else:
        # 🔥 For local (JSON file)
        credentials = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "service_account.json"),
    scopes=SCOPES
)

    service = build("calendar", "v3", credentials=credentials)
    return service