
class NonNegInt(int):
    @classmethod
    def __new__(cls, val):
        if val < 0:
            raise ValueError("Negative values not allowed")
        super().__new__(val)
