from collections.abc import Iterator
from inspect import signature
from math import pi
from sys import version_info
from typing import ClassVar

from pytest import fixture
from dandy_lib.datatypes.tuples import MixableNamedTuple


class RootClass(MixableNamedTuple):  # type: ignore[misc, valid-type]
    pass


class BaseClass(MixableNamedTuple, RootClass):  # type: ignore[misc, valid-type]
    a: int
    b: int

    foo: str = ""
    bar: str = ""


def test_mixin_tuples() -> None:
    # """

    class TestClass(MixableNamedTuple, BaseClass):  # type: ignore[misc, valid-type]

        b: str  # type: ignore[assignment]
        c: str = "xyz"

    # """

    # TestBaseClass = MixableNamedTuple("TestBaseClass", [("a", int), ("b", int), ("foo", str), ("bar", str)])
    # TestClass = MixableNamedTuple("TestClass", [("b", str), ("c", str)], [TestBaseClass])
    r = RootClass()
    a = BaseClass(1, 2, "1", "2")
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


def test_nonannotated_override() -> None:
    class TestOverride(MixableNamedTuple, BaseClass):  # type: ignore[misc, valid-type]

        b = 3.14  # type: ignore[assignment]
        d: float = pi

    to = TestOverride(1, "1", "2")
    assert to.a == 1
    assert to.b == 3.14
    assert to.d == pi
    assert to.foo == "1"
    assert to.bar == "2"


def test_classvar_override() -> None:
    class TestCVOverride(MixableNamedTuple, BaseClass):  # type: ignore[misc, valid-type]

        b: ClassVar[float] = 3.14  # type: ignore[assignment, misc]
        d: float = pi

    to = TestCVOverride(1, "1", "2")
    assert to.a == 1
    assert to.b == 3.14
    assert to.d == pi
    assert to.foo == "1"
    assert to.bar == "2"
