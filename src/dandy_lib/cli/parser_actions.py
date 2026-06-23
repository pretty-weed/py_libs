from argparse import Action, ArgumentError, ArgumentParser, Namespace
from inspect import isclass, signature
from os import name
from typing import (
    Any,
    Callable,
    Collection,
    Literal,
    NamedTuple,
    Protocol,
    Self,
    Sequence,
    Type,
    TypeVar,
    TypeAlias,
    cast,
)
from webbrowser import get


class NamedTupleMetaProt(Protocol):
    _fields: tuple[str, ...]

    def _make(self, iterable: Any) -> Any: ...


class Named(Protocol):
    name: str


Number: TypeAlias = int | float
IntfinityLiteral = int | float
_T = TypeVar("_T", bound=tuple)


class TupleHintedNamespace(Namespace):
    @classmethod
    def for_classes(
        cls: type[Self], **fields: type[NamedTupleMetaProt]
    ) -> type[Self]:
        """Dynamically builds a Namespace subclass with proper type annotations.

        Usage: TupleHintedNamespace.for_classes(point=Point, user=User)
        """
        # Build list annotations, e.g., {'point': list[Point], 'user': list[User]}
        annotations = {name: list for name, tuple_type in fields.items()}

        # Also pre-populate defaults as empty lists so Pyright knows they exist
        # class_attributes = {"__annotations__": annotations}
        # Explicitly hint the dictionary type to prevent restrictive auto-inference
        class_attributes: dict[str, Any] = {"__annotations__": annotations}
        for name in fields:
            class_attributes[name] = []

        # Use cast to assure Pyright that the generated class fits type[Self]

        return cast(
            type[Self], type(f"Dynamic{cls.__name__}", (cls,), class_attributes)
        )


class Range(NamedTuple):
    start: int
    end: IntfinityLiteral
    arg: str | int
    inclusive: bool = True

    def is_range(self) -> bool:
        return self.start != self.end

    @classmethod
    def new(
        cls, start: int, end: None | IntfinityLiteral = None, inclusive=True
    ):
        """
        Factory to allow for single value ranges
        """
        if end is None:
            arg: int | str = start
            match start:
                case "?":
                    start = 0
                    end = 1
                case "*":
                    start = 0
                    end = float("inf")
                case "+":
                    start = 1
                    end = float("inf")
                case int() | str():
                    end = start
                    arg = "+"
                case _:
                    raise ValueError(f"Invalid value for a range: {start}")
            assert end is not None

        else:
            arg = "+"
        return cls(start, end, arg, inclusive=inclusive)

    def __contains__(self, other: Number, inclusive=True) -> bool:  # type: ignore[override]
        if inclusive:
            return self.start <= other <= self.end
        return self.start < other < self.end


class NargsRangeAction(Action):
    """
    Base action to handle a specific range of nargs (e.g. 3 <= num of args <=5)

    As `Action`'s `__call__()` raises exceptions, this class' `__call__()` does
    not call `__super__()`. As such, this should be used as a base class and
    not a mixin.
    """

    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        append_type: Callable = list,
        **kwargs,
    ):
        if nargs is not None:
            try:
                self.n_range = Range.new(*nargs)
            except TypeError:
                self.n_range = Range.new(nargs)
            nargs = self.n_range.arg
        else:
            self.n_range = None
        self.append_type: Callable[..., Any] = append_type
        super().__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        values = self._validate_values(values, option_string=option_string)
        # If the above has not failed...
        setattr(namespace, self.dest, values)

    def _validate_values(
        self, values: Sequence[Any], option_string=None
    ) -> Any:

        match values:
            case list() | tuple():
                pass
            case _:
                values = [values]
        if self.n_range is not None and not len(values) in self.n_range:
            help_name = (
                option_string
                if option_string
                else (self.metavar if self.metavar else self.dest)
            )
            expected_msg = f"Expected {self.n_range.start}-{self.n_range.end} ({'not' if not self.n_range.inclusive else ''} inclusive)"
            raise ArgumentError(
                self,
                f"Incorrect number of values for {help_name}: {expected_msg}, got {len(values)} ({values}).",
            )
        if self.type is not None:
            # MyPy thinks that self.type is a string for some reason
            return self._handle_append_type([self.type(v) for v in values])  # type: ignore[operator]
        return self._handle_append_type(values)

    def _handle_append_type(self, values: list[Any] | tuple[Any]) -> Collection:
        # This doesn't handle all edge cases where
        if (
            isclass(self.append_type)
            and issubclass(self.append_type, Collection)
        ) or (
            not isclass(self.append_type)
            and issubclass(
                signature(self.append_type).return_annotation, Collection
            )
        ):
            return self.append_type(values)  # type: ignore[call-arg]
        else:
            return self.append_type(*values)


