import json

import boto3

sqs = boto3.client("sqs")


def send_message(queue_url, message_body):
    global sqs

    if isinstance(message_body, dict):
        message_body = json.dumps(message_body)
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )
