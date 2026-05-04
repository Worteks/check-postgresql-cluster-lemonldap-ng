import psycopg
import sys


def connect_to_database(server_info: dict, high_privilege=False):
    host = server_info["host"]
    port = server_info["port"]
    database = server_info["database"]

    # Use high privilege account
    if high_privilege is True:
        user = server_info["super_user"]
        password = server_info["super_password"]
    else:
        user = server_info["user"]
        password = server_info["password"]
    try:
        connection = psycopg.connect(host=host, port=port, dbname=database,
                                     user=user, password=password,
                                     autocommit=True)
    except psycopg.OperationalError:
        print(f"[Error] Could not connect to database: host:{host}, port:{port}, database:{database}, user:{user}.")
        sys.exit(2)
    return connection


def disconnect_to_database(connect):
    connect.close()


def verify_server_config(connect):
    listen_addresses = sql_command_error_catching(connect,
                                                 "SHOW listen_addresses")[0]
    if listen_addresses != "*":
        print(f'[Warning] Listen_addresses not set to *, listen_addressess={listen_addresses}.')
    wal_level = sql_command_error_catching(connect,
                                           "SHOW wal_level")[0]
    if wal_level != "logical":
        print(f'[Error] WAL level not set as logical, wal_level={wal_level}.')
        sys.exit(2)
    return listen_addresses, wal_level


def verify_pg_hba(connect, user):
    """
    This view can be helpful to diagnose a previous failure. Note that this
    view reports on the current contents of the file, not on what was last
    loaded by the server.
    - Raises an error connection to database is not possible.
    - Raises a warning if not sufficient privilege to read view.
    """
    sql_cmd = "SELECT * FROM pg_hba_file_rules() WHERE user_name = "+ "'{"+user+"}'"
    results = sql_command_error_catching(connect, sql_cmd)
    if type(results) is str:
        print("[Warning] Insufficient privilege to access pg_hba file rules with user:'{user}'.")
    elif type(results) is psycopg.Cursor:
        messages = []
        for result in results:
            messages.append(f' - Host: {result[6]}, database: {result[4]}, user: {result[5]}.')
        return messages


def sql_command_error_catching(connect, sql_cmd):
    try:
        dbcursor = connect.cursor()
        dbcursor.execute(sql_cmd)
        return dbcursor.fetchall()[0]
    except psycopg.errors.InsufficientPrivilege:
        return "Permission denied, insufficient privilege."


def get_config_number(connect):
    config_number = sql_command_error_catching(connect, "SELECT max(cfgnum) FROM lmConfig")
    return config_number


def get_count_sessions(connect):
    count_sessions = sql_command_error_catching(connect, "SELECT count(*) FROM sessions")
    return count_sessions


# TODO: Add low level replication check
#def check_replication(dbcursor, statement):
#    dbcursor.execute("SELECT *  FROM pg_subscription;")
#    replication = dbcursor.fetchone()
#    if replication is None:
#        cursor.execute(statement)
#    else:
#        print("The replication exists already.")
