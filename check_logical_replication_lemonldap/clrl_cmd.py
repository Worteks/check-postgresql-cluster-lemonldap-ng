from pathlib import Path
import json
import psql_cmd
import sys


def read_configuration(configuration_file: str) -> dict:
    """
    Read configuration from a file into a dictionary.

    Parameters:
    configuration_file (str): Configuration file path.

    Returns:
    dict: Dictionary with the configuration options.

    Raises:
    FileNotFoundError:
    json.decoder.JSONDecodeError:
    """
    configuration_path = Path(configuration_file)
    try:
        return json.load(open(configuration_path))
    except FileNotFoundError:
        print(f"[Error] File not found: {configuration_file}.")
        sys.exit(2)
    except json.decoder.JSONDecodeError:
        print(f"[Error] Badly configured json file: {configuration_file}.")
        sys.exit(2)


def define_configuration(configuration_file: str):
    """
    Read local and global configuration files. Then overwrite global with local
    values if they exist.
    - Inexistant or invalid global configuration file will raise an error and exit.
    - Inexistant or invalid local configuration file will raise a warning and
      continue.
    """
    configuration = read_configuration("./configuration.json")
    if configuration == 2:
        print("[Error] Global configuration error.")
        sys.exit(2)
    configuration_locale = read_configuration(configuration_file)
    if configuration_locale == 2:
        print("[Warning] Local configuration error.")
    elif type(configuration_locale) is dict:
        for key in configuration_locale.keys():
            for second_key in configuration_locale[key].keys():
                configuration[key][second_key] = configuration_locale[key][second_key]
    return configuration


def check_connection(server_info):
    """
    Connect and disconnects to server with normal account.
    - Raises an error and exits if can not connect to database.
    """
    connect = psql_cmd.connect_to_database(server_info)
    psql_cmd.disconnect_to_database(connect)


def check_config(server_info):
    message = []
    if "super_user" in server_info and server_info["super_user"] != 'None':
        connect = psql_cmd.connect_to_database(server_info, high_privilege=True)
        message = psql_cmd.verify_pg_hba(connect, server_info["user"])
        psql_cmd.disconnect_to_database(connect)
    else:
        print('[Warning] Super user not configured, pg_hba.file not read.')
    connect = psql_cmd.connect_to_database(server_info)
    psql_cmd.verify_server_config(connect)
    psql_cmd.disconnect_to_database(connect)
    return message


def check_sync(server_info_main, server_info_backup, sensibility=3):
    number_try = 0
    connect_main = psql_cmd.connect_to_database(server_info_main)
    connect_backup = psql_cmd.connect_to_database(server_info_backup)

    check_config_number(connect_main, connect_backup, number_try, sensibility)
    check_sessions(connect_main, connect_backup, number_try)

    psql_cmd.disconnect_to_database(connect_main)
    psql_cmd.disconnect_to_database(connect_backup)


def check_config_number(connect_main, connect_backup, number_try, sensibility=3):
    number_try += 1
    config_main = psql_cmd.get_config_number(connect_main)
    config_backup = psql_cmd.get_config_number(connect_backup)
    if config_main == config_backup:
        print("Configuration is synchronised.")
        print(f"Config number: {config_main}")
        return
    elif sensibility == number_try:
        print(f"[Error] Configurations are not in synchronisation. Main: {config_main}, backup: {config_backup}.")
        sys.exit(2)
    else:
        check_config_number(connect_main, connect_backup, number_try, sensibility)
    return


def check_sessions(connect_main, connect_backup, number_try, sensibility=5):
    number_try += 1
    session_main = psql_cmd.get_count_sessions(connect_main)
    session_backup = psql_cmd.get_count_sessions(connect_backup)
    if (int(session_backup) - 1) <= int(session_main) <= int(session_backup):
        print("Sessions are synchronised.")
    elif sensibility == number_try:
        print(f"[Error] Sessions are not in synchronisation. Main: {session_main}, backup: {session_backup}.")
        sys.exit(2)
    else:
        check_sessions(connect_main, connect_backup, number_try, sensibility)
