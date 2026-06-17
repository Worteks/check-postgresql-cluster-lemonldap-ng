import psycopg
import sys
from dotenv import dotenv_values

from sqlalchemy import create_engine, select, text
from sqlalchemy import Table, MetaData
from sqlalchemy import func
from sqlalchemy.exc import OperationalError


config_local = dotenv_values(".env")
# TODO: Add superuser for priviledge selects.

# TODO: Make proper debug function
DEBUG = False

# LemonLDAP Database
lemonldap_server = {}
lemonldap_server["main"] = create_engine(config_local["URL_MAIN"], execution_options={"isolation_level": "AUTOCOMMIT", "postgresql_readonly": "True"}, echo=DEBUG)
lemonldap_server["backup"] = create_engine(config_local["URL_BACKUP"], execution_options={"isolation_level": "AUTOCOMMIT", "postgresql_readonly": "True"}, echo=DEBUG)

# Admin Database
admin_server = {}
admin_server["main"] = create_engine(config_local["ADMIN_URL_MAIN"], execution_options={"isolation_level": "AUTOCOMMIT", "postgresql_readonly": "True"}, echo=DEBUG)
admin_server["backup"] = create_engine(config_local["ADMIN_URL_BACKUP"], execution_options={"isolation_level": "AUTOCOMMIT", "postgresql_readonly": "True"}, echo=DEBUG)

metadata_obj = MetaData()
lmconfig = Table("lmconfig", metadata_obj, autoload_with=lemonldap_server["main"])
sessions = Table("sessions", metadata_obj, autoload_with=lemonldap_server["main"])
psessions = Table("psessions", metadata_obj, autoload_with=lemonldap_server["main"])


def get_replication_config(server: str):
    """
    Get pg_hba view entries for the replication user.

    This view can be helpful to diagnose a previous failure. Note that this
    view reports on the current contents of the file, not on what was last
    loaded by the server.
    - Raises an error connection to database is not possible.
    - Raises a warning if not sufficient privilege to read view.
    """
    connection = server_select_high_privilege(server)
    sql_command = text("SELECT * FROM pg_hba_file_rules() WHERE user_name = '{replication}'")
    results = connection.execute(sql_command).fetchall()
    if results:
        print("[Info] - pg_hba.conf:")
        for result in results:
            print(f'[Info] -> host: {result[6]}, db: {result[4][0]}, user: {result[5][0]}')
    sql_command = text("SELECT subconninfo FROM pg_subscription")
    results = connection.execute(sql_command).fetchall()[0][0]
    if results:
        print(f"[Info] - Subscriptions {server}:")
        # Result string formatting for printing
        results = results.replace("\n", "").split(" ")
        results = " ".join([x for x in results if x])
        print(f"[Info]  ->  {results}")


def get_server_config(server: str):
    connection = server_select_high_privilege(server)

    sql_command = text("SHOW listen_addresses")
    listen_addresses = connection.execute(sql_command).fetchall()[0][0]
    if listen_addresses != "*":
        print(f'[Warning] Listen_addresses not set to *, listen_addressess={listen_addresses}.')

    sql_command = text("SHOW wal_level")
    wal_level = connection.execute(sql_command).fetchall()[0][0]
    if wal_level != "logical":
        print(f'[Error] WAL level not set as logical, wal_level={wal_level}.')
        sys.exit(2)


def server_select_high_privilege(server: str):
    try:
        return admin_server[server].connect()
    except OperationalError:
        print(f"[Error] Could not connect to server: {server}.")
        sys.exit(2)
    except Exception as err:
        print(f"[Error] Unexpected error: {err}.")
        sys.exit(2)


def select_table(table):
    if table == "lmconfig":
        return lmconfig
    elif table == "sessions":
        return sessions
    elif table == "psessions":
        return psessions
    print(f"[Error] Table: {table} is not a LemonLDAP database table.")
    sys.exit(2)


# TODO: Add low level replication check
#def check_replication(dbcursor, statement):
#    dbcursor.execute("SELECT *  FROM pg_subscription;")
#    replication = dbcursor.fetchone()
#    if replication is None:
#        cursor.execute(statement)
#    else:
#        print("The replication exists already.")

def server_select(server: str):
    try:
        return lemonldap_server[server].connect()
    except OperationalError:
        print(f"[Error] Could not connect to server: {server}.")
        sys.exit(2)
    except Exception as err:
        print(f"[Error] Unexpected error: {err}.")
        sys.exit(1)


def get_config_number(server: str):
    server_connection = server_select(server)
    stmt = select(func.max(lmconfig.c.cfgnum))
    config_number = server_connection.execute(stmt)
    return config_number.first()[0]


def get_count_sessions(server: str):
    server_connection = server_select(server)
    stmt = select(func.count(sessions.c.id))
    total_sessions = server_connection.execute(stmt)
    return total_sessions.first()[0]


def get_count_psessions(server: str):
    server_connection = server_select(server)
    stmt = select(func.count(psessions.c.id))
    total_psessions = server_connection.execute(stmt)
    return total_psessions.first()[0]
