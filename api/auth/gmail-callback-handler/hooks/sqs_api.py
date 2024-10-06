import json

import boto3


def send_message(queue_url, message_body):
    sqs = boto3.client("sqs")

    if isinstance(message_body, dict):
        message_body = json.dumps(message_body)
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )
