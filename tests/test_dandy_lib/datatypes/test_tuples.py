from collections import namedtuple
from collections.abc import Iterator
from inspect import signature
from math import pi
from re import A
from sys import version_info
from typing import Any, ClassVar, NamedTuple

from pytest import Subtests, approx, fixture
from dandy_lib.datatypes.tuples import MixableNamedTuple


class RootClass(MixableNamedTuple):  # type: ignore[misc, valid-type]
    pass


class BaseClass(MixableNamedTuple, RootClass):  # type: ignore[misc, valid-type]
    a: int
    b: int

    foo: str = ""
    bar: str = ""


def test_mixin_tuples(subtests: Subtests) -> None:
    # """

    class TestClass(MixableNamedTuple, BaseClass):  # type: ignore[misc, valid-type]

        b: str  # type: ignore[assignment]
        c: str = "xyz"

    # """

    # TestBaseClass = MixableNamedTuple("TestBaseClass", [("a", int), ("b", int), ("foo", str), ("bar", str)])
    # TestClass = MixableNamedTuple("TestClass", [("b", str), ("c", str)], [TestBaseClass])
    r = RootClass()
    with subtests.test("Base class"):
        a = BaseClass(1, 2, "1", "2")

        assert a.a == 1
        assert a.b == 2
        assert a.foo == "1"
        assert a.bar == "2"

    with subtests.test("Test inherited/mixed in"):
        b = TestClass(
            1,
            "2",
            "3",
            "abc",
        )
        c = TestClass(5, 13, "foo", "bar", "c")

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

    with subtests.test("Test Function call style"):

        FnClass: type[tuple] = MixableNamedTuple(
            "FnClass", [("c", float), ("d", float)], [BaseClass]
        )
        d = FnClass(1, 2, "a", "b", 3.5, 4.6)  # type: ignore[arg-type, call-arg]
        assert d.a == 1  # type: ignore[attr-defined]
        assert d.b == 2  # type: ignore[attr-defined]
        assert d.c == 3.5  # type: ignore[attr-defined]
        assert d.d == 4.6  # type: ignore[attr-defined]
        assert d.foo == "a"  # type: ignore[attr-defined]
        assert d.bar == "b"  # type: ignore[attr-defined]


def test_non_annotated_override() -> None:
    class TestOverride(MixableNamedTuple, BaseClass):  # type: ignore[misc, valid-type]

        b = 3.14  # type: ignore[assignment]
        d: float = pi

    to = TestOverride(1, "1", "2")
    assert to.a == 1
    assert to.b == 3.14  # type: ignore[has-type]
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


def test_methods(subtests: Subtests) -> None:
    class HasMethod(MixableNamedTuple):  # type: ignore[misc, valid-type]
        a: int
        b: str

        def foo(self) -> str:
            return f"{self.a} - {self.b}"

        def bar(self, baz: int) -> int:
            return baz * self.a

        # Any, because other things below will override with non-strings
        def boop(self) -> Any:
            return self.a * self.b

    with subtests.test("Basic, not inherited"):
        hm = HasMethod(2, "two")
        assert hm.foo() == "2 - two"
        assert hm.bar(3) == 6
        assert hm.boop() == "twotwo"

    with subtests.test("Inherits only from MixableNamedTuple"):

        class MethodInherit(MixableNamedTuple, HasMethod):  # type: ignore[misc, valid-type]
            d: float = 3.3333

        mi = MethodInherit(3, "four")
        assert mi.foo() == "3 - four"
        assert mi.bar(3) == 9

    with subtests.test("Inherits from non-mixable namedtuple"):

        class NTClass(NamedTuple):
            a: int
            b: float

            def meep(self) -> float:
                return self.a * self.b

        class NTInherit(MixableNamedTuple, NTClass):  # type: ignore[misc, valid-type]
            c: str = "morp"

        nti = NTInherit(3, 2.2)
        assert nti.c == "morp"
        assert approx(6.6) == nti.meep()

    # Disabling til this fxnality is built, if it's even possible
    """with subtests.test("Inherits from non-namedtuple tuple subclass"):

        class SimpleClass(tuple):
            def meep(self) -> str:
                val: float = 1.0
                leftover: list[str] = []
                for sv in self:
                    try:
                        val *= sv
                    except TypeError:
                        leftover.append(str(sv))
                return f"{val} - {';'.join(leftover)}"

        class SimpleInherit(MixableNamedTuple, SimpleClass):
            a: int = 3
            b: float = 2.5
            c: str = "boop"
            d: None = None

        si = SimpleInherit()
        assert si.meep() == "7.5 - boop;None"

    with subtests.test("Inherits from class inheriting from object"):

            class SimpleClass:
                def meep(self) -> str:
                    val: float = 1.0
                    leftover: list[str] = []
                    for sv in self:
                        try:
                            val *= sv
                        except TypeError:
                            leftover.append(str(sv))
                    return f"{val} - {';'.join(leftover)}"

            class SimpleInherit(MixableNamedTuple, SimpleClass):
                a: int = 3
                b: float = 2.5
                c: str = "boop"
                d: None = None

            si = SimpleInherit()
            assert si.meep() == "7.5 - boop;None"
    """
