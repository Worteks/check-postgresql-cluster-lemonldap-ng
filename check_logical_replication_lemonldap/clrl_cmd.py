import postgresql as psql
import sys


def check_config():
    """
    Check configuration for listen_addresses, wal_level and pg_hba file.

    Parameters:
    server_info (dict): Dictionary with server configuration.
    """
    for server in ["main", "backup"]:

        print(f"[Info] * {server.capitalize()} server configuration:")
        psql.get_server_config(server)
        psql.get_replication_config(server)


def check_sync(interval: int = 3):
    """
    Check synchronisation for LemonLDAP configruation, sessions and psessions.

    Parameters:
    interval (int): Intervale to consider sessions synchronised.
    """
    for _ in range(2):
        value = compare_config_number()
        if value:
            break
    else:
        print("[Warning] Configurations are not synchronised")
        sys.exit(1)

    for _ in range(3):
        value = compare_sessions(interval)
        if value:
            break
    else:
        print("[Warning] Sessions are not synchronised")
        sys.exit(1)
    for _ in range(3):
        value = compare_psessions(interval)
        if value:
            break
    else:
        print("[Warning] Sessions are not synchronised")
        sys.exit(1)


def compare_config_number() -> bool:
    """
    Compare the configuration number main and backup, then compare them to
    verify synchronisation.

    Returns:
    bool: Boolean depending on synchronisation.
    """
    config_main = psql.get_config_number("main")
    config_backup = psql.get_config_number("backup")
    if config_main == config_backup:
        print("[Info] Configuration is synchronised.")
        return True
    return False


def compare_sessions(interval: int) -> bool:
    """
    Compare number of sessions on both databases.

    Parameters:
    interval: Integer to define tolerance interval.

    Returns:
    bool: Boolean depending on synchronisation.
    """
    session_main = psql.get_count_sessions("main")
    session_backup = psql.get_count_sessions("backup")
    if abs(session_main - session_backup) <= interval:
        print("[Info] Sessions are synchronised.")
        return True
    return False


def compare_psessions(interval: int) -> bool:
    """
    Compare number of psessions on both databases.

    Parameters:
    interval: Integer to define tolerance interval.

    Returns:
    bool: Boolean depending on synchronisation.
    """
    psession_main = psql.get_count_sessions("main")
    psession_backup = psql.get_count_sessions("backup")
    if abs(psession_main - psession_backup) <= interval:
        print("[Info] Persistent sessions are synchronised.")
        return True
    return False
