import datetime
import uuid

import boto3
import dns.resolver
import pymysql


class Account:
    uid: str
    register_type: str
    email: str
    version: str
    can_refresh: bool
    job_type: str
    register_at: str
    last_login_at: str

    def __init__(
        self,
        uid,
        register_type,
        email,
        version,
        can_refresh,
        job_type,
        register_at,
        last_login_at,
    ):
        self.uid = uid
        self.register_type = register_type
        self.email = email
        self.version = version
        self.can_refresh = can_refresh
        self.job_type = job_type
        self.register_at = register_at
        self.last_login_at = last_login_at

    def __repr__(self):
        return f"Account(uid={self.uid}, register_type={self.register_type}, email={self.email}, version={self.version}, can_refresh={self.can_refresh})"


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


def get_account_by_uid(connection, uid):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            SELECT * FROM accounts 
            WHERE uid = %s AND register_type = 'google'
        """
        cursor.execute(sql, (uid,))
        result = cursor.fetchone()
        if result is None:
            return None
        return Account(**result)


def get_account(connection, email):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            SELECT * FROM accounts 
            WHERE email = %s AND register_type = 'google'
        """
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        if result is None:
            return None
        return Account(**result)


def exists_account(connection, email):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
            SELECT COUNT(*) AS account_exists
            FROM accounts 
            WHERE email = %s AND register_type = 'google'
        """
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        return result["account_exists"] > 0


def create_account(connection, register_type, email, job_type, can_refresh=False):
    try:
        print("invoked create_account")
        uid = str(uuid.uuid4())
        version = str(uuid.uuid4())

        tz = datetime.timezone(datetime.timedelta(hours=9))
        current_time = datetime.datetime.now(tz=tz).strftime("%Y-%m-%-d %H:%M:%S")

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO accounts (uid, register_type, email, version, job_type, can_refresh, register_at, last_login_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    uid,
                    register_type,
                    email,
                    version,
                    job_type,
                    can_refresh,
                    current_time,
                    current_time,
                ),
            )
            connection.commit()
            created_account = get_account(connection, email)
            print(f"created_account: {created_account}")
            return created_account
    except Exception as e:
        print(f"Error: {e}")
        raise e
