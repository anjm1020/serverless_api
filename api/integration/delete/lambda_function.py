import json

from hooks.db.credential_db import delete_by_id, get_connection


def handler(event, conetext):

    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_uid"]
        cred_id = event["pathParameters"]["id"]

        conn = get_connection(None)
        delete_by_id(connection=conn, cred_id=cred_id, user_id=user_id)

        return {"statusCode": 204}
    except Exception as e:
        print(f"error={e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"msg": "internal server error"}),
        }
