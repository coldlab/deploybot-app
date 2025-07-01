from typing import Optional, List
from google.oauth2 import service_account
from google.auth.credentials import Credentials
import google.auth
import os

def get_credentials(scopes: Optional[List[str]] = None) -> Credentials:
    scopes = scopes if scopes is not None else ['https://www.googleapis.com/auth/cloud-platform']

    service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if service_account_file is None:
        credentials, project = google.auth.default(scopes=scopes)
        if not isinstance(credentials, Credentials):
            raise ValueError("Default credentials are not compatible with the required Google Auth credentials type.")
        return credentials
    
    return service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes
    )
