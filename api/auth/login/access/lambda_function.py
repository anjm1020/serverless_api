from google_auth_oauthlib.flow import Flow

from hooks.aws.ssm_api import ParamRequest, get_parameters


def handler(event, context):
    service_type = "google-login"
    selected_job_type = event["queryStringParameters"]["job_type"]

    required_params: list[ParamRequest] = [
        ParamRequest(
            name="client_secret",
            key=f"/oauth/{service_type}/client_secret",
            type="json",
        ),
        ParamRequest(name="config", key=f"/oauth/{service_type}/config", type="json"),
    ]

    params = get_parameters(required_params=required_params)
    client_secret = params["client_secret"]
    oauth_config = params["config"]

    scopes = oauth_config["scopes"]
    redirect_uri = oauth_config["redirect_uri"]

    flow = Flow.from_client_config(
        client_config=client_secret,
        scopes=scopes,
        redirect_uri=redirect_uri,
        state=selected_job_type,
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )

    return {"statusCode": 302, "headers": {"Location": authorization_url}}
