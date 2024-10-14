import io
import datetime

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from entity.accessible_data import AccessibleData
from entity.formatted_data import FormattedData
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
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="max_length",
            key="/findy/config/google_drive_max_length",
            type="int",
        )
    ]
    params = get_parameters(required_params=required_params)
    max_length = int(params["max_length"])

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
                fields="nextPageToken, files(id, name, fileExtension, createdTime, modifiedTime, webViewLink, webContentLink, mimeType, size)",
                pageToken=pageToken,
            )
            .execute()
        )
        files.extend(response.get("files", []))
        if len(files) >= max_length:
            files = files[:max_length]
            break
        pageToken = response.get("nextPageToken", None)
        if pageToken is None:
            break
    return files


def segmentation(file_list) -> tuple[list[AccessibleData], list[FormattedData]]:

    required_params: list[ParamRequest] = [
        ParamRequest(
            name="supproted_extensions",
            key="/findy/config/supported_extensions",
            type="string",
        )
    ]

    params = get_parameters(required_params=required_params)
    supported_extensions = params["supproted_extensions"].split(" ")

    processable_data: list[AccessibleData] = []
    non_processable_data: list[FormattedData] = []
    for curr in file_list:

        # TODO
        # mimeType mapper
        # (e.g. "application/vnd.google-apps.document" -> "google-docx")
        formatted_data: FormattedData = FormattedData.non_processable_data(
            title=curr["name"],
            type=curr.get("mimeType", "unknown"),
            created_at=curr.get("createdTime", ""),
            original_location="google-drive",
            file_updated_at=curr.get("modifiedTime", ""),
            file_original_url=curr.get("webContentLink", curr.get("webViewLink")),
            file_download_link=curr.get(
                "webContentLink",
                curr.get(
                    "webViewLink",
                ),
            ),
            file_extension=curr.get("fileExtension"),
        )
        if _is_supported(curr, supported_extensions):
            accessible_data: AccessibleData = AccessibleData(
                access_info={
                    "id": curr["id"],
                    "size": curr["size"],
                    "meta": formatted_data.to_dict(),
                },
            )
            processable_data.append(accessible_data)
        else:
            non_processable_data.append(formatted_data)

    return processable_data, non_processable_data


def _is_supported(file, supported_extensions):
    return (
        file.get("fileExtension") is not None
        and file.get("fileExtension") in supported_extensions
        and (
            int(file.get("size")) <= 5 * 1024 * 1024
            if file.get("size") is not None
            else True
        )
    )


def download_file(credentials: Credentials, file_id: str, temp_dir: str):
    service = build("drive", "v3", credentials=credentials)
    request = service.files().get_media(fileId=file_id)

    chunk_size = 5 * 1024 * 1024
    with open(temp_dir, "wb") as f:
        downloader = MediaIoBaseDownload(f, request, chunksize=chunk_size)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    return temp_dir
