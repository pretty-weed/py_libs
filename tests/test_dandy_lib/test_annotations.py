from pytest import raises, Subtests

from dandy_lib import annotations


def test_in_range(subtests: Subtests) -> None:
    for anno in [
        annotations.ValueRange(t1(1), t2(10))
        for t1, t2 in [(int, int), (float, float), (int, float), (float, int)]
    ]:
        for bad_value in [-1, 0, 0.99999999, 10.000001, 110000, float("inf")]:
            with subtests.test(
                "checking bad value fails anno", bad_value=bad_value
            ):
                with raises(ValueError):
                    anno.validate_value(bad_value)
        for good_value in [1, 1.0, 1.5, 5.5, 9, 10, 10.0]:
            with subtests.test(
                "checking good value passes anno", good_value=good_value
            ):
                assert anno.validate_value(good_value) is None
