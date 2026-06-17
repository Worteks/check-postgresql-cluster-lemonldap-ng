import argparse
import clrl_cmd
from pathlib import Path


def check_sync():
    clrl_cmd.check_sync()


def check_config():
    clrl_cmd.check_config()
    print("[Info] PostgreSQL configuration is ok.")


# Argument parsing
parser = argparse.ArgumentParser(
        prog="check_logical_replication_lemonldap",
        description="Tool to verify configuration and synchronisation of \
                PostgreSQL logical replicationn for LemonLDAP-NG",
        epilog="Thanks for using %(prog)s! :)",)

# Subcommands
subparsers = parser.add_subparsers(
    title="subcommands", help="Operations"
)
subparsers.required = True

sync_parser = subparsers.add_parser(
        "csync",
        help="Verify replication between both PostgreSQL servers.",
        )
sync_parser.set_defaults(func=check_sync)

config_parser = subparsers.add_parser(
        "cconfig",
        help="Check basic logical replication configuration, by default in \
                both servers.",
        )
config_parser.set_defaults(func=check_config)

# Options
parser.add_argument(
        "-v", "--version", action="version",
        version="%(prog)s 0.0.1"
)
parser.add_argument(
        "-c", "--config",
        help="Define à configuration file",
        default="./configuration.local.json",
        type=Path
        )
parser.add_argument(
        "-d", "--debug",
        help="Run in debug mode.",
        action="store_true"
        )

args = parser.parse_args()
DEBUG = args.debug

args.func()

exit(0)
