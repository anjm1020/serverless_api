from hooks.google.drive_api import get_profile as get_profile_drive
from hooks.google.gmail_api import get_profile as get_profile_gmail


def get_account(credentials, service_type):
    _functions = {
        "gmail": _gmail_get_account,
        "google-drive": _drive_get_account,
    }

    if service_type not in _functions:
        raise ValueError(f"Service type {service_type} is not supported")
    return _functions[service_type](credentials)


def _gmail_get_account(credentials):
    profile = get_profile_gmail(credentials)
    return profile["emailAddress"]


def _drive_get_account(credentials):
    profile = get_profile_drive(credentials)
    return profile["user"]["emailAddress"]
