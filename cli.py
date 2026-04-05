#!/usr/bin/env python3
"""CLI tool for agroforestal management with permission controls."""

import argparse
import sys


def create_parser():
    """Create the argument parser with all CLI flags."""
    parser = argparse.ArgumentParser(
        prog="agroforestal",
        description="Agroforestal management CLI tool",
    )
    parser.add_argument(
        "--dangerously-skip-permissions",
        action="store_true",
        default=False,
        help=(
            "Skip all permission checks before executing commands. "
            "WARNING: This bypasses safety checks and should only be used "
            "in trusted environments (e.g., CI pipelines, local development)."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'run' command
    run_parser = subparsers.add_parser("run", help="Run an agroforestal operation")
    run_parser.add_argument("operation", help="The operation to run")

    # 'config' command
    config_parser = subparsers.add_parser("config", help="View or modify configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current config")

    return parser


def check_permissions(operation):
    """Check if the current user has permissions for the given operation.

    Returns True if permitted, False otherwise.
    """
    # Placeholder: in a real system this would check user roles, ACLs, etc.
    restricted_operations = {"delete", "reset", "migrate"}
    if operation in restricted_operations:
        return False
    return True


def run_operation(operation, skip_permissions=False):
    """Execute an agroforestal operation with optional permission bypass."""
    if not skip_permissions:
        if not check_permissions(operation):
            print(
                f"Error: Permission denied for operation '{operation}'. "
                "Use --dangerously-skip-permissions to bypass.",
                file=sys.stderr,
            )
            return 1
    else:
        print(
            f"WARNING: Skipping permission checks for '{operation}'.",
            file=sys.stderr,
        )

    print(f"Executing operation: {operation}")
    return 0


def show_config(skip_permissions=False):
    """Display the current configuration."""
    config = {
        "permissions_enabled": not skip_permissions,
        "environment": "development",
    }
    for key, value in config.items():
        print(f"{key}: {value}")
    return 0


def main(argv=None):
    """Entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    skip = args.dangerously_skip_permissions

    if args.command == "run":
        return run_operation(args.operation, skip_permissions=skip)
    elif args.command == "config":
        if args.show:
            return show_config(skip_permissions=skip)
        parser.parse_args(["config", "--help"])
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
