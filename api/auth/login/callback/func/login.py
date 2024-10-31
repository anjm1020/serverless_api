from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from hooks.db.account_db import (
    Account,
    create_account,
    destroy_connection,
    get_account,
    get_connection,
)


class LoginRequest:
    credentials: Credentials
    job_type: str

    def __init__(self, credentials, job_type):
        self.credentials = credentials
        self.job_type = job_type


def login(loginRequest: LoginRequest):

    credentials = loginRequest.credentials
    job_type = loginRequest.job_type

    print(f"cred={credentials}, job_type={job_type}")

    connection = get_connection(None)
    account: Account = None
    try:
        service = build("oauth2", "v2", credentials=credentials)
        profile = service.userinfo().get().execute()

        email = profile["email"]
        account = get_account(connection, email)

        if account is None:
            print(f"Create account: {email}")
            account = create_account(connection, "google", email, job_type)
    finally:
        destroy_connection(connection)
        return account
