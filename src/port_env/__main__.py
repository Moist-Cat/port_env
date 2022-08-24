import argparse
from typing import List
import sys

from port_env import command


def get_command(argv: List[str] = sys.argv[1:]): # pylint: disable=W0102
    """Get and parse command"""
    parser = argparse.ArgumentParser(description="Fix python virtual envionments after being moved")
    parser.set_defaults(func=command.main)

    parser.add_argument(
        "path",
        type=str,
        default="env",
        help="Path of the virtual environment",
    )

    parser.add_argument(
        "--fix_third_party",
        "-tp",
        help="Whether or not to fix site-packages python version",
    )

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    get_command()
