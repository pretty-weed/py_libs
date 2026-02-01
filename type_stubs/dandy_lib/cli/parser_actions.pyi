from _typeshed import Incomplete
from argparse import Action
from typing import NamedTuple, Protocol, TypeAlias

Number: TypeAlias = int | float

class Named(Protocol):
    name: str

class Range(NamedTuple):
    start: int
    end: int
    arg: str | int
    inclusive: bool = ...
    def is_range(self) -> bool: ...
    @classmethod
    def new(cls, start, end=None, inclusive: bool = True): ...
    def __contains__(self, object: Number) -> bool: ...

class NargsRangeAction(Action):
    n_range: Incomplete
    def __init__(self, option_strings, dest, nargs=None, **kwargs) -> None: ...
    def __call__(
        self, parser, namespace, values, option_string=None
    ) -> None: ...

class ConditionalFailingAction(Action):
    EXCEPTIONS_TO_CATCH: tuple[type[Exception], ...]
    FORCE_DEST: str
    FORCE_FLAG: str
    FORCE_FLAGS: Incomplete
    force: Incomplete
    def __init__(self, option_strings, dest, nargs=None, **kwargs) -> None: ...
    def __call__(
        self, parser, namespace, values, option_string=None
    ) -> None: ...
