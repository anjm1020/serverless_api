import boto3

from entity.accessible_data import AccessibleData
from entity.formatted_data import FormattedData
from entity.user_credentials import UserCredentials
from hooks.google_api import get_credentials
from hooks.ssm_api import ParamRequest, get_parameters
from hooks.gmail_api import get_mail_content
from hooks.drive_api import download_file
from func.parse_file import extract_text_from_file, split_text


def access_data(data: AccessibleData):
    _functions = {
        "gmail": _gmail_access_data,
        "google-drive": _drive_access_data,
    }

    return _functions[data.credentials.service_type](data)


def _gmail_access_data(accessible_data: AccessibleData):
    google_credentials = _get_google_credentials(accessible_data.credentials, "gmail")
    data: FormattedData = get_mail_content(
        google_credentials, accessible_data.access_info["id"]
    )
    data.content = split_text(data.content)
    return data


def _drive_access_data(accessible_data: AccessibleData):
    google_credentials = _get_google_credentials(
        accessible_data.credentials, "google-drive"
    )
    file_id = accessible_data.access_info["id"]
    file_meta = accessible_data.access_info["meta"]

    file_name = file_meta["title"]
    tmp_dir = f"/tmp/{file_name}"
    file_dir = download_file(google_credentials, file_id, tmp_dir)

    texts = extract_text_from_file(file_dir)
    updated_data = {**file_meta, "content": texts}

    return FormattedData.from_dict(updated_data)


def _get_google_credentials(credentials: UserCredentials, service_type: str):
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="client_secret",
            key=f"/oauth/{service_type}/client_secret",
            type="json",
        )
    ]

    params = get_parameters(required_params=required_params)
    client_secret = params["client_secret"]
    return get_credentials(user_credentials=credentials, client_secret=client_secret)
