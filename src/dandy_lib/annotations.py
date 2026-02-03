from typing import NamedTuple


class ValueRange(NamedTuple):
    min: float | int
    max: float | int

    def validate_value(self, x):
        if not (self.min <= x <= self.max):
            raise ValueError(f"{x} must be in range [{self.min}, {self.max}]")


class DivisibleBy(NamedTuple):
    divisor: float | int

    def validate_value(self, val: float | int):
        if val % self.divisor:
            raise ValueError(f"{val} must be divisible by {self.divisor}")
