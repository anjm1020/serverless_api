import json

from func.get_entire_data import get_entire_data

from hooks.sqs_api import (
    ack_message,
    get_queue_url_from_arn,
    nack_message,
    send_message,
)
from hooks.ssm_api import ParamRequest, get_parameters
from hooks.with_timeout import TimeoutException, with_timeout


def process(record):
    required_params = [
        ParamRequest(
            name="indexing_queue_url",
            key="/findy/queue/indexing_queue_url",
            type="string",
        ),
        ParamRequest(
            name="download_queue_url",
            key="/findy/queue/download_queue_url",
            type="string",
        ),
    ]

    parmas = get_parameters(required_params=required_params)
    indexing_queue_url = parmas["indexing_queue_url"]
    download_queue_url = parmas["download_queue_url"]

    credentials = record["body"]
    if not isinstance(credentials, dict):
        credentials = json.loads(credentials)

    processable_data, non_processable_data = get_entire_data(record)
    send_message(queue_url=download_queue_url, message_body=processable_data)
    send_message(queue_url=indexing_queue_url, message_body=non_processable_data)


def handler(event, context):
    for record in event["Records"]:
        receipt_handle = record["receiptHandle"]

        try:
            with_timeout(lambda: process(record), timeout=30)
            ack_message(receipt_handle)
            print(f"Message processed successfully: {record['messageId']}")
        except TimeoutException:
            print(f"Timeout occurred while processing message: {record['messageId']}")
            continue
        except Exception as e:
            print(f"Error processing message: {record['messageId']}, Error: {str(e)}")
            nack_message(receipt_handle)
