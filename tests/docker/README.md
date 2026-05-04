# PostgreSQL dockers

## Starting PostgreSQL containers

Start the docker containers

```bash
docker compose up -d
# I personnaly use when restarted
# docker compose up -d --force-recreate --remove-orphans
```

Stopping the containers

```bash
docker compose down
```

Data inside Database is completely removed everytime the container is erased.
This can be easily modified, but has no interest for testing purposes.

## Writing into the containers

Before starting running the python script, create a LemonLDAP configuration file: `./tools/lmConf-1.json`.

You can then create the logical replication and start writing into the sessions
and lmConfig tables with the following script. The script dependencies are in
`requirements.txt`.

To create the virtual environment

```bash
python3 -m venv venv
# Bash:
source venv/bin/activate
# Fish:
source venv/bin/activate.fish
pip install -r requirements.txt
```

Run the script

```bash
./tools/write.py
```

## Basic commands

Show the logs of both containers as they are created

```bash
docker-compose logs --follow
```

To connect into one of the databases via the client `psql` the following
command can be used

```bash
# Connecting into master
docker exec -it postgres-master /bin/bash -c 'PGPASSWORD=writersecret psql --host postgres-master --username writer -d lemonldap'
# Connecting into backup
docker exec -it postgres-backup /bin/bash -c 'PGPASSWORD=writersecret psql --host postgres-backup --username writer -d lemonldap'
```

## Environment variables

The environment variables for docker composer are in the `.env` files. 
As of today, the `./initdb.d/init.sh` and `./tools/write.py` are independent of
the `.env` file. If variables are modified in the environment file, they must be
modified also in the previous two files.

The docker specifications are in `docker-compose.yaml`.

