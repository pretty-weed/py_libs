from argparse import ArgumentParser, ArgumentError
import enum
import random
from contextlib import ExitStack
from typing import Any, Callable, ParamSpec, TypeVar
from unittest import mock

import pytest
from dandy_lib.cli.enums import (
    CallableChoiceEnumMixin,
    ChoiceEnumMixin,
    EnumAction,
)


@pytest.fixture(scope="function")
def subtest(subtests: pytest.Subtests):
    yield subtests


class FuncChoices(CallableChoiceEnumMixin, enum.Enum):

    @enum.member
    def M(inval: str) -> int:
        return int(inval) * int(inval)

    @enum.member
    def APPEND(inval: str) -> str:
        return inval + inval


class IntChoices(ChoiceEnumMixin, enum.IntEnum):
    won = 1
    two = 2
    tree = 3


class CustomChoicesType:
    def __init__(self, a, b, c="merp"):
        self.a = a
        self.b = b
        self.c = c


class CustomChoices(CustomChoicesType, ChoiceEnumMixin, enum.Enum):
    A = (1, 2)
    B = (3, 4, "cheese")


class CustomChoicesIntType(int):
    def __new__(self, val, foo=2, bar=3):
        return super().__new__(self, val)

    def __init__(self, val, foo=2, bar=3) -> None:
        self.foo = foo
        self.bar = bar
        assert int(self) == val
        super().__init__()


class CustomChoicesInt(CustomChoicesIntType, ChoiceEnumMixin, enum.Enum):
    A = (1, 2)
    B = (3, 4, "cheese")


@pytest.fixture
def parser_factory[**P]() -> Callable[P, ArgumentParser]:
    def factory(*args, exit_on_error=False, **kwargs) -> ArgumentParser:
        # The ignore ignores this error, which is incorrect, unless someone
        # passes enough positional arguments
        # "ArgumentParser" gets multiple values for keyword argument "exit_on_error"
        return ArgumentParser(
            *args, exit_on_error=exit_on_error, **kwargs
        )  # type: ignore[misc]

    return factory


@pytest.mark.usefixtures("subtest")
def test_stringsAndLiteralNumber(
    subtest: pytest.Subtests, parser_factory: Callable[..., ArgumentParser]
):
    parser = parser_factory()
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
        with pytest.raises(ArgumentError):
            parsed = parser.parse_args(["--intval", "won"])
            assert parsed.intval == 1

    with subtest.test("incorrect intenum fails"):
        with pytest.raises(ArgumentError):
            parser.parse_args(["--intval", "freeb"])

    with subtest.test("function choices: 0"):
        parsed = parser.parse_args(["--func", "M"])
        assert parsed.func in FuncChoices
        assert parsed.func(3) == 9

    with subtest.test("function choices: 1"):
        parsed = parser.parse_args(["--func", "APPEND"])

        assert parsed.func in FuncChoices
        assert parsed.func("foo") == "foofoo"


def test_custom_class(
    subtest: pytest.Subtests, parser_factory: Callable[..., ArgumentParser]
) -> None:
    with subtest.test(
        "Custom type inheriting only from object, with only choices and action"
    ):

        parser = parser_factory()
        parser.add_argument("test_me", choices=CustomChoices, action=EnumAction)

        with pytest.raises(ArgumentError):
            parser.parse_args(["mlerp"])

        parsed = parser.parse_args("A")
        assert parsed.test_me == CustomChoices.A

    with subtest.test("Providing custom type only with type and action"):
        parser = parser_factory()
        parser.add_argument("test_me", type=CustomChoices, action=EnumAction)  # type: ignore[arg-type]
        assert parser.parse_args("B").test_me == CustomChoices.B

    with subtest.test("Providing custom type with type, choices and action"):
        parser = parser_factory()
        parser.add_argument(
            "test_me",
            type=CustomChoices,  # type: ignore[arg-type]
            choices=CustomChoices,
            action=EnumAction,
        )
        assert parser.parse_args("A").test_me == CustomChoices.A

    with subtest.test(
        "Check that mismatching type and choices fails the action"
    ):
        parser = parser_factory()
        with pytest.raises(TypeError):
            parser.add_argument(
                "no worky",
                type=CustomChoices,  # type: ignore[arg-type]
                choices=["A", "B"],
                action=EnumAction,
            )

    with subtest.test("Check that invalid args for class fails"):

        with pytest.raises(TypeError):

            class BadChoices(CustomChoicesType, ChoiceEnumMixin, enum.Enum):
                A = (1, 2)
                B = (3, 4, "cheese")
                C = (None,)
