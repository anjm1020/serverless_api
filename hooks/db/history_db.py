import datetime
import uuid

import boto3
import dns.resolver
import pymysql
import pymysql.cursors
from pymysql.connections import Connection


class History:
    uid: str
    query: str
    user_id: str
    timestamp: str

    def __init__(self, uid, query, user_id, timestamp):
        self.uid = uid
        self.query = query
        self.user_id = user_id
        self.timestamp = timestamp

    def to_item_response(self):
        return self.__dict__


def save_history(connection: Connection, query, user_id):
    tz = datetime.timezone(datetime.timedelta(hours=9))
    current_time = datetime.datetime.now(tz=tz).strftime("%Y-%m-%-d %H:%M:%S")
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            INSERT INTO history(uid, query, user_id, timestamp)
            VALUES(%s, %s, %s, %s)
        """

        cursor.execute(sql, (str(uuid.uuid4()), query, user_id, current_time))
        connection.commit()


def get_list(connection: Connection, user_id):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            SELECT *
            FROM history
            WHERE user_id = %s
        """

        cursor.execute(sql, (user_id))
        result = cursor.fetchall()
        return [History(**r) for r in result]


def delete_by_id(connection: Connection, history_id, user_id):
    with connection.cursor() as cursor:
        sql = """
            DELETE
            FROM history
            WHERE uid = %s and user_id = %s
        """

        cursor.execute(sql, (history_id, user_id))
        connection.commit()


def destroy_connection(connection):
    if connection is not None and connection.open:
        connection.close()
        connection = None


def get_connection(connection):
    param = _get_connection_params()
    if connection is not None and connection.open:
        return connection

    connection = pymysql.connect(
        host=param["host"],
        user=param["user"],
        password=param["password"],
        database=param["database"],
    )
    print(f"connection: {connection}")
    print(f"connection state: {connection.open}")
    return connection


def _get_connection_params():
    _ssm = boto3.client("ssm")

    dir = "/findy/rds/"
    required_params = [
        f"{dir}{n}" for n in ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    ]
    param_resp = _ssm.get_parameters(Names=required_params, WithDecryption=True)

    param_map = {}
    for param in param_resp["Parameters"]:
        param_map[param["Name"]] = param["Value"]

    host = param_map[f"{dir}DB_HOST"]
    user = param_map[f"{dir}DB_USER"]
    password = param_map[f"{dir}DB_PASSWORD"]
    database = param_map[f"{dir}DB_NAME"]

    host_ip = dns.resolver.resolve(host, "A")

    if len(host_ip) == 0:
        raise Exception("Cannot Resolve Hostname : " + host)
    host = str(host_ip[0].address)
    conn_params = {
        "host": host,
        "user": user,
        "password": password,
        "database": database,
    }
    return conn_params
