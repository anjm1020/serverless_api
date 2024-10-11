from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from entity.accessible_data import AccessibleData
from entity.formatted_data import FormattedData

_MAX_MAIL_LENGTH = 2000


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


def get_mail_and_attachments_list(credentials: Credentials):
    service = build("gmail", "v1", credentials=credentials)

    pageToken = None
    mails = []
    while True:
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                pageToken=pageToken,
                maxResults=500,
                includeSpamTrash=False,
                q="in:inbox newer_than:1y",
            )
            .execute()
        )
        mails.extend(response.get("messages", []))

        if len(mails) >= _MAX_MAIL_LENGTH:
            mails = mails[:_MAX_MAIL_LENGTH]
            break

        pageToken = response.get("nextPageToken", None)
        if pageToken is None:
            break
    return mails


def segmentation(entire_list) -> tuple[list[AccessibleData], list[FormattedData]]:
    # All mail have to process
    return [AccessibleData(access_info=mail) for mail in entire_list], []
