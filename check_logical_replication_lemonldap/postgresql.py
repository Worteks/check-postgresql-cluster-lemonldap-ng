import psycopg
import sys
from dotenv import dotenv_values

config_local = dotenv_values(".env")


def connect_to_database(server_info: dict,
                        high_privilege: bool = False) -> psycopg.Connection:
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
        print(f"[Error] Cannot connect: host:{host}, port:{port}, db:{database}, user:{user}")
        sys.exit(2)
    return connection


def disconnect_to_database(connect: psycopg.Connection):
    connect.close()


def get_server_config(connect: psycopg.Connection):
    listen_addresses = sql_command_error_catching(connect,
                                                  "SHOW listen_addresses")
    if listen_addresses != "*":
        print(f'[Warning] Listen_addresses not set to *, listen_addressess={listen_addresses}.')
    wal_level = sql_command_error_catching(connect,
                                           "SHOW wal_level")
    if wal_level != "logical":
        print(f'[Error] WAL level not set as logical, wal_level={wal_level}.')
        sys.exit(2)


def get_high_privilege_sql_cmd(connect: psycopg.Connection, sql_cmd: str):
    """
    Run a SQL command that requires high privilege, superuser.

    This view can be helpful to diagnose a previous failure. Note that this
    view reports on the current contents of the file, not on what was last
    loaded by the server.
    - Raises an error when connection to database is not possible because of
      wrong configuration.
    - Raises a warning if not sufficient privilege to run sql command.
    """
    results = sql_command_error_catching(connect, sql_cmd)
    if results[0] is psycopg.errors.InsufficientPrivilege:
        print(f'[Warning] Insufficient privilege. Command: "{sql_cmd}"')
    else:
        return results



def get_replication_config(connect: psycopg.Connection, user: str):
    """
    Get pg_hba view entries for the replication user.

    This view can be helpful to diagnose a previous failure. Note that this
    view reports on the current contents of the file, not on what was last
    loaded by the server.
    - Raises an error connection to database is not possible.
    - Raises a warning if not sufficient privilege to read view.
    """
    sql_cmd = f"SELECT * FROM pg_hba_file_rules() WHERE user_name = '{{{user}}}'"
    results = get_high_privilege_sql_cmd(connect, sql_cmd)
    if results:
        print("- pg_hba.conf:")
        for result in results:
            print(f' -> host: {result[6]}, db: {result[4][0]}, user: {result[5][0]}')
    sql_cmd = "SELECT subconninfo FROM pg_subscription"
    results = get_high_privilege_sql_cmd(connect, sql_cmd)
    if results:
        print("- subscriptions:")
        # Result string formatting for printing
        results = results.replace("\n", "").split(" ")
        results = " ".join([x for x in results if x])
        print(f" ->  {results}")


def sql_command_error_catching(connect: psycopg.Connection, sql_cmd: str) -> list:
    """
    Run the SQL commands, return a single value (int, str, etc..) if only one
    result else it returns a list with all the values.
    - Returns an error when insufficient privilege.
    """
    try:
        dbcursor = connect.cursor()
        dbcursor.execute(sql_cmd)
        result = dbcursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        else:
            return result
    except psycopg.errors.InsufficientPrivilege:
        return [psycopg.errors.InsufficientPrivilege]


# TODO: Add low level replication check
#def check_replication(dbcursor, statement):
#    dbcursor.execute("SELECT *  FROM pg_subscription;")
#    replication = dbcursor.fetchone()
#    if replication is None:
#        cursor.execute(statement)
#    else:
#        print("The replication exists already.")
