from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_profile(credentials: Credentials):
    try:
        print("Start get profile")
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        print(f"Response Profile: {profile}")
        return profile

    except RefreshError as e:
        print(f"Token expired or invalid: {e}")
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
