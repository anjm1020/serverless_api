from entity.accessible_data import AccessibleData
from entity.formatted_data import FormattedData
from entity.user_credentials import UserCredentials
from hooks.drive_api import get_file_list as drive_get_data_list
from hooks.drive_api import segmentation as drive_segmentation
from hooks.gmail_api import get_mail_and_attachments_list as gmail_get_data_list
from hooks.gmail_api import segmentation as gmail_segmentation
from hooks.google_api import get_credentials
from hooks.ssm_api import ParamRequest, get_parameters


def get_entire_data(
    user_credentials: UserCredentials,
) -> tuple[list[AccessibleData], list[FormattedData]]:
    service_type = user_credentials.service_type

    _functions = {
        "gmail": lambda creds: _google_get_entire_data(creds, "gmail"),
        "google-drive": lambda creds: _google_get_entire_data(creds, "google-drive"),
    }
    return _functions[service_type](user_credentials)


def _google_get_entire_data(
    user_credentials: UserCredentials, service_type
) -> tuple[list[AccessibleData], list[FormattedData]]:
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="client_secret",
            key=f"/oauth/{service_type}/client_secret",
            type="json",
        )
    ]

    params = get_parameters(required_params=required_params)
    client_secret = params["client_secret"]
    google_credentials = get_credentials(
        user_credentials=user_credentials, client_secret=client_secret
    )

    _get_data_list = {
        "gmail": gmail_get_data_list,
        "google-drive": drive_get_data_list,
    }

    _segmentation = {
        "gmail": gmail_segmentation,
        "google-drive": drive_segmentation,
    }
    entire_file_list = _get_data_list[service_type](credentials=google_credentials)
    processable_data, non_processable_data = _segmentation[service_type](
        entire_file_list
    )

    for pd in processable_data:
        pd.credentials = user_credentials

    return processable_data, non_processable_data
