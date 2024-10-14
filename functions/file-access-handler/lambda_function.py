import json
import traceback

from entity.formatted_data import FormattedData
from entity.index_data import IndexData
from func.access_data import access_data
from func.invoke_embedding import invoke_embedding
from func.save_index import save_index
from func.mark_complete import mark_complete

from entity.accessible_data import AccessibleData
from hooks.sqs_api import (
    ack_message,
    get_queue_url_from_arn,
    nack_message,
    send_message,
)
from hooks.with_timeout import TimeoutException, with_timeout


def process(record):
    raw_data = record["body"]
    if not isinstance(raw_data, dict):
        raw_data = json.loads(raw_data)

    data: AccessibleData = AccessibleData.from_dict(data=raw_data)
    accessed_data: FormattedData = access_data(data)
    print("Completed access data")
    embeded_data: IndexData = invoke_embedding(accessed_data)
    print("Completed invoke embedding")
    save_index(embeded_data)
    print("Completed save index")
    mark_complete(user_id=data.credentials.user_id, obj_key="test-object-key")

    print(f"Success: process data: {record['messageId']}")
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
