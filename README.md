# check-postgresql-cluster-lemonldap-ng
Monitoring script to check if a LL::NG PostgreSQL cluster is in sync

## Configuration file

Configuration file is expected in `json` format. Variables are mostly self explanatory.

Last two variables ,`DB_SUPER_USER` and `DB_SUPER_PASSWORD`, are used to read
the [`pg_hba.conf`](https://www.postgresql.org/docs/16/auth-pg-hba-conf.html) file. This required special privileges in PostgreSQL that replication user may not have. This variables can stay undefined.

An example of configuration file can be found in `check-postgresql-cluster-lemonldap-ng/configuration.json`.

Local configuration must be added in file: `check-postgresql-cluster-lemonldap-ng/configuration.local.json`
to avoid being disturbed by upgrades.

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
  in main server is compared to the number of bakcup sessions. A margin of error
  of 2 is added to account for the time needed to reflect a new connection. This
  is repeated at most 5 times before declaring out of  sync.