class NargsRangeAppendAction(NargsRangeAction):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        values = self._validate_values(values, option_string=option_string)
        items: list[Any] = getattr(namespace, self.dest) or []
        items.append(values)
        setattr(namespace, self.dest, items)


class ConditionalFailingAction(Action):
    EXCEPTIONS_TO_CATCH: tuple[type[Exception], ...] = (NotImplementedError,)
    FORCE_DEST = "force"
    FORCE_FLAG = "--force"
    FORCE_FLAGS = frozenset(["--force"])

    _force_parsers: dict[str, ArgumentParser] = {}

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)
        if self.FORCE_FLAG not in self.FORCE_FLAGS:
            # could handle this in a metaclass  but meh
            raise ValueError(
                f"the class {self.__class__} is misconfigured, as the force flag is not in all possible force flags"
            )
        if self.FORCE_FLAG not in self._force_parsers:
            force_parser = ArgumentParser()
            force_parser.add_argument(
                *self.FORCE_FLAGS, dest=self.FORCE_DEST, action="store_true"
            )
            self.__class__._force_parsers[self.FORCE_FLAG] = force_parser

        parsed, _unparsed = self._force_parsers[
            self.FORCE_FLAG
        ].parse_known_args()
        self.force = getattr(parsed, self.FORCE_DEST)

    def _get_val(self, parser, namespace, values, option_string=None) -> Any:
        raise NotImplementedError()

    def _do_check(
        self, parser, namespace, values, result, option_string=None
    ) -> None:
        raise NotImplementedError()

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        single_result: bool | None = None
        try:
            results = [
                self._get_val(parser, namespace, value, option_string)
                for value in values
            ]
        except TypeError:
            # single item
            results = [self._get_val(parser, namespace, values, option_string)]
            values = [values]
            single_result = True
        else:
            single_result = False

        for result, value in zip(results, values):
            try:
                self._do_check(
                    parser,
                    namespace,
                    value,
                    result,
                    option_string=option_string,
                )
            except self.EXCEPTIONS_TO_CATCH as exc:
                if not self.force:
                    raise exc
                print("forced")

        setattr(namespace, self.dest, results[0] if single_result else results)


NT_Hint: TypeAlias = Callable[..., tuple[Any, ...]]


class NamedTupleAction(Action):
    NT_CLASS: NT_Hint | None = None

    def __init__(self, *args, **kwargs) -> None:
        if not self.NT_CLASS:
            raise ValueError(
                "Do not use AppendNamedTuple directly. Use AppendNamedTuple.for_class(YourTuple)"
            )

        # Force argparse to use the subclass-level defaults if not explicitly overwritten
        kwargs.setdefault("nargs", self.nargs)
        kwargs.setdefault("metavar", self.metavar)
        super().__init__(*args, **kwargs)

    @classmethod
    def for_tuple(cls: Type[Self], tuple_type: Type[NamedTuple]) -> Type[Self]:

        return type(  # type: ignore[override]
            f"Append{tuple_type.__name__}Action",
            (cls,),
            {
                "NT_CLASS": tuple_type,
                "nargs": len(tuple_type._fields),
                "metavar": tuple_type._fields,
            },
        )

    def _cast_item(self, values: Sequence[Any]) -> tuple[Any, ...]:
        if self.NT_CLASS is None:
            raise RuntimeError("NT_CLASS is not initialized. Use .for_class()")

        annotations: dict[str, Any] = getattr(
            self.NT_CLASS, "__annotations__", {}
        )
        fields: tuple[str, ...] = getattr(self.NT_CLASS, "_fields", ())
        converted = []
        for field, value in zip(fields, values):
            field_type = annotations.get(field, str)
            try:
                converted.append(field_type(value))
            except (ValueError, TypeError) as e:
                raise ArgumentError(
                    self, f"Invalid arguments for {self.NT_CLASS.__name__}: {e}"
                )

        return self.NT_CLASS(*converted)

    # see override note above `values`
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        # Always have seq values because always nave nargs
        values: Sequence[Any],
        option_string=str | None,
    ):

        if self.NT_CLASS is None:
            raise RuntimeError("NT_CLASS is not initialized. Use .for_class()")

        items = getattr(namespace, self.dest) or []
        setattr(namespace, self.dest, self._cast_item(values))


class AppendNamedTupleAction(NamedTupleAction):

    def __call__(self, parser, namespace, values: Sequence[Any], option_string=None):  # type: ignore[override]
        if self.NT_CLASS is None:
            raise RuntimeError("NT_CLASS is not initialized. Use .for_class()")

        sequence_values = [values] if isinstance(values, str) else list(values)

        items = getattr(namespace, self.dest) or []
        items.append(self._cast_item(sequence_values))
        setattr(namespace, self.dest, items)
