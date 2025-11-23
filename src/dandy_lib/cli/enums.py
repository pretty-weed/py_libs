"""
Use enums as choices or subparsers in parsers
"""

from argparse import Action
import enum

from typing import Any, Callable


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
        nargs: str | int,
        const: Any = None,
        default: Any = None,
        type: Callable | None = None,
        choices: list[str] | None = None,
        required: bool = False,
        metavar: str | None = None,
    ):
        if choices and (type is not None) and choices != type:
            raise TypeError(
                "If choices and type are both provided, they must be the same"
            )
        if choices:
            self.enum_choices = choices
        elif type is not None:
            self.enum_choices = choices
        else:
            self.enum_choices = None

        if self.enum_choices is not None:
            choices = self.enum_choices.choices()
            # type = self.enum_choices.type_me

        def type(inval):
            try:
                self.enum_choices[inval]
            except KeyError as exc:
                raise ValueError(
                    f"Invalid value for {self.metavar}: {inval}"
                ) from exc
            return str(inval)

        print(f"choices: {choices}")
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.enum_choices[values[0]])
