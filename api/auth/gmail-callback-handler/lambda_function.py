import traceback

import hooks.db_api as DB
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from hooks.get_parameters import get_parameters
from hooks.gmail_api import get_profile

load_dotenv(override=True)


class TokenAlreadyExists(Exception):
    pass


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
    login_success_url = params["login_success_url"]

    scopes = oauth_config["scopes"]
    redirect_uri = oauth_config["redirect_uri"]

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
        print("Start Fetching token")
        flow.fetch_token(code=code)

        credentials = flow.credentials

        print("Start get profile")
        profile = get_profile(credentials)
        user_id = state

        conn = None
        conn = DB.get_connection(connection=conn)

        if DB.exists_token(
            connection=conn,
            user_id=user_id,
            account=profile["emailAddress"],
            service_type="gmail",
        ):
            print("Token already exists")
            DB.destroy_connection(connection=conn)
            raise TokenAlreadyExists("Token already exists")

        print("Storing token")
        DB.store_new_token(
            connection=conn,
            user_id=user_id,
            account=profile["emailAddress"],
            service_type="gmail",
            token_data={
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
            },
        )
        print("Token stored successfully")
        DB.destroy_connection(connection=conn)
        print("Connection successfully destroyed")

        return {"statusCode": 302, "headers": {"Location": login_success_url}}
    except Exception as e:
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        error_msg = "internal_server_error"
        if isinstance(e, TokenAlreadyExists):
            error_msg = "token_already_exists"
        return {
            "statusCode": 302,
            "headers": {"Location": f"{login_success_url}?error={error_msg}"},
        }
