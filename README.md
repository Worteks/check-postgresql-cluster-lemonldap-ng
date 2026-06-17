# check-postgresql-cluster-lemonldap-ng
Monitoring script to check if a LL::NG PostgreSQL cluster is in sync

## Configuration file

Configuration file is expected in as `.env` file. Variables are mostly self explanatory.
You can copy the `env.bckp` file to start with obligatory variables.

```bash
cp env.bckp .env
```

Local configuration most include at least the `main` and `backup` server parameters;
except for  `super_user` and `super_password`. This two last variables are used to read the
[`pg_hba.conf`](https://www.postgresql.org/docs/16/auth-pg-hba-conf.html) file which requires special privileges in PostgreSQL.

## Commands

### Check connection

The `check-connection` command verify the connection to both databases from
local server via the replication user.

To be exhaustive, `check-postgresql-cluster-lemonldap-ng` should be run in both
servers. Nevertheless, it is easier to test via the `psql` during the initial
setup for a logical replication installation. 

For example: 

```bash
PGPASSWORD=$PASSWORD psql -h $HOST -p $PORT -U "$REPLICATION" -d "$DATABASE"
```

### Check configuration

The `check-config` command verify logical replication parameters in PostgreSQL instance:

- `listen_addresses = *`, other configurations may work. Only a warning is
  shown for this attribute.
- `wal_level = logical`, a error is shown since this is a necessary value.

If `pg_hba_file_rules` view is readable via a super user, the `pg_hba.conf`
entries with the replication user are shown. If not, a warning is shown.

> If a `super_user` is badly configured, this will result in an error.

### Check synchronisation

The `check-sync` command is based in two simple calculations:

- Get the latest configuration number for both databases. This table is the main
  reason for replication, hence the verification. Most installations will be low
  traffic. 
- Count the number of entries in the `sessions` tables. The number of sessions
  in main server is compared to the number of backup sessions. A margin of error
  of 2 is added to account for the time needed to reflect a new connection. This
  is repeated at most 5 times before declaring out of  sync.

## Installation


| OS       | Tested                    |
| -------- | ------------------------- |
| Debian13 | ok                        |
| Debian12 | ok                        |
| Debian11 | `python3-psycopg` missing |


Clone de repository into the server

```bash
git clone https://github.com/Worteks/check-postgresql-cluster-lemonldap-ng.git
```

Install dependencies
```bash
# Debian
# Fedora
sudo apt install python3-psycopg python3-sqlalchemy python3-dotenv
sudo dnf install python3-psycopg3
```

> If the OS psycopg version is not compatible, you can use a virtual environment, see
> below for configuration.

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
