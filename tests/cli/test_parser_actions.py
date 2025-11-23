from argparse import ArgumentError, ArgumentParser, Namespace
from typing import Any
import unittest
from unittest import mock
import random

import dandy_lib.cli.parser_actions as pa


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
        if option_string and option_string.startswith("--rev_"):
            match values:
                case list() | tuple() | str():
                    values = values.__class__(reversed(values))
        print(parser)
        print("namespace is", namespace)
        setattr(namespace, self.dest, values)


class TestNargsRange(unittest.TestCase):

    def test_stringsAndLiteralNumber(self):
        intstrs = "0123456789"
        for nargs, start, end in [
            ("?", 0, 1),
            ("*", 0, float("inf")),
            ("+", 1, float("inf")),
            (3, 3, 3),
        ]:
            with self.subTest(str(nargs), nvars=nargs):
                parser = ArgumentParser(exit_on_error=False)
                parser.add_argument(
                    "--foo", nargs=nargs, action=SampleAction, type=int
                )

                # check that fewer than desired (if possible) throws error

                if start > 0:
                    with self.assertRaises(ArgumentError):
                        parser.parse_args("--foo")

                    if start > 1:
                        with self.assertRaises(ArgumentError):
                            parser.parse_args(
                                "--foo", *random.choices(intstrs)[: start - 1]
                            )

                        parser.parse_args(
                            "--foo", *random.choices(intstrs)[:start]
                        )

    def test_working(self):
        parser = ArgumentParser(exit_on_error=False)

        parser.add_argument(
            "--rev_rangeme",
            nargs=(3, 5),
            action=SampleAction,
            type=int,
        )

        parsed = parser.parse_args(["--rev_rangeme", "4", "5", "6", "7"])

        self.assertEqual(parsed.rev_rangeme, [7, 6, 5, 4])

    def test_out_of_range(self):

        parser = ArgumentParser(exit_on_error=False)

        parser.add_argument(
            "--three_five",
            dest="t",
            nargs=(3, 5),
            type=int,
            action=SampleAction,
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
