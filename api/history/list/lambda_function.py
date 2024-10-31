import json

from func.split_history import split_by_date

from hooks.db.history_db import History, get_connection, get_list


def handler(event, conetext):

    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_uid"]

        conn = get_connection(None)
        history_list: list[History] = get_list(connection=conn, user_id=user_id)

        result = split_by_date(history_list)

        body = json.dumps(
            {
                "items": [
                    {
                        "label": h["label"],
                        "data": [e.to_item_response() for e in h["data"]],
                    }
                    for h in result
                ]
            }
        )

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
