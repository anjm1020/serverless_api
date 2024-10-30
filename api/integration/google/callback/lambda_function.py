import traceback

from dotenv import load_dotenv
from func.get_account import get_account
from func.login import login
from google_auth_oauthlib.flow import Flow

import hooks.db.credential_db as DB
from entity.user_credentials import UserCredentials
from hooks.aws.sqs_api import send_message, send_user_credentials_message
from hooks.aws.ssm_api import ParamRequest, get_parameters

load_dotenv(override=True)


class CustomException(Exception):
    @classmethod
    def message(cls):
        return "internal_server_error"


class CodeMissingException(CustomException):
    @classmethod
    def message(cls):
        return "Code missing in query parameters"


class TokenConflictException(CustomException):
    @classmethod
    def message(cls):
        return "Token already exists"


def handler(event, context):
    try:
        service_type = event["queryStringParameters"]["service_type"]
        print(f"Event: {event}")
        print(f"Context: {context}")
        required_params: list[ParamRequest] = [
            ParamRequest(
                name="client_secret",
                key=f"/oauth/{service_type}/client_secret",
                type="json",
            ),
            ParamRequest(
                name="config", key=f"/oauth/{service_type}/config", type="json"
            ),
            ParamRequest(
                name="login_success_url",
                key="/oauth/common/login_success_url",
                type="string",
            ),
            ParamRequest(
                name="queue_url",
                key="/oauth/common/credential_queue_url",
                type="string",
            ),
        ]

        params = get_parameters(required_params=required_params)
        client_secret = params["client_secret"]
        oauth_config = params["config"]
        login_success_url = params["login_success_url"]

        scopes = oauth_config["scopes"]
        redirect_uri = oauth_config["redirect_uri"]

        code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]

        if not code:
            raise CodeMissingException()

        flow = Flow.from_client_config(
            client_config=client_secret,
            scopes=scopes,
            redirect_uri=redirect_uri,
            state=state,
        )

        print("Start Fetching token")
        flow.fetch_token(code=code)
        credentials = flow.credentials

        if service_type == "google-login":
            print(login(credentials))
            return {"statusCode": 302, "headers": {"Location": login_success_url}}

        print("Start get account mail")
        user_id = state
        account = get_account(credentials, service_type)

        conn = None
        conn = DB.get_connection(connection=conn)

        if DB.exists_token(
            connection=conn,
            user_id=user_id,
            account=account,
            service_type=service_type,
        ):
            print("Token already exists")
            DB.destroy_connection(connection=conn)
            raise TokenConflictException()

        scopes = " ".join(scopes)

        print("Storing token")
        DB.store_new_token(
            connection=conn,
            user_id=user_id,
            account=account,
            service_type=service_type,
            token_data={
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
            },
            scopes=scopes,
        )
        print("Token stored successfully")

        print("Sending message to SQS")
        user_credentials: UserCredentials = UserCredentials(
            user_id=user_id,
            service_type=service_type,
            service_account=account,
            scopes=scopes,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
        )
        send_user_credentials_message(
            queue_url=params["queue_url"], message_body=user_credentials
        )

        print("Message sent successfully")

        DB.destroy_connection(connection=conn)
        print("Connection successfully destroyed")

        return {"statusCode": 302, "headers": {"Location": login_success_url}}
    except Exception as e:
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")

        error_msg = "internal_server_error"
        if isinstance(e, CustomException):
            error_msg = e.message()

        return {
            "statusCode": 302,
            "headers": {"Location": f"{login_success_url}?error={error_msg}"},
        }
