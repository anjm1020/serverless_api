import datetime
import time

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


def get_file_list(credentials: Credentials):
    # Get entire file list
    # only user drive, before 1 year
    service = build("drive", "v3", credentials=credentials)

    pageToken = None
    files = []
    while True:
        limited_time_mark = datetime.datetime.now() - datetime.timedelta(days=365)
        limited_time_mark = time.strftime("%Y-%m-%dT%H:%M:%S")
        response = (
            service.files()
            .list(
                q=f"trashed=false and ( modifiredTime < {limited_time_mark} or createdTime < {limited_time_mark} )",
                corpora="user",
                size=1000,
                spaces="drive",
                fields="nextPageToken, files(id, name, fileExtension, contentHints, webViewLink, webContentLink, thumbnailLink, mimeType)",
                pageToken=pageToken,
            )
            .execute()
        )
        files.extend(response.get("files", []))
        pageToken = response.get("nextPageToken", None)
        if pageToken is None:
            break
    return files
