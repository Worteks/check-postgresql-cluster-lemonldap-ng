import argparse
import clrl_cmd

# This is the main script.
# We parse the arguments and options and return adapt exit codes and messages.


def check_sync(configuration: dict):
    clrl_cmd.check_sync(configuration['main'], configuration['backup'])


def check_config(configuration: dict):
    for server in configuration.keys():
        messages = clrl_cmd.check_config(configuration[server])
        print(f"* {server.capitalize()} server configuration: ok")
        if messages:
            for message in messages:
                print(message)


def check_connection(configuration: dict):
    for server in configuration.keys():
        clrl_cmd.check_connection(configuration[server])
        print(f"* Connection from local to {server}: ok")


# Argument parsing

parser = argparse.ArgumentParser(
        prog="check_logical_replication_lemonldap",
        description="Tool to verify configuration and synchronisation of PostgreSQL logical replicationn for LemonLDAP-NG",
        epilog="Thanks for using %(prog)s! :)",)

# Subcommands
subparsers = parser.add_subparsers(
    title="subcommands", help="Operations"
)

sync_parser = subparsers.add_parser(
        "check-sync",
        help="Verify replication between both PostgreSQL servers.",
        )
sync_parser.set_defaults(func=check_sync)

config_parser = subparsers.add_parser(
        "check-config",
        help="Check basic logical replication configuration, by default in both servers.",
        )
config_parser.set_defaults(func=check_config)

connection_parser = subparsers.add_parser(
        "check-connection",
        help="Test connection from running server into both servers.",
        )
connection_parser.set_defaults(func=check_connection)

# Options
parser.add_argument(
        "--version", action="version",
        version="%(prog)s 0.0.1"
)
parser.add_argument(
        "-c", "--config",
        help="Define à configuration file",
        default="./configuration.local.json",
        type=str
        )
parser.add_argument(
        # Not yet in use.
        "-v", "--verbose",
        help="Increase output verbosity.",
        action="store_true"
        )

args = parser.parse_args()


configuration = clrl_cmd.define_configuration(args.config)

args.func(configuration)

exit(0)
