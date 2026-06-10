import lemonldap as llng
from pathlib import Path
import json
import postgresql as psql
import sys
from psycopg import Connection as pconnect


def read_configuration(configuration_path: Path) -> dict:
    """
    Read configuration from a file into a dictionary.

    Parameters:
    configuration_path (Path): Configuration file path.

    Returns:
    dict: Dictionary with the configuration options.

    Raises:
    FileNotFoundError:
    json.decoder.JSONDecodeError:
    """
    try:
        return json.load(open(configuration_path))
    except FileNotFoundError:
        print(f"[Error] File not found: {configuration_path}.")
        sys.exit(2)
    except json.decoder.JSONDecodeError:
        print(f"[Error] Badly configured json file: {configuration_path}.")
        sys.exit(2)


def define_configuration(configuration_file: Path) -> dict:
    """
    Read  and compare local and global configuration files. Afterwards,
    overwrite global with existing local values.

    Parameters:
    configuration_file (pathlib.Path): Configuration file path.

    Returns:
    dict: Dictionary with full configuration options.
    """
    configuration_global = read_configuration(Path("./configuration.json"))
    configuration_local = read_configuration(configuration_file)
    for key in configuration_local.keys():
        for second_key in configuration_local[key].keys():
            configuration_global[key][second_key] = configuration_local[key][second_key]
    return configuration_global


def check_connection(server_info: dict):
    """
    Connects into database. Reads tables: lmConfig, sessions and psessions.
    Finally disconnects from the database to confirm that everything
    is ok.

    Parameters:
    server_info (dict): Dictionary with server configuration.
    """
    connect = psql.connect_to_database(server_info)
    llng.check_read_tables(connect)
    psql.disconnect_to_database(connect)


def check_config(server_info: dict):
    # TODO: Add a Select to a table to make sure of permissions for tables.
    """
    Check configuration for listen_addresses, wal_level and pg_hba file.

    Parameters:
    server_info (dict): Dictionary with server configuration.
    """
    if "super_user" in server_info and server_info["super_user"] != 'None':
        connect = psql.connect_to_database(server_info, high_privilege=True)
        psql.get_replication_config(connect, server_info["user"])
        psql.disconnect_to_database(connect)
    else:
        print('[Warning] Super user not configured, pg_hba.file not read.')
    connect = psql.connect_to_database(server_info)
    psql.get_server_config(connect)
    psql.disconnect_to_database(connect)


def check_sync(server_info_main: dict, server_info_backup: dict,
               interval: int = 3):
    """
    Check configuration for listen_addresses, wal_level and pg_hba file.

    Parameters:
    server_info_main (dict): Dictionary with configuration for main server.
    server_info_backup (dict): Dictionary with configuration for backup server.
    sensibility (int): Intervale to consider sessions synchronised.
    """
    connect_main = psql.connect_to_database(server_info_main)
    connect_backup = psql.connect_to_database(server_info_backup)

    for _ in range(2):
        value = check_config_number(connect_main, connect_backup)
        if value:
            break
    else:
        print("[Error] Configurations are not synchronised")
        sys.exit(2)

    for _ in range(3):
        value = check_sessions(connect_main, connect_backup, interval)
        if value:
            break
    else:
        print("[Error] Sessions are not synchronised")
        sys.exit(2)

    psql.disconnect_to_database(connect_main)
    psql.disconnect_to_database(connect_backup)


def check_config_number(connect_main: pconnect, connect_backup: pconnect) -> bool:
    """
    Check the configuration number of both databases, then compare them to
    verify synchronisation.

    Parameters:
    connect_main (pconnect): PostgreSQL connection to main server.
    connect_backup (pconnect): PostgreSQL connection to backup server.

    Returns:
    bool: Boolean depending on synchronisation.
    """
    config_main = llng.get_config_number(connect_main)
    config_backup = llng.get_config_number(connect_backup)
    if config_main == config_backup:
        print("Configuration is synchronised.")
        return True
    return False


def check_sessions(connect_main: pconnect, connect_backup: pconnect,
                   interval: int) -> bool:
    """
    Check number of sessions of both databases, then compare them to
    verify synchronisation.

    Parameters:
    connect_main (pconnect): PostgreSQL connection to main server.
    connect_backup (pconnect): PostgreSQL connection to backup server.
    interval: Integer to define tolerance interval.

    Returns:
    bool: Boolean depending on synchronisation.
    """
    session_main = llng.get_count_sessions(connect_main)
    session_backup = llng.get_count_sessions(connect_backup)
    min_value = session_backup - interval
    if min_value <= int(session_main) <= int(session_backup):
        print("Sessions are synchronised.")
        return True
    return False
