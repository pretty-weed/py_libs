import pathlib
from argparse import ArgumentParser
from datetime import datetime

from dandy_lib.cli import parser as parser_helpers
from dandy_lib.cli import parser_types

EXAMPLE_OUT = "Example file, please ignore\n"


def test_with_conflict():
    parser = ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("-F", dest="force_overwrite", action="store_true")
    parser.add_argument(
        "sources", action=TestAction, nargs="+", type=pathlib.Path
    )

    parser_helpers.add_output_force_overwrite_to_parser(
        parser, overwrite_flags=["--force"]
    )
    print(" ##### PARSER CREATED ##### ")

    parsed = parser.parse_args()

    print(parsed)


def test_me():
    parser = ArgumentParser()

    parser.add_argument("sources", nargs="+", type=parser_types.path_exists)
    parser_helpers.add_output_force_overwrite_to_parser(parser)
    parsed = parser.parse_args()

    print(parsed)
    prev = (
        "" if not parsed.output.exists() else parsed.output.read_text() + "\n"
    )
    parsed.output.write_text(prev + datetime.now().isoformat() + EXAMPLE_OUT)


if __name__ == "__main__":
    test_me()
    # test_with_conflict()
