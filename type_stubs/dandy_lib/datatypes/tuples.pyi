from collections import namedtuple
from collections.abc import Iterable as Iterable
from copy import copy as copy
from typing import Any, NamedTuple, NamedTupleMeta, Self

ANNOTATIONS: str

class MixinableNamedTupleMeta(NamedTupleMeta):
    def __new__(
        cls, typename, bases: list[type], ns: dict[str, Any]
    ) -> Self: ...

MixableNamedTupleBase: NamedTupleMeta

class MixableNamedTuple(NamedTuple):
    pass
