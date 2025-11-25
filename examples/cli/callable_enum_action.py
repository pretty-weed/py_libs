import argparse
import enum

from dandy_lib.cli.enums import CallableChoiceEnum
from dandy_lib.cli.enums import ChoiceEnum
from dandy_lib.cli.enums import EnumAction


def example():

    class Choices(ChoiceEnum, enum.StrEnum):
        A = "ay"
        B = "bee"
        C = "cee"

    class IntChoices(ChoiceEnum, enum.IntEnum):
        won = 1
        two = 2
        tree = 3

    class FuncChoices(CallableChoiceEnum):

        @enum.member
        def M(inval: str) -> int:
            return int(inval) * int(inval)

        @enum.member
        def A(inval: str) -> str:
            return inval + inval

    parser = argparse.ArgumentParser()

    parser.add_argument("--intval", choices=IntChoices, type=int)
    parser.add_argument(
        "--func",
        action=EnumAction,
        metavar="func",
        nargs=1,
        choices=FuncChoices,
        type=FuncChoices,
    )
    parser.add_argument("value")
    parsed = parser.parse_args()
    if parsed.intval:
        print(parsed.intval)
    if parsed.func:
        print(parsed.func(parsed.value))


if __name__ == "__main__":
    example()
