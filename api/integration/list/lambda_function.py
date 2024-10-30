import json

from entity.user_credentials import UserCredentials
from hooks.db.credential_db import get_connection, get_list_by_user_id


def handler(event, conetext):

    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_uid"]

        conn = get_connection(None)
        credential_list: list[UserCredentials] = get_list_by_user_id(
            connection=conn, user_id=user_id
        )

        body = json.dumps({"items": [c.to_item_response() for c in credential_list]})

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": body,
        }
    except Exception as e:
        print(f"error={e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"msg": "internal server error"}),
        }
