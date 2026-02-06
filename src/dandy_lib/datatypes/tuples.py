"""
Ain't exactly great practice, but kinda fuckin around with this.
"""

from collections import namedtuple
from collections.abc import Iterable
from copy import copy, deepcopy
from enum import IntEnum
from inspect import _ParameterKind, Parameter, getmro
from typing import (  # type: ignore[attr-defined]
    Any,
    Callable,
    ClassVar,
    NamedTuple,
    _NamedTuple,
    NamedTupleMeta,
    Self,
    get_origin,
)

# annotation lib added 3.14
try:
    # Ignore not found, since supporting 3.13
    import annotationlib  # type: ignore[import-not-found]
except ImportError:

    def get_annotate_from_class_namespace(obj: dict[str, Any]) -> Any:
        try:
            return obj["__annotate__"]
        except KeyError:
            return obj.get("__annotate_func__", None)

    def call_annotate_function(
        annotate: Callable[[int], dict[str, type]], format
    ) -> dict[str, type]:
        # 2 is value with fake globals
        return annotate(2)

    class Format(IntEnum):
        VALUE = 1
        VALUE_WITH_FAKE_GLOBALS = 2
        FORWARDREF = 3
        STRING = 4

else:
    from annotationlib import (  # type: ignore[no-redef, assignment]
        call_annotate_function,
        get_annotate_from_class_namespace,
        Format,
    )

# Only needed for annotationlib related stuff
try:
    from typing import _make_eager_annotate  # type: ignore[attr-defined]
except ImportError:

    def _make_eager_annotate(
        types: dict[str, type],
    ) -> Callable[[int | Format], dict[str, Any]]:
        # TODO maybe check types like they do in annotationlib _type_check
        new_types = dict((k, v) for k, v in types.items())

        def annotate(format: int | Format) -> dict[str, Any]:
            """
            Format matched from annotationlib Format IntEnum:
            class Format(IntEnum):
                VALUE = 1
                VALUE_WITH_FAKE_GLOBALS = 2
                FORWARDREF = 3
                STRING = 4
            """

            match format:
                case 1 | 3:
                    return new_types
                case 4:
                    return dict((k, str(v)) for k, v in new_types.items())
                case _:
                    raise NotImplementedError(format)

        return annotate


ANNOTATIONS = "__annotations__"
ANNOTATE_FUNC = "__annotate_func__"


def _get_params_from_bases(bases: list[type] | None) -> dict[str, Parameter]:
    params: dict[str, Parameter] = {}
    if bases is None:
        return params
    for base in bases:
        if base in (tuple, NamedTuple, MixableNamedTuple):
            continue
        if tuple not in getmro(base):
            continue
        # Ignore is for type checker thinking base.__annotate__ is None
        try:
            annotations: dict[str, type] = base.__annotate__(Format.VALUE)  # type: ignore[arg-type, attr-defined, misc]
        except AttributeError as exc:
            # python3.13 and earlier will hit this
            annotations = copy(base.__annotations__)
        for pname, ptype in annotations.items():  # type: ignore[misc]
            if pname in params:
                continue
            if (
                hasattr(base, "_field_defaults")
                and pname in base._field_defaults
            ):
                params[pname] = Parameter(
                    pname,
                    _ParameterKind.POSITIONAL_OR_KEYWORD,
                    default=base._field_defaults[pname],
                    annotation=ptype,
                )

            else:
                params[pname] = Parameter(
                    pname,
                    _ParameterKind.POSITIONAL_OR_KEYWORD,
                    annotation=ptype,
                )

    return params


def _get_defaults(
    ns: dict[str, Any], base_namespace: dict[str, Parameter]
) -> dict[str, Any]:
    return dict(
        (k, p.default)
        for k, p in base_namespace.items()
        if p.default is not p.empty
    ) | dict((k, ns[k]) for k in base_namespace if k in ns)


