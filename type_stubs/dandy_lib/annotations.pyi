from typing import NamedTuple

class ValueRange(NamedTuple):
    min: float | int
    max: float | int
    def validate_value(self, x) -> None: ...

class DivisibleBy(NamedTuple):
    divisor: float | int
    def validate_value(self, val: float | int): ...
