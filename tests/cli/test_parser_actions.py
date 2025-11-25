import argparse
import random
from contextlib import ExitStack
from typing import Any
from unittest import mock

import dandy_lib.cli.parser_actions as pa
import pytest


@pytest.fixture(scope="function")
def subtest(subtests: pytest.Subtests):
    yield subtests


class SampleAction(pa.NargsRangeAction):
    """
    Insert opposites when `--option_string` starts with `--not_`.
    for some reason needs the range of nargs.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ):
        super().__call__(parser, namespace, values, option_string=option_string)
        if option_string and option_string.startswith("--rev_"):
            match values:
                case list() | tuple() | str():
                    values = values.__class__(reversed(values))
        setattr(namespace, self.dest, values)


@pytest.mark.usefixtures("subtest")
def test_stringsAndLiteralNumber(subtest: pytest.Subtests):
    intstrs = "0123456789"
    for nargs, start, end in [
        ("?", 0, 1),
        ("*", 0, float("inf")),
        ("+", 1, float("inf")),
        (3, 3, 3),
    ]:
        with subtest.test(str(nargs), nvars=nargs):
            parser = argparse.ArgumentParser(exit_on_error=False)
            parser.add_argument(
                "--foo", nargs=nargs, action=SampleAction, type=int  # type: ignore
            )

            # check that fewer than desired (if possible) throws error

            if start > 0:
                with subtest.test("checking that fails with zero args"):
                    with pytest.raises(argparse.ArgumentError):
                        parser.parse_args(["--foo"])

            if start > 1:
                # with pytest.raises(argparse.ArgumentError) as exc_info:
                with subtest.test("1 arg fewer than min fails", nargs=nargs):
                    with pytest.raises(argparse.ArgumentError):
                        parser.parse_args(
                            ["--foo", *random.choices(intstrs, k=start - 1)]
                        )

                with subtest.test("min and max num of args pass", nargs=nargs):
                    parser.parse_args(
                        ["--foo", *random.choices(intstrs, k=start)]
                    )

            if end < float("inf"):
                with subtest.test("too many args fails", nargs=nargs):
                    with pytest.raises(argparse.ArgumentError):

                        parser.parse_args(
                            ["--foo", *random.choices(intstrs, k=int(end + 1))]
                        )

                with subtest.test("max args passes", nargs=nargs):
                    parser.parse_args(
                        ["--foo", *random.choices(intstrs, k=int(end))]
                    )


def test_working():
    parser = argparse.ArgumentParser(exit_on_error=False)

    parser.add_argument(
        "--rev_rangeme",
        nargs=(3, 5),
        action=SampleAction,
        type=int,
    )

    parsed = parser.parse_args(["--rev_rangeme", "4", "5", "6", "7"])

    assert parsed.rev_rangeme == [7, 6, 5, 4]


@pytest.mark.usefixtures("subtest")
def test_out_of_range(subtest: pytest.Subtests):

    parser = argparse.ArgumentParser(exit_on_error=False)

    parser.add_argument(
        "--three_five",
        dest="t",
        nargs=(3, 5),  # type: ignore
        type=int,
        action=SampleAction,
    )
    with subtest.test("One argument when 3-5 are expected"):
        with pytest.raises(argparse.ArgumentError) as cm:
            parser.parse_args(["--three_five", "1"])

    for arg_list in [list(range(1, ll + 1)) for ll in range(3, 6)]:
        with subtest.test("Check that args work", args=arg_list):
            assert (
                parser.parse_args(
                    ["--three_five", *[str(i) for i in arg_list]]
                ).t
                == arg_list
            )
    with subtest.test("Check that too many args fails"):
        with pytest.raises(argparse.ArgumentError):
            parser.parse_args(
                ["--three_five", "1", "2", "3", "4", "5", "6", "7", "8"]
            )
