#!/usr/bin/env python3
import psycopg
from time import sleep
import string
import random

# TODO: Getting configuration from the .env file.

# Configuration
dbname = "lemonldap"
port = 5432
host_master = "postgres-master"
host_backup = "postgres-backup"
port_master = 5432
port_backup = 5433
user_repli = "replication"
password_repli = "replicationsecret"
user = "writer"
password = "writersecret"


def id_generator(size=64, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_config_number(dbcursor):
    dbcursor.execute("SELECT max(cfgnum) FROM lmConfig")
    config_number = dbcursor.fetchone()[0]
    if config_number is None:
        print("New table, starting ...")
        config_number = 0
    return config_number


def init_database(dbcursor, config_number):
    if config_number < 20:
        for number in range(config_number, 21):
            write_into_database(dbcursor, number)


def write_into_database(dbcursor, number):
    lemonConfig = open('tools/lmConf-1.json')
    print(f"Writing config number {number}")
    dbcursor.execute("INSERT INTO lmConfig (cfgnum, data) VALUES (%s, %s) ",
                     (number, lemonConfig.read()))
    id_64 = id_generator()
    dbcursor.execute("INSERT INTO sessions (id, a_session) VALUES (%s, %s) ",
                     (id_64,
                      '{"ipAddr":"172.18.0.1","_whatToTrace":"dwho","_session_id":"8ec0997e4ae5b8437149335049510f6e3a5d83438be7bd997ad1ef4a99de6df9","_userDB":"Demo","hGroups":{"users":{"name":"users"},"timelords":{"name":"timelords"}},"_choice":"2_Demo","_session_kind":"SSO","_loginHistory":{"successLogin":[{"ipAddr":"172.18.0.1","_utime":1776933287},{"_utime":1775030212,"ipAddr":"192.168.144.1"},{"_utime":1775030192,"ipAddr":"192.168.144.1"},{"_utime":1774946778,"ipAddr":"192.168.96.1"},{"_utime":1774946690,"ipAddr":"192.168.96.1"}]},"mail":"dwho@badwolf.org","authenticationLevel":1,"groups":"timelords; users","cn":"Doctor Who","_language":"en","_auth":"Demo","uid":"dwho","_updateTime":"20260423103447","UA":"Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0","_utime":1776933287,"_lastAuthnUTime":1776933287,"_user":"dwho","_startTime":"20260423103447"}'))


def replication_statement(host, port, dbname, user, password, serveur):
    # By default, is the main server behaviour
    copy_data = "false"
    if serveur == "backup":
        copy_data = "true"

    replication_statement = f"""CREATE SUBSCRIPTION sub_replication
    CONNECTION 'host={host} port={port} dbname={dbname}
    user={user} password={password}'
    PUBLICATION publication_replication
    WITH (copy_data={copy_data}, origin=none);
    """
    return replication_statement


def create_replication(dbcursor, statement):
    dbcursor.execute("SELECT *  FROM pg_subscription;")
    replication = dbcursor.fetchone()
    if replication is None:
        cursor.execute(statement)
    else:
        print("The replication exists already.")


# Initialize database
with psycopg.connect(host="127.0.0.1", port=port_master, dbname=dbname,
                     user=user, password=password,
                     autocommit=True) as connection:
    cursor = connection.cursor()
    config_number = get_config_number(cursor)
    init_database(cursor, config_number)

# Replication backup reading main
with psycopg.connect(host="127.0.0.1", port=port_backup, dbname=dbname,
                     user=user, password=password,
                     autocommit=True) as connection:
    cursor = connection.cursor()
    statement = replication_statement(host=host_master, port=port,
                                      dbname=dbname, user=user_repli,
                                      password=password_repli,
                                      serveur="backup")
    print("Creating replication backup to main...")
    create_replication(cursor, statement)

# Replication main reading backup
with psycopg.connect(host="127.0.0.1", port=port, dbname=dbname,
                     user=user, password=password,
                     autocommit=True) as connection:
    cursor = connection.cursor()
    statement = replication_statement(host=host_backup, port=port,
                                      dbname=dbname, user=user_repli,
                                      password=password_repli, serveur="main")
    print("Creating replication main to backup...")
    create_replication(cursor, statement)

# Writing ad infinitum
with psycopg.connect(host="127.0.0.1", port=port_master, dbname=dbname,
                     user=user, password=password,
                     autocommit=True) as connection:
    cursor = connection.cursor()
    config_number = get_config_number(cursor) + 1
    while (True):
        write_into_database(cursor, config_number)
        #sleep(0.01)
        config_number += 1
