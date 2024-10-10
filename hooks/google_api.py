from google.oauth2.credentials import _GOOGLE_OAUTH2_TOKEN_ENDPOINT, Credentials


def get_credentials(credentials: dict, client_secret: dict) -> Credentials:
    client_secret = client_secret["web"]

    client_id = client_secret["client_id"]
    _client_secret = client_secret["client_secret"]

    token = credentials["token_data"]["access_token"]
    refresh_token = credentials["token_data"]["refresh_token"]
    scopes = credentials["scopes"]

    info = {
        "token": token,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": _client_secret,
        "scopes": scopes,
        "token_uri": _GOOGLE_OAUTH2_TOKEN_ENDPOINT,
    }
    return Credentials.from_authorized_user_info(info)
