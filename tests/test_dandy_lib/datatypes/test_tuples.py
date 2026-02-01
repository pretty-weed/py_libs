from inspect import signature
from sys import version_info

from pytest import mark

if version_info.major > 3 or (
    version_info.major == 3 and version_info.minor >= 14
):
    from dandy_lib.datatypes.tuples import MixableNamedTuple

    skip_lte313 = False
else:
    skip_lte313 = True


@mark.skipif(skip_lte313, reason="Pre 3.14 Python")
def test_mixin_tuples() -> None:
    # """

    class TestRootClass(MixableNamedTuple):  # type: ignore[misc, valid-type]
        pass

    class TestBaseClass(MixableNamedTuple, TestRootClass):  # type: ignore[misc, valid-type]
        a: int
        b: int

        foo: str = ""
        bar: str = ""

    class TestClass(MixableNamedTuple, TestBaseClass):  # type: ignore[misc, valid-type]

        b: str  # type: ignore[assignment]
        c: str = "xyz"

    # """

    # TestBaseClass = MixableNamedTuple("TestBaseClass", [("a", int), ("b", int), ("foo", str), ("bar", str)])
    # TestClass = MixableNamedTuple("TestClass", [("b", str), ("c", str)], [TestBaseClass])
    r = TestRootClass()
    a = TestBaseClass(1, 2, "1", "2")
    b = TestClass(
        1,
        "2",
        "3",
        "abc",
    )
    c = TestClass(5, 13, "foo", "bar", "c")

    assert a.a == 1
    assert a.b == 2
    assert a.foo == "1"
    assert a.bar == "2"

    assert b.a == 1
    assert b.b == "2"
    assert b.foo == "3"
    assert b.bar == "abc"
    assert b.c == "xyz"

    assert c.a == 5
    assert c.b == 13
    assert c.foo == "foo"
    assert c.bar == "bar"
    assert c.c == "c"
