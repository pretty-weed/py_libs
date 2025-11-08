from argparse import ArgumentError, ArgumentParser, Namespace
from typing import Any
import unittest
from unittest import mock


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
        if option_string and option_string.startswith("--not_"):
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
            action=SampleAction,
            type=int,
        )

        parsed = parser.parse_args(["--rangeme", "4", "5", "6", "7"])

        self.assertEqual(parsed.rangeme, [4, 5, 6, 7])

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
