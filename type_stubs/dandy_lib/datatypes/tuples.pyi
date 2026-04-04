from collections import namedtuple as namedtuple
from collections.abc import Iterable as Iterable
from enum import IntEnum
from typing import Any, Callable, NamedTupleMeta, Self

def get_annotate_from_class_namespace(obj: dict[str, Any]) -> Any: ...
def call_annotate_function(
    annotate: Callable[[int], dict[str, type]], format
) -> dict[str, type]: ...

class Format(IntEnum):
    VALUE = 1
    VALUE_WITH_FAKE_GLOBALS = 2
    FORWARDREF = 3
    STRING = 4

ANNOTATIONS: str
ANNOTATE_FUNC: str

class MixinableNamedTupleMeta(NamedTupleMeta):
    def __new__(
        cls, typename, bases: list[type], ns: dict[str, Any]
    ) -> Self: ...

MixableNamedTupleBase: NamedTupleMeta

def MixableNamedTuple(
    typename: str,
    fields: list[tuple[str, type]] | None = None,
    bases: list[type] | None = None,
    /,
    **kwargs: Any,
) -> type[tuple]: ...
