from functools import cached_property
from typing import Annotated, Any, NamedTuple, TypeAlias

from annotated_types import Ge
from .numeric import NonNegFloat, NonNegInt


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

    def __getattr__(self, name) -> Number:
        """
        Automagically get child element attributes (e.g. width, x)
        so frickin lazy
        """
        raise_exc: None | AttributeError = None
        for element in self:
            try:
                return getattr(element, name)
            except AttributeError:
                pass

        # Gonna raise an exception
        try:
            return super().__getattr__(name)  # type: ignore
        except AttributeError:
            raise AttributeError(f"{type(self)} has no attribute {name}")

    @cached_property
    def top(self) -> Number:
        return self.y

    @cached_property
    def bottom(self) -> Number:
        return self.y + self.height

    @cached_property
    def left(self) -> Number:
        return self.y

    @cached_property
    def right(self) -> Number:
        return self.y + self.width

    @cached_property
    def top_left(self) -> Coord:
        return Coord(self.x, self.y)

    @cached_property
    def bottom_left(self) -> Coord:
        return Coord(self.bottom, self.right)

    @cached_property
    def top_right(self) -> Coord:
        return Coord(self.x, self.right)

    @cached_property
    def bottom_right(self) -> Coord:
        return Coord(self.bottom, self.right)
