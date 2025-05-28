from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = Credentials.from_service_account_file(
        'credentials.json',
        scopes = SCOPES
    )

    service = build('calendar', 'v3', credentials=creds)
    return service