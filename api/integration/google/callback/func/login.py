from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from hooks.account_db import (
    create_account,
    get_connection,
    destroy_connection,
    get_account,
    Account,
)


def login(credentials: Credentials):
    connection = get_connection(None)
    account: Account = None
    try:
        service = build("oauth2", "v2", credentials=credentials)
        profile = service.userinfo().get().execute()

        email = profile["email"]
        account = get_account(connection, email)

        if account is None:
            print(f"Create account: {email}")
            account = create_account(connection, "google", email)
    finally:
        destroy_connection(connection)
        return account
