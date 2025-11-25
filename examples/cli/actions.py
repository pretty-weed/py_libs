import pathlib
from argparse import ArgumentParser

from dandy_lib.cli import parser_actions


class FileExistsError(Exception):
    pass


class TestAction(parser_actions.ConditionalFailingAction):
    EXCEPTIONS_TO_CATCH = (FileExistsError,)

    def _get_val(
        self, parser, namespace, value, option_string=None
    ) -> pathlib.PurePath:
        return pathlib.Path(value)

    def _do_check(
        self,
        parser,
        namespace,
        value,
        result: pathlib.Path,
        option_string=None,
    ) -> None:
        if result.exists():
            raise FileExistsError(f"{value} exists")


def test_with_conflict():
    parser = ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "check_files", action=TestAction, nargs="+", type=pathlib.Path
    )
    print(" ##### PARSER CREATED ##### ")

    parsed = parser.parse_args()

    print(parsed)


def test_me():
    parser = ArgumentParser()
    parser.add_argument(
        "check_files", action=TestAction, nargs="+", type=pathlib.Path
    )
    print(" ##### PARSER CREATED ##### ")

    parsed = parser.parse_args()

    print(parsed)


if __name__ == "__main__":
    # test_me()
    test_with_conflict()
