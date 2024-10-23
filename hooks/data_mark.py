import redis


class MarkData:
    def __init__(
        self, user_id, service, service_account, version, object_id=None, success=None
    ):
        self._user_id = user_id
        self._service = service
        self._service_account = service_account
        self._version = version
        self._object_id = object_id
        self._success = success

    @property
    def user_id(self):
        return self._user_id

    @property
    def service(self):
        return self._service

    @property
    def service_account(self):
        return self._service_account

    @property
    def version(self):
        return self._version

    @property
    def object_id(self):
        return self._object_id

    @property
    def success(self):
        return self._success

    @classmethod
    def for_meta(cls, user_id, service, service_account, version):
        return cls(user_id, service, service_account, version, None, None)

    @classmethod
    def for_marking(
        cls, user_id, service, service_account, version, object_id, success
    ):
        return cls(user_id, service, service_account, version, object_id, success)


def get_redis_client(host, port=6379):
    return redis.Redis(host=host, port=port, ssl=True)


def set_list_size(client: redis.Redis, mark_data: MarkData, size):
    client.set(
        name=get_list_key(
            user_id=mark_data.user_id,
            service=mark_data.service,
            service_account=mark_data.service_account,
            version=mark_data.version,
        ),
        value=size,
        ex=60 * 60 * 1,
    )


def mark(client: redis.Redis, mark_data: MarkData):
    client.set(
        name=get_object_mark_key(
            user_id=mark_data.user_id,
            service=mark_data.service,
            service_account=mark_data.service_account,
            version=mark_data.version,
            object_id=mark_data.object_id,
        ),
        value="1" if mark_data.success else "0",
        ex=60 * 60 * 1,
    )


def is_process_ended(client: redis.Redis, mark_data: MarkData):
    print("$$ start is_process_ended")
    list_key = get_list_key(
        user_id=mark_data.user_id,
        service=mark_data.service,
        service_account=mark_data.service_account,
        version=mark_data.version,
    )
    list_size = client.get(list_key)
    if list_size is None:
        print(f"No list size found: {list_key}")
        raise Exception("No list size found")
    list_size = int(list_size)

    object_mark_key_pattern = get_object_mark_key(
        user_id=mark_data.user_id,
        service=mark_data.service,
        service_account=mark_data.service_account,
        version=mark_data.version,
        object_id="*",
    )

    cursor = 0
    object_mark_keys = []
    while True:
        cursor, keys = client.scan(
            cursor=cursor, match=object_mark_key_pattern, count=100
        )
        print(f"$ keys: {keys}")
        object_mark_keys.extend(keys)
        if cursor == "0" or cursor == 0:
            break

    print(f"$$ object_mark_keys: {len(object_mark_keys)}")
    print(f"$$ list_size: {list_size}")
    if len(object_mark_keys) != list_size:
        return False

    success_count = sum(1 for key in object_mark_keys if client.get(key) == b"1")
    success_percentage = (success_count / list_size) * 100 if list_size > 0 else 0

    return success_percentage


def get_object_mark_key(user_id, service, service_account, version, object_id):
    return f"object:{user_id}:{service}:{service_account}:{version}:{object_id}"


def get_list_key(user_id, service, service_account, version):
    return f"list:{user_id}:{service}:{service_account}:{version}"


def close_connection(client: redis.Redis):
    client.quit()


if __name__ == "__main__":
    client = get_redis_client(host="localhost", port=6379)
    mark_data = MarkData.for_meta(
        user_id="test",
        service="google-drive",
        service_account="anjm1020@gmail.com",
        version="1.0.0",
    )
    set_list_size(client, mark_data, 10)
    print(is_process_ended(client, mark_data))

    for _ in range(10):
        mark_data = MarkData.for_marking(
            user_id="test",
            service="google-drive",
            service_account="anjm1020@gmail.com",
            version="1.0.0",
            object_id=f"{_}",
            success=True,
        )
        mark(client, mark_data)

    print(is_process_ended(client, mark_data))
