from argparse import Action
from argparse import ArgumentError
from argparse import ArgumentParser
from typing import Any
from typing import NamedTuple
from typing import Protocol
from typing import Type
from typing import TypeAlias

Number: TypeAlias = int | float


class Named(Protocol):
    name: str


class Range(NamedTuple):
    start: int
    end: int
    arg: str | int
    inclusive: bool = True

    def is_range(self) -> bool:
        return self.start == self.end

    @classmethod
    def new(cls, start, end=None, inclusive=True):
        """
        Factory to allow for single value ranges
        """
        if end is None:
            arg = start
            match start:
                case "?":
                    start = 0
                    end = 1
                case "*":
                    start = 0
                    end = float("inf")
                case "+":
                    start = 1
                    end = float("inf")
                case int() | number():
                    end = start
                    arg = "+"
                case _:
                    raise ValueError(f"Invalid value for a range: {start}")

        else:
            arg = "+"
        return cls(start, end, arg, inclusive=inclusive)

    # ignore[override] because superclass is object: object
    def __contains__(self, object: Number) -> bool:  # type: ignore[override]
        return self.start <= object <= self.end


class NargsRangeAction(Action):
    """
    Base action to handle a specific range of nargs (e.g. 3 <= num of args <=5)

    As `Action`'s `__call__()` raises exceptions, this class' `__call__()` does
    not call `__super__()`. As such, this should be used as a base class and
    not a mixin.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            try:
                self.n_range = Range.new(*nargs)
            except TypeError:
                self.n_range = Range.new(nargs)
            nargs = self.n_range.arg
        else:
            self.n_range = None
        super().__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):

        match values:
            case list() | tuple():
                pass
            case _:
                values = [values]
        if self.n_range is not None and not len(values) in self.n_range:
            help_name = (
                option_string
                if option_string
                else (self.meta if self.meta else self.dest)
            )
            expected_msg = f"Expected {self.n_range.start}-{self.n_range.end} ({'not' if not self.n_range.inclusive else ''} inclusive)"
            raise ArgumentError(
                self,
                f"Incorrect number of values for {help_name}: {expected_msg}, got {len(values)} ({values}).",
            )


class ConditionalFailingAction(Action):
    EXCEPTIONS_TO_CATCH: tuple[Type[Exception], ...] = (NotImplementedError,)
    FORCE_DEST = "force"
    FORCE_FLAG = "--force"
    FORCE_FLAGS = frozenset(["--force"])

    _force_parsers: dict[str, ArgumentParser] = {}

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)
        if self.FORCE_FLAG not in self.FORCE_FLAGS:
            # could handle this in a metaclass  but meh
            raise ValueError(
                f"the class {self.__class__} is misconfigured, as the force flag is not in all possible force flags"
            )
        if self.FORCE_FLAG not in self._force_parsers:
            force_parser = ArgumentParser()
            force_parser.add_argument(
                *self.FORCE_FLAGS, dest=self.FORCE_DEST, action="store_true"
            )
            self.__class__._force_parsers[self.FORCE_FLAG] = force_parser

        parsed, _unparsed = self._force_parsers[
            self.FORCE_FLAG
        ].parse_known_args()
        self.force = getattr(parsed, self.FORCE_DEST)

    def _get_val(self, parser, namespace, values, option_string=None) -> Any:
        raise NotImplementedError()

    def _do_check(
        self, parser, namespace, values, result, option_string=None
    ) -> None:
        raise NotImplementedError()

    def __call__(self, parser, namespace, values, option_string=None):
        single_result: bool = None
        try:
            results = [
                self._get_val(parser, namespace, value, option_string)
                for value in values
            ]
        except TypeError:
            # single item
            results = [self._get_val(parser, namespace, values, option_string)]
            values = [values]
            single_result = True
        else:
            single_result = False

        for result, value in zip(results, values):
            try:
                self._do_check(
                    parser,
                    namespace,
                    value,
                    result,
                    option_string=option_string,
                )
            except self.EXCEPTIONS_TO_CATCH as exc:
                if not self.force:
                    raise exc
                print("forced")

        setattr(namespace, self.dest, results[0] if single_result else results)
