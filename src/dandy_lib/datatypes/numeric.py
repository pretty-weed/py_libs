def bounded_int_factory(min_val, max_val):
    foo = 3
    here_min, here_max = min_val, max_val

    class BoundedInt(int):
        bar = foo
        min_val = here_min
        max_val = here_max

        def __new__(cls, in_val=0):
            if not cls.min_val <= in_val <= cls.max_val:
                raise ValueError(
                    f"Value {in_val} is not in range {cls.min_val}, {cls.max_val}"
                )
            return super().__new__(cls)

    return BoundedInt


class NonNegInt(int):
    @classmethod
    def __new__(cls, val):
        if val < 0:
            raise ValueError("Negative values not allowed")
        super().__new__(val)