class MixinableNamedTupleMeta(NamedTupleMeta):
    def __new__(cls, typename, bases: list[type], ns: dict[str, Any]) -> Self:
        """
        Add fields from inherited named tuples to the new one
        """

        bases = [
            base
            for base in bases
            if base is not MixableNamedTupleBase and not issubclass(base, tuple)
        ]
        if _NamedTuple not in bases:
            bases.append(_NamedTuple)

        base_namespace = _get_params_from_bases(ns["__orig_bases__"])
        original_annotate: None | Callable[[Format], dict[str, Any]] = None

        defaults: dict[str, Any] = _get_defaults(ns, base_namespace)

        if ANNOTATIONS in ns:
            types = ns[ANNOTATIONS]
            for pname, ptype in base_namespace.items():
                if pname not in ns[ANNOTATIONS] and pname not in ns:
                    ns[ANNOTATIONS][pname] = ptype
            annotate: Callable[[int | Format], dict[str, Any]] = (
                _make_eager_annotate(types)
            )
        elif (
            original_annotate := get_annotate_from_class_namespace(ns)
        ) is not None:

            types = call_annotate_function(original_annotate, Format.FORWARDREF)
            original_annotate = original_annotate
        elif base_namespace and ANNOTATE_FUNC in ns:
            # capturing where there's no new namedtuple members
            original_annotate = lambda format: {}
            types = original_annotate(Format.VALUE)
        else:
            types = {}
            original_annotate = lambda format: {}
        defaults.update(dict((k, ns[k]) for k in types if k in ns))
        base_annotations: dict[str, type] = dict(
            (k, v.annotation) for k, v in base_namespace.items()
        )
        # Find things that have been removed from the class nt fields
        field_remove = set(
            dk
            for dk in defaults
            if (dk in ns and dk not in types)
            or get_origin(types.get(dk)) is ClassVar
        )
        # Start with base items without defaults
        annotations: dict[str, type] = dict(
            (k, v) for k, v in base_annotations.items() if k not in defaults
        )
        # Add non-default items from this class
        annotations.update(
            dict((k, v) for k, v in types.items() if k not in defaults)
        )
        # Add default items back in from merged bases + ns
        annotations.update(
            dict(
                (k, v)
                for k, v in (base_annotations | types).items()
                if k in defaults and k not in field_remove
            )
        )

        if ANNOTATIONS in ns:
            ns[ANNOTATIONS] = annotations
        elif (
            original_annotate is not None
            and original_annotate(Format.VALUE) != annotations
        ):

            def annotate(
                format: int | Format,
            ) -> dict[str, Any]:
                # TODO: DO if format != annotationlib.Format.STRING: check from typing.py
                return deepcopy(annotations)

            ns[ANNOTATE_FUNC] = annotate
        return super().__new__(cls, typename, bases, ns)


MixableNamedTupleBase: NamedTupleMeta = type.__new__(
    MixinableNamedTupleMeta, "MixableNamedTuple", (), {}
)


def MixableNamedTuple(
    typename: str,
    fields: list[tuple[str, type]] | None = None,
    bases: list[type] | None = None,
    /,
    **kwargs: Any,
) -> type[tuple]:  # type: ignore[valid-type]
    """
    Mixinable named tuple type
    """
    if fields is None:
        fields_dict: dict[str, type] = dict(kwargs.items())
    else:
        fields_dict = dict(fields)
    base_fields = dict(
        (k, v.annotation) for k, v in _get_params_from_bases(bases).items()
    )
    return NamedTuple(typename, (base_fields | fields_dict).items())  # type: ignore[return-value]


def _mixablenamedtuple_mro_entries(bases):
    assert MixableNamedTuple in bases
    return (
        MixableNamedTupleBase,
        _NamedTuple,
    )


MixableNamedTuple.__mro_entries__ = _mixablenamedtuple_mro_entries  # type: ignore[attr-defined]
MixableNamedTuple.__mro__ = (MixableNamedTuple, tuple, object)  # type: ignore[attr-defined]
