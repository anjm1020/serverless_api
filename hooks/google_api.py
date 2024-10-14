from google.oauth2.credentials import Credentials

from entity.user_credentials import UserCredentials


def get_credentials(
    user_credentials: UserCredentials, client_secret: dict
) -> Credentials:
    client_secret = client_secret["web"]

    client_id = client_secret["client_id"]
    _client_secret = client_secret["client_secret"]

    token = user_credentials.access_token
    refresh_token = user_credentials.refresh_token
    scopes = user_credentials.scopes

    info = {
        "token": token,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": _client_secret,
        "scopes": scopes,
    }
    return Credentials.from_authorized_user_info(info)
