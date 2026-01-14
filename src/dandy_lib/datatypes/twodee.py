from functools import lru_cache
from typing import NamedTuple

from .numeric import NonNegInt, NonNegFloat


class Size(NamedTuple):
    width: NonNegInt | NonNegFloat
    height: NonNegInt | NonNegFloat

    @classmethod
    def factory(cls, *in_vals: NonNegInt | NonNegFloat):
        if len(in_vals) == 1:
            return cls(in_vals[0], in_vals[0])
        return cls(*in_vals)


type Number = int | float


class Vector(NamedTuple):
    x: Number
    y: Number


class Coord(Vector):
    pass


class Rect(NamedTuple):
    position: Coord
    size: Size

    def __getattr__(self, name: str) -> Number:
        """
        Automagically get child element attributes (e.g. width, x)
        so frickin lazy
        """
        for element in self:
            try:
                return getattr(element, name)
            except AttributeError:
                pass

        raise AttributeError(f"'{self}' object has no attribute '{name}'.")

    @property
    @lru_cache
    def top(self) -> Number:
        return self.y

    @property
    @lru_cache
    def bottom(self) -> Number:
        return self.y + self.height

    @property
    @lru_cache
    def left(self) -> Number:
        return self.y

    @property
    @lru_cache
    def right(self) -> Number:
        return self.y + self.width

    @property
    @lru_cache
    def top_left(self) -> Coord:
        return Coord(self.x, self.y)

    @property
    @lru_cache
    def bottom_left(self) -> Coord:
        return Coord(self.bottom, self.right)

    @property
    @lru_cache
    def top_right(self) -> Coord:
        return Coord(self.x, self.right)

    @property
    @lru_cache
    def bottom_right(self) -> Coord:
        return Coord(self.bottom, self.right)
