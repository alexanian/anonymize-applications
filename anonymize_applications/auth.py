import pickle
import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .config import SCOPES


def get_credentials(token_path: str = "token.pickle", credentials_path: str = "credentials.json"):
    """
    This is taken directly from the Google API quickstart guide, since they presumably know the
    right approach to authenticating.

    :param credentials_path: path to JSON file containing Google Sheets API credentials.
    :param token_path: the token pickle file stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first time.
    :returns: google.oauth2.credentials.Credentials object.
    """
    creds = None
    # If a token pickle file already exists, read it.
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds
