#!/usr/bin/env bash
set -e

# TODO: Getting configuration from .env file.
# Database configuration
DATABASE=lemonldap
MAIN_USER=writer
MAIN_PASSWORD=writersecret
REPLICATION_USER=replication
REPLICATION_PASSWORD=replicationsecret
PUBLICATION=publication_replication

# SQL command
# Creating users and database.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$REPLICATION_USER') THEN
      CREATE ROLE $REPLICATION_USER LOGIN REPLICATION PASSWORD '$REPLICATION_PASSWORD';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$MAIN_USER') THEN
      CREATE ROLE $MAIN_USER LOGIN PASSWORD '$MAIN_PASSWORD';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DATABASE') THEN
      CREATE DATABASE $DATABASE OWNER writer;
    END IF;
  END
  \$\$;

  -- Giving priviledges to users
  GRANT ALL PRIVILEGES ON DATABASE lemonldap TO $MAIN_USER;
  GRANT ALL PRIVILEGES ON DATABASE lemonldap TO $REPLICATION_USER;
EOSQL

# Creating tables
psql -v ON_ERROR_STOP=1 -q --username "$MAIN_USER" --dbname "$DATABASE" < /docker-entrypoint-initdb.d/lemonldap_tables/config.pg.sql
psql -v ON_ERROR_STOP=1 -q --username "$MAIN_USER" --dbname "$DATABASE" < /docker-entrypoint-initdb.d/lemonldap_tables/sessions.pg.sql

# Adding priviledges to tables
psql -v ON_ERROR_STOP=1 -q --username "$MAIN_USER" --dbname "$DATABASE" <<-EOSQL
  GRANT ALL ON ALL TABLES IN SCHEMA public TO $REPLICATION_USER,$MAIN_USER;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $REPLICATION_USER,$MAIN_USER;
  CREATE PUBLICATION $PUBLICATION FOR ALL TABLES;
EOSQL

# Adding connection configuration
echo "
host  $DATABASE  $REPLICATION_USER  postgres-master.postgres_network  scram-sha-256
host  $DATABASE  $MAIN_USER  postgres-master.postgres_network  scram-sha-256
host  $DATABASE  $REPLICATION_USER  postgres-backup.postgres_network  scram-sha-256
host  $DATABASE  $MAIN_USER  postgres-backup.postgres_network  scram-sha-256
" >> /var/lib/postgresql/data/pg_hba.conf
