from google_auth_oauthlib.flow import Flow
from hooks.get_parameters import get_parameters


def handler(event, context):
    dir = "/oauth/gmail"
    required_params = {"client_secret": "json", "config": "json"}

    params = get_parameters(base_dir=dir, required_params=required_params)
    client_secret = params["client_secret"]
    oauth_config = params["config"]
    scopes = oauth_config["scopes"]
    redirect_uri = oauth_config["redirect_uri"]

    flow = Flow.from_client_config(
        client_config=client_secret, scopes=scopes, redirect_uri=redirect_uri
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    return {"statusCode": 302, "headers": {"Location": authorization_url}}
