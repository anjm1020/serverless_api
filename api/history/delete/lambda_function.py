import json

from hooks.db.history_db import delete_by_id, get_connection


def handler(event, conetext):

    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_uid"]
        history_id = event["pathParameters"]["id"]

        conn = get_connection(None)
        delete_by_id(connection=conn, history_id=history_id, user_id=user_id)

        return {"statusCode": 204}
    except Exception as e:
        print(f"error={e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"msg": "internal server error"}),
        }
