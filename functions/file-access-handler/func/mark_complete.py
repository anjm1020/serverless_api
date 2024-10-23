from hooks.data_mark import (
    get_redis_client,
    is_process_ended,
    MarkData,
    mark,
    close_connection,
)
from hooks.ssm_api import ParamRequest, get_parameters


def mark_complete(
    user_id: str,
    service: str,
    service_account: str,
    version: str,
    obj_key: str,
    success: bool,
):

    params = get_parameters(
        [
            ParamRequest(
                name="redis_host",
                key="/findy/config/redis_host",
                type="string",
            ),
            ParamRequest(
                name="redis_port",
                key="/findy/config/redis_port",
                type="string",
            ),
        ]
    )

    client = get_redis_client(host=params["redis_host"], port=params["redis_port"])

    mark_data = MarkData.for_marking(
        user_id=user_id,
        service=service,
        service_account=service_account,
        version=version,
        object_id=obj_key,
        success="1" if success else "0",
    )

    mark(client, mark_data)

    res = is_process_ended(client, mark_data)
    if res:
        print(f"Completed mark: , success: {res}")
        close_connection(client)
