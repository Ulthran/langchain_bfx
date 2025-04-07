import argparse
import sys


def main(argv):
    parser = argparse.ArgumentParser(
        description="Command line interface for LangChain BFX."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Add subcommands here
    # Example: 
    # subparser = subparsers.add_parser("example", help="Example command")
    # subparser.add_argument("arg1", type=str, help="Argument 1")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Handle subcommands here
    # Example:
    # if args.command == "example":
    #     print(f"Running example command with arg1: {args.arg1}")