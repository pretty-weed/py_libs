from turtle import heading, width
from .numeric import (
    NonNegFloat as NonNegFloat,
    NonNegInt as NonNegInt,
    NonNegNum as NonNegNum,
)
from functools import lru_cache
from typing import NamedTuple

class Size(NamedTuple):
    width: NonNegNum
    height: NonNegNum
    @classmethod
    def factory(cls, *in_vals: NonNegNum): ...

type Number = int | float

class Vector(NamedTuple):
    x: Number
    y: Number

class Coord(Vector): ...

class Rect(NamedTuple):
    position: Coord
    size: Size
    x: Number
    y: Number
    width: Number
    height: Number

    def __getattr__(self, name: str) -> Number: ...
    @property
    def top(self) -> Number: ...
    @property
    def bottom(self) -> Number: ...
    @property
    def left(self) -> Number: ...
    @property
    def right(self) -> Number: ...
    @property
    def top_left(self) -> Coord: ...
    @property
    def bottom_left(self) -> Coord: ...
    @property
    def top_right(self) -> Coord: ...
    @property
    def bottom_right(self) -> Coord: ...
