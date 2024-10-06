from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_profile(credentials: Credentials):
    try:
        print("Start get Drive profile")
        service = build("drive", "v3", credentials=credentials)
        profile = service.about().get(fields="user").execute()
        print(f"Response Drive Profile: {profile}")
        return profile

    except RefreshError as e:
        print(f"Token expired or invalid: {e}")
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
