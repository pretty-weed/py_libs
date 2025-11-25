"""
Use enums as choices or subparsers in parsers
"""

import enum
from argparse import Action
from inspect import isclass
from typing import Any
from typing import Callable, Optional, Type


class ChoiceEnum(enum.Enum):
    def __str__(self):
        return self.name

    @classmethod
    def choices(cls) -> list[str]:
        return cls._member_names_


class CallableChoiceEnum(ChoiceEnum):

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)


class EnumAction(Action):

    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        nargs: Optional[str | int] = None,
        const: Any = None,
        default: Any = None,
        # This redef is due to the interface of argparse
        type: Optional[Type[ChoiceEnum] | Callable] = None,  # type: ignore[no-redef]
        choices: Optional[Type[ChoiceEnum]] = None,
        required: bool = False,
        metavar: str | None = None,
    ):
        self.enum_choices: Type[ChoiceEnum] | None = None

        match (choices, type):
            case (c, t) if c != None and t != None and c != t:
                raise TypeError(
                    "If choices and type are both provided, they must be the same"
                )
            case (c, t) if issubclass(c, ChoiceEnum) and (t is None or t == c):  # type: ignore[arg-type]
                self.enum_choices = c
                type = None
            case (c, t) if (
                c is None and isclass(t) and issubclass(t, ChoiceEnum)  # type: ignore[assignment]
            ):
                self.enum_choices = t
                type = None

        def type_fn(inval):
            try:
                self.enum_choices[inval]
            except KeyError as exc:
                raise ValueError(
                    f"Invalid value for {self.metavar}: {inval}"
                ) from exc
            return str(inval)

        if self.enum_choices is not None:
            type = type_fn
            choices = self.enum_choices.choices()  # type: ignore[assignment]

        print(f"choices: {choices}")
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            # The action updates the choices here.
            choices=choices,  # type: ignore[arg-type]
            required=required,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.enum_choices[values[0]])
