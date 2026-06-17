# check-postgresql-cluster-lemonldap-ng
Monitoring script to check if a LL::NG PostgreSQL cluster is in sync

## Configuration file

Configuration file is expected in as `.env` file. Variables are mostly self explanatory.
You can copy the `env.bckp` file to start with obligatory variables.

```bash
cp env.bckp .env
```

Local configuration most include `URL_MAIN` and `URL_BACKUP` for `csync` command.

Local configuration most include `ADMIN_URL_MAIN` and `ADMIN_URL_BACKUP` for `cconfig` command.

## Commands

### Check configuration

> A `admin` user is needed for all checks.

The `cconfig` command verify minimal configuration needed for logical replication.

The parameters of PostgreSQL instance shown are:

- `listen_addresses = *`, other configurations may work. Only a warning is
  shown for this attribute.
- `wal_level = logical`, a error is shown since this is a necessary value.
- `pg_hba_file_rules` entries with the replication user are shown.

Also the subscriptions into LemonLDAP database are shown.

An example of the command:

```bash
$ ./check_logical_replication_lemonldap.py cconfig
[Info] * Main server configuration:
[Info] listen_adresses set as: *.
[Info] WAL level set as: logical.
[Info] pg_hba.conf => host: postgres-master.postgres_network, db: lemonldap, user: replication
[Info] pg_hba.conf => host: postgres-backup.postgres_network, db: lemonldap, user: replication
[Info] Subscriptions =>  host=postgres-backup port=5432 dbname=lemonldap user=replication
[Info] * Backup server configuration:
[Info] listen_adresses set as: *.
[Info] WAL level set as: logical.
[Info] pg_hba.conf => host: postgres-master.postgres_network, db: lemonldap, user: replication
[Info] pg_hba.conf => host: postgres-backup.postgres_network, db: lemonldap, user: replication
[Info] Subscriptions =>  host=postgres-master port=5432 dbname=lemonldap user=replication
```

### Check synchronisation

The `check-sync` verify if both LemonLDAP databases are synchronized. This is
achieved by comparing the value of LemonLDAP configuration number, the total
number of sessions and the total number of persistent sessions.

For sessions a difference of +/-3 sessions is accepted as synchronized.

An example of the command:

```bash
$ ./check_logical_replication_lemonldap.py csync
[Info] Configuration is synchronised.
[Info] Sessions are synchronised.
[Info] Persistent sessions are synchronised.
```

## Installation


| OS       | Tested                    |
| -------- | ------------------------- |
| Debian13 | ok                        |
| Debian12 | ok                        |
| Debian11 | `python3-psycopg` missing |


Clone de repository with latest tag into the server. For example:

```bash
git clone --branch v0.1.0 https://github.com/Worteks/check-postgresql-cluster-lemonldap-ng.git
```

Install dependencies
```bash
# Debian
sudo apt install python3-psycopg python3-sqlalchemy python3-dotenv
# RHEL or clone
sudo dnf install epel-release
sudo dnf install python3-psycopg3 python3-sqlalchemy python3-dotenv
# Fedora
sudo dnf install python3-psycopg3 python3-sqlalchemy python3-dotenv
```

> If the OS version is not compatible, you can use a virtual environment. See below.

Define configuration, see configuration section at the top.

### Installation via a virtual environment

The repository comes with a `requirements.txt` file to create your virtual
environment.

```bash
cd check_logical_replication_lemonldap/
python3 -m pip venv .venv
python3 -m pip install -r requirements.txt
```

## Project wishlist

- Adding [logging](https://docs.python.org/3/library/logging.html) and verbose.
- Add code formatting: [ruff](https://docs.astral.sh/ruff/)
- Add type hinting.
- Add test [pytest](http://pytest.org)
- Add class for servers.
- Adding docstrings to functions.
