import json

import boto3

sqs = boto3.client("sqs")


def get_queue_url_from_arn(queue_arn):
    region = queue_arn.split(":")[3]
    account_id = queue_arn.split(":")[4]
    queue_name = queue_arn.split(":")[5].split("/")[-1]

    return f"https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}"


def send_message(queue_url, message_body):
    global sqs

    if isinstance(message_body, dict):
        message_body = json.dumps(message_body)
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )


def ack_message(queue_url, receipt_handle):
    global sqs
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
    )


def nack_message(queue_url, receipt_handle, visibility_timeout=0):
    global sqs
    try:
        sqs.change_message_visibility(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=visibility_timeout,
        )
        print(
            f"Message returned to the queue for reprocessing, receipt handle: {receipt_handle}"
        )
    except Exception as e:
        print(f"Failed to nack message: {e}")
