from argparse import ArgumentError, ArgumentParser, Namespace
from typing import Any, Literal, NamedTuple
import unittest
from unittest import mock


from contextlib import ExitStack

import pytest


import dandy_lib.cli.parser_actions as pa

from dandy_lib.cli.parser_actions import (
    NargsRangeAction,
    NargsRangeAppendAction,
)


class SampleAction(pa.NargsRangeAction):
    """
    Insert opposites when `--option_string` starts with `--not_`.
    for some reason needs the range of nargs.
    """

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Any,
        option_string: str | None = None,
    ):
        super().__call__(parser, namespace, values, option_string=option_string)
        if option_string and any(
            option_string.startswith(prefix) for prefix in ["--not_", "--rev_"]
        ):
            match values:
                case list() | tuple() | str():
                    values = values.__class__(reversed(values))
                case int() | float():
                    values = -values
                case bool():
                    values = not values

        setattr(namespace, self.dest, values)


class TestNargsRange(unittest.TestCase):

    def test_working(self):
        parser = ArgumentParser(exit_on_error=False)

        parser.add_argument(
            "--rangeme",
            nargs=(3, 5),
            action=NargsRangeAction,
            type=int,
        )

        parsed = parser.parse_args(["--rangeme", "4", "5", "6", "7"])

        self.assertEqual(parsed.rangeme, [4, 5, 6, 7])

    def test_bad_type(self) -> None:
        parser = ArgumentParser(exit_on_error=False)
        parser.add_argument(
            "rangeme", nargs=(3, 5), action=NargsRangeAction, type=int  # type: ignore[arg-type]
        )

        parsed = parser.parse_args(list("135"))
        self.assertListEqual(parsed.rangeme, [1, 3, 5])
        parsed = parser.parse_args(list("13579"))
        self.assertListEqual(parsed.rangeme, [1, 3, 5, 7, 9])
        with self.assertRaises(ArgumentError):
            _ = parser.parse_args(list[str]("123456"))
        with self.assertRaises(ArgumentError):
            _ = parser.parse_args(["1.2", "3.5", "5.6"])

    def test_out_of_range(self) -> None:

        parser = ArgumentParser(exit_on_error=False)

        parser.add_argument(
            "--three_five",
            dest="t",
            nargs=(3, 5),  # type: ignore[arg-type]
            type=int,
            action=NargsRangeAction,
        )

        with self.assertRaises(ArgumentError):
            parser.parse_args(["--three_five", "1"])

        for arg_list in [list(range(1, ll + 1)) for ll in range(3, 6)]:

            self.assertEqual(
                parser.parse_args(
                    ["--three_five", *[str(i) for i in arg_list]]
                ).t,
                arg_list,
            )

        with self.assertRaises(ArgumentError):
            parser.parse_args(
                ["--three_five", "1", "2", "3", "4", "5", "6", "7", "8"]
            )


class TestNargsRangeAppend(unittest.TestCase):
    def test_working(self):
        parser = ArgumentParser(exit_on_error=False)

        parser.add_argument(
            "--rangeme",
            nargs=(3, 5),
            action=NargsRangeAppendAction,
            type=int,
        )
        with self.subTest("single append"):
            parsed = parser.parse_args(["--rangeme", "4", "5", "6", "7"])
            self.assertEqual(parsed.rangeme, [[4, 5, 6, 7]])
        with self.subTest("two appends"):
            parsed = parser.parse_args(
                [
                    "--rangeme",
                    "4",
                    "5",
                    "6",
                    "7",
                    "--rangeme",
                    "8",
                    "9",
                    "10",
                    "11",
                ]
            )
            self.assertEqual(parsed.rangeme, [[4, 5, 6, 7], [8, 9, 10, 11]])


class Case(NamedTuple):
    nargs: str | int
    minArgs: int
    maxArgs: int | float

    def __str__(self) -> str:
        return f"<Test Case: nargs: {self.nargs}, start: {self.minArgs}, end: {self.maxArgs}>"


def test_stringsAndLiteralNumber(subtests: pytest.Subtests):
    intstrs = "0123456789"
    cases: list[Case] = [  # type: ignore[call-overload]
        Case("?", 0, 1),
        Case("*", 0, float("inf")),
        Case("+", 1, float("inf")),
        Case(3, 3, 3),
    ]

    for case in cases:
        nargs, start, end = case
        with subtests.test(str(case)):
            parser = ArgumentParser(exit_on_error=False)
            parser.add_argument(
                "--foo", nargs=nargs, action=NargsRangeAction, type=int
            )

            # check that fewer than desired (if possible) throws error

            if start > 0:
                with subtests.test("checking that fails with zero args"):
                    with pytest.raises(ArgumentError):
                        parser.parse_args(["--foo"])

            if start > 1:
                # with pytest.raises(argparse.ArgumentError) as exc_info:
                with subtests.test("1 arg fewer than min fails", nargs=nargs):
                    with pytest.raises(ArgumentError):
                        vars = ["--foo"] + list(intstrs[: start - 1])
                        parser.parse_args(vars)

                with subtests.test("min and max num of args pass", nargs=nargs):
                    parser.parse_args(["--foo", *intstrs[:start]])

            if end < float("inf"):
                with subtests.test("too many args fails", nargs=nargs):
                    with pytest.raises(ArgumentError):
                        vars = ["--foo"] + list(intstrs[: int(end) + 1])
                        parser.parse_args(vars)

                with subtests.test("max args passes", nargs=nargs):
                    parser.parse_args(["--foo", *intstrs[: int(end)]])


def test_working():
    parser = ArgumentParser(exit_on_error=False)

    parser.add_argument(
        "--rev_rangeme",
        nargs=(3, 5),  # type: ignore[arg-type]
        action=SampleAction,
        type=int,
    )

    parsed = parser.parse_args(["--rev_rangeme", "4", "5", "6", "7"])

    assert parsed.rev_rangeme == [7, 6, 5, 4]


def test_out_of_range(subtests: pytest.Subtests):

    parser = ArgumentParser(exit_on_error=False)

    parser.add_argument(
        "--three_five",
        dest="t",
        nargs=(3, 5),  # type: ignore
        type=int,
        action=NargsRangeAction,
    )
    with subtests.test("One argument when 3-5 are expected"):
        with pytest.raises(ArgumentError) as cm:
            parser.parse_args(["--three_five", "1"])

    for arg_list in [list(range(1, ll + 1)) for ll in range(3, 6)]:
        with subtests.test("Check that args work", args=arg_list):
            assert (
                parser.parse_args(
                    ["--three_five", *[str(i) for i in arg_list]]
                ).t
                == arg_list
            )
    with subtests.test("Check that too many args fails"):
        with pytest.raises(ArgumentError):
            parser.parse_args(
                ["--three_five", "1", "2", "3", "4", "5", "6", "7", "8"]
            )
