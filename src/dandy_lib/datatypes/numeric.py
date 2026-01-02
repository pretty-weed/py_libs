from typing import Annotated, TypeAlias

from annotated_types import Ge


NonNegInt: TypeAlias = Annotated[int, Ge(0)]
NonNegFloat: TypeAlias = Annotated[float, Ge(0.0)]
