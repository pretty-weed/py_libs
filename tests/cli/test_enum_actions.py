import argparse
import enum
import random
from contextlib import ExitStack
from typing import Any
from unittest import mock

import pytest
from dandy_lib.cli.enums import CallableChoiceEnum
from dandy_lib.cli.enums import ChoiceEnum
from dandy_lib.cli.enums import EnumAction


@pytest.fixture(scope="function")
def subtest(subtests: pytest.Subtests):
    yield subtests


class FuncChoices(CallableChoiceEnum):

    @enum.member
    def M(inval: str) -> int:
        return int(inval) * int(inval)

    @enum.member
    def APPEND(inval: str) -> str:
        return inval + inval


class IntChoices(ChoiceEnum, enum.IntEnum):
    won = 1
    two = 2
    tree = 3


@pytest.mark.usefixtures("subtest")
def test_stringsAndLiteralNumber(subtest: pytest.Subtests):
    parser = argparse.ArgumentParser(exit_on_error=False)

    parser.add_argument("--intval", choices=IntChoices, type=int)
    parser.add_argument(
        "--func",
        action=EnumAction,
        metavar="func",
        nargs=1,
        choices=FuncChoices,
        type=FuncChoices,
    )
    with subtest.test("simple int enum"):
        with pytest.raises(argparse.ArgumentError):
            parsed = parser.parse_args(["--intval", "won"])
            assert parsed.intval == 1

    with subtest.test("incorrect intenum fails"):
        with pytest.raises(argparse.ArgumentError):
            parser.parse_args(["--intval", "freeb"])

    with subtest.test("function choices: 0"):
        parsed = parser.parse_args(["--func", "M"])
        assert parsed.func in FuncChoices
        assert parsed.func(3) == 9

    with subtest.test("function choices: 1"):
        parsed = parser.parse_args(["--func", "APPEND"])

        assert parsed.func in FuncChoices
        assert parsed.func("foo") == "foofoo"
