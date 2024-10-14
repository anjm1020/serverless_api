import json
import traceback

from func.get_entire_data import get_entire_data

from entity.accessible_data import AccessibleData
from entity.formatted_data import FormattedData
from entity.user_credentials import UserCredentials
from hooks.sqs_api import (
    ack_message,
    get_queue_url_from_arn,
    nack_message,
    send_accessible_data_message,
    send_formatted_data_message,
)
from hooks.ssm_api import ParamRequest, get_parameters
from hooks.with_timeout import TimeoutException, with_timeout


def process(record):
    required_params = [
        ParamRequest(
            name="indexing_queue_url",
            key="/findy/config/indexing_queue_url",
            type="string",
        ),
        ParamRequest(
            name="accessible_queue_url",
            key="/findy/config/accessible_queue_url",
            type="string",
        ),
    ]

    parmas = get_parameters(required_params=required_params)
    indexing_queue_url = parmas["indexing_queue_url"]
    accessible_queue_url = parmas["accessible_queue_url"]

    credentials = record["body"]
    if not isinstance(credentials, dict):
        credentials = json.loads(credentials)
    user_credentials = UserCredentials.from_dict(credentials)

    processable_data: list[AccessibleData]
    non_processable_data: list[FormattedData]

    processable_data, non_processable_data = get_entire_data(
        user_credentials=user_credentials
    )

    print(f"processable_data: {len(processable_data)}")
    print(f"non_processable_data: {len(non_processable_data)}")
    for data in processable_data:
        send_accessible_data_message(
            queue_url=accessible_queue_url,
            message_body=data,
        )
    for data in non_processable_data:
        send_formatted_data_message(
            queue_url=indexing_queue_url,
            message_body=data,
        )


def handler(event, context):
    print(f"Event: {event}")
    for record in event["Records"]:
        receipt_handle = record["receiptHandle"]
        source_queue_url = get_queue_url_from_arn(record["eventSourceARN"])

        try:
            with_timeout(lambda: process(record), timeout=30)
            ack_message(queue_url=source_queue_url, receipt_handle=receipt_handle)
            print(f"Message processed successfully: {record['messageId']}")
        except TimeoutException:
            print(f"Timeout occurred while processing message: {record['messageId']}")
            continue
        except Exception as e:
            print(f"Error processing message: {record['messageId']}, Error: {str(e)}")
            traceback.print_exc()
            nack_message(queue_url=source_queue_url, receipt_handle=receipt_handle)
