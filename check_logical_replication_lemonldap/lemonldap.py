import psycopg
import postgresql as psql


def get_count_sessions(connect: psycopg.Connection):
    count_sessions = psql.sql_command_error_catching(connect,
                                                "SELECT count(*) FROM sessions")
    return count_sessions


def get_config_number(connect: psycopg.Connection):
    config_number = psql.sql_command_error_catching(connect,
                                               "SELECT max(cfgnum) FROM lmConfig")
    return config_number


def check_read_tables(connect: psycopg.Connection):
    tables = ["lmConfig", "sessions", "psessions"]
    for table in tables:
        psql.sql_command_error_catching(connect,
                                        f"SELECT * from {table} LIMIT 2")
