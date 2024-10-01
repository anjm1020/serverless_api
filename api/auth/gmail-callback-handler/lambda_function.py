import traceback

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from hooks.get_parameters import get_parameters

load_dotenv(override=True)


def handler(event, context):

    print(f"Event: {event}")
    print(f"Context: {context}")

    dir = "/oauth/gmail"
    required_params = {
        "client_secret": "json",
        "config": "json",
        "login_success_url": "string",
    }

    params = get_parameters(base_dir=dir, required_params=required_params)
    client_secret = params["client_secret"]
    oauth_config = params["config"]
    scopes = oauth_config["scopes"]
    redirect_uri = oauth_config["redirect_uri"]
    login_success_url = params["login_success_url"]

    code = event["queryStringParameters"]["code"]
    state = event["queryStringParameters"]["state"]

    if not code:
        return {"statusCode": 400, "body": "Missing code parameter"}

    flow = Flow.from_client_config(
        client_config=client_secret,
        scopes=scopes,
        redirect_uri=redirect_uri,
        state=state,
    )

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        ## TODO : save credentials on db
        ## TODO : put message on sqs
        return {"statusCode": 302, "headers": {"Location": login_success_url}}
    except Exception as e:
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {"statusCode": 500, "body": "Internal Server Error"}