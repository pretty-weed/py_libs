from .numeric import (
    NonNegFloat as NonNegFloat,
    NonNegInt as NonNegInt,
    NonNegNum as NonNegNum,
)
from .tuples import MixableNamedTuple as MixableNamedTuple
from functools import lru_cache
from typing import NamedTuple

class Size(MixableNamedTuple):
    width: NonNegNum
    height: NonNegNum
    @classmethod
    def factory(cls, *in_vals: NonNegNum): ...

type Number = int | float

class Vector(NamedTuple):
    x: Number
    y: Number

ZERO_VEC: Vector

class Coord(Vector): ...

ZERO_COORD: Coord

class Rect(MixableNamedTuple):
    position: Coord
    size: Size
    def __getattr__(self, name: str) -> Number: ...
    @property
    @lru_cache
    def top(self) -> Number: ...
    @property
    @lru_cache
    def bottom(self) -> Number: ...
    @property
    @lru_cache
    def left(self) -> Number: ...
    @property
    @lru_cache
    def right(self) -> Number: ...
    @property
    @lru_cache
    def top_left(self) -> Coord: ...
    @property
    @lru_cache
    def bottom_left(self) -> Coord: ...
    @property
    @lru_cache
    def top_right(self) -> Coord: ...
    @property
    @lru_cache
    def bottom_right(self) -> Coord: ...
