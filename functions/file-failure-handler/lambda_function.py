import json
import traceback
import uuid
from entity.accessible_data import AccessibleData
from func.mark_complete import mark_complete
from hooks.sqs_api import (
    ack_message,
    get_queue_url_from_arn,
    nack_message,
)
from hooks.with_timeout import TimeoutException, with_timeout


def process(record):
    raw_data = record["body"]
    if not isinstance(raw_data, dict):
        raw_data = json.loads(raw_data)

    data: AccessibleData = AccessibleData.from_dict(data=raw_data)

    object_key = str(uuid.uuid4())
    mark_complete(
        user_id=data.credentials.user_id,
        service=data.credentials.service_type,
        service_account=data.credentials.service_account,
        version=data.version,
        obj_key=object_key,
        success=False,
    )
    return


def handler(event, context):
    print(f"Event: {event}")
    for record in event["Records"]:
        receipt_handle = record["receiptHandle"]
        source_queue_url = get_queue_url_from_arn(record["eventSourceARN"])

        try:
            with_timeout(lambda: process(record), timeout=60)
            ack_message(queue_url=source_queue_url, receipt_handle=receipt_handle)
            print(f"Message processed successfully: {record['messageId']}")
        except TimeoutException:
            print(f"Timeout occurred while processing message: {record['messageId']}")
            continue
        except Exception as e:
            print(f"Error processing message: {record['messageId']}, Error: {str(e)}")
            traceback.print_exc()
            nack_message(queue_url=source_queue_url, receipt_handle=receipt_handle)
