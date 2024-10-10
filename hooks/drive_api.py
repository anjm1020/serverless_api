import datetime

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from hooks.ssm_api import ParamRequest, get_parameters


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
    service = build("drive", "v3", credentials=credentials)

    pageToken = None
    files = []
    while True:
        limited_time_mark = (
            datetime.datetime.now() - datetime.timedelta(days=365)
        ).isoformat() + "Z"

        response = (
            service.files()
            .list(
                q=f"trashed=false and (modifiedTime < '{limited_time_mark}' or createdTime < '{limited_time_mark}')",
                corpora="user",
                pageSize=1000,
                spaces="drive",
                fields="nextPageToken, files(id, name, fileExtension, webContentLink, mimeType, size)",
                pageToken=pageToken,
            )
            .execute()
        )
        files.extend(response.get("files", []))
        pageToken = response.get("nextPageToken", None)
        if pageToken is None:
            break
    return files


def segmentation(file_list) -> tuple:

    required_params: list[ParamRequest] = [
        ParamRequest(
            name="supproted_extensions",
            key="/findy/config/supported_extensions",
            type="string",
        )
    ]

    params = get_parameters(required_params=required_params)
    supported_extensions = params["supproted_extensions"].split(" ")
    print(f"supported_extensions: {supported_extensions}")
    processable_data = []
    non_processable_data = []
    for curr in file_list:
        if (
            "fileExtension" not in curr
            or curr["fileExtension"] not in supported_extensions
        ):
            non_processable_data.append(curr)
        else:
            processable_data.append(curr)

    return processable_data, non_processable_data
