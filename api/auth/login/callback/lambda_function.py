import traceback

from dotenv import load_dotenv
from func.login import LoginRequest, login
from google_auth_oauthlib.flow import Flow

from hooks.auth.login_token import issue
from hooks.aws.ssm_api import ParamRequest, get_parameters
from hooks.db.account_db import Account

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
        service_type = "google-login"
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

        print(f"state={state}")

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

        account: Account = login(LoginRequest(credentials=credentials, job_type=state))
        token = issue(account.uid)
        return {
            "statusCode": 302,
            "headers": {"Location": f"{login_success_url}?token={token}"},
        }
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
