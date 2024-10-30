import boto3
import dns.resolver
import pymysql
import pymysql.cursors

from entity.user_credentials import UserCredentials


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


def exists_token(connection, user_id, account, service_type):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            SELECT COUNT(*) AS token_exists
            FROM credentials 
            WHERE user_id = %s AND service_account = %s AND service_type = %s
        """
        cursor.execute(sql, (user_id, account, service_type))
        result = cursor.fetchone()
        print(result)
        return result["token_exists"] > 0


def store_new_token(connection, user_id, account, service_type, token_data, scopes):
    with connection.cursor() as cursor:
        sql = """
            INSERT INTO credentials (user_id, service_account, service_type, access_token, refresh_token, scopes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                user_id,
                account,
                service_type,
                token_data["access_token"],
                token_data["refresh_token"],
                scopes,
            ),
        )
        connection.commit()


def get_list_by_user_id(connection, user_id):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            SELECT * FROM credentials 
            WHERE user_id = %s
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [UserCredentials(**a) for a in result]
