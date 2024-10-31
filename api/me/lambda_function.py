import json

from hooks.db.account_db import Account, get_account_by_uid, get_connection


def handler(event, context):
    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_uid"]

        conn = get_connection(None)
        account: Account = get_account_by_uid(connection=conn, uid=user_id)

        if account is None:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"msg": "user not found"}),
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(account.__dict__),
        }

    except Exception as e:
        print(f"error={e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"msg": "internal server error"}),
        }
