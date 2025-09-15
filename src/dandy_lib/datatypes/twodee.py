from dataclasses import dataclass

from .numeric import NonNegInt
@dataclass(unsafe_hash=True)
class Size:
    width: NonNegInt
    height: NonNegInt

    @classmethod
    def factory(cls, *in_vals):
        if len(in_vals) == 1:
            return cls(in_vals[0], in_vals[0])
        return cls(*in_vals)

    def __iter__(self) -> Iterator[int]:
        yield from [self.width, self.height]
