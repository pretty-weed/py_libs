from typing import Annotated, TypeAlias

from annotated_types import Ge, Le

NonNegInt: TypeAlias = Annotated[int, Ge(0)]
NonNegFloat: TypeAlias = Annotated[float, Ge(0.0)]
NonNegNum: TypeAlias = NonNegInt | NonNegFloat

Infinity: TypeAlias = Annotated[float | int, Ge(float("inf"))]
NegativeInfinity: TypeAlias = Annotated[float | int, Le(-float("inf"))]
