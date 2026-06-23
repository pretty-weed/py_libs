from _typeshed import Incomplete
from argparse import Action, ArgumentParser, Namespace
from dandy_lib.datatypes.numeric import Infinity as Infinity
from typing import (
    Any,
    Callable,
    NamedTuple,
    Protocol,
    Self,
    Sequence,
    TypeAlias,
)
from webbrowser import get as get

class Named(Protocol):
    name: str

Number: TypeAlias = int | float

class TupleHintedNamespace(Namespace):
    @classmethod
    def for_classes(cls, **fields: type[NamedTuple]) -> type[Self]: ...

IntfinityLiteral = int | float

class Range(NamedTuple):
    start: int
    end: IntfinityLiteral
    arg: str | int
    inclusive: bool = ...
    def is_range(self) -> bool: ...
    @classmethod
    def new(
        cls,
        start: int,
        end: None | IntfinityLiteral = None,
        inclusive: bool = True,
    ): ...
    def __contains__(self, other: Number, inclusive: bool = True) -> bool: ...

class NargsRangeAction(Action):
    n_range: Incomplete
    append_type: Callable[..., Any]
    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        append_type: Callable = ...,
        **kwargs,
    ) -> None: ...
    def __call__(
        self, parser, namespace, values, option_string=None
    ) -> None: ...

class NargsRangeAppendAction(NargsRangeAction):
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

class NamedTupleClass(Protocol): ...

NT_Hint: TypeAlias = Callable[..., tuple[Any, ...]]

class NamedTupleAction(Action):
    NT_CLASS: NT_Hint | None
    def __init__(self, *args, **kwargs) -> None: ...
    @classmethod
    def for_tuple(cls, tuple_type: type[NamedTuple]) -> type[Self]: ...
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Sequence[Any],
        option_string=...,
    ): ...

class AppendNamedTupleAction(NamedTupleAction):
    def __call__(
        self, parser, namespace, values: Sequence[Any], option_string=None
    ): ...
