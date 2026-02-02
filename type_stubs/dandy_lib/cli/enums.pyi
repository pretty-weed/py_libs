import enum
from argparse import Action
from typing import Any, Callable

class ChoiceEnum(enum.Enum):
    @classmethod
    def choices(cls) -> list[str]: ...

class CallableChoiceEnum(ChoiceEnum):
    def __call__(self, *args, **kwargs): ...

class EnumAction(Action):
    enum_choices: type[ChoiceEnum] | None
    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        nargs: str | int | None = None,
        const: Any = None,
        default: Any = None,
        type: type[ChoiceEnum] | Callable | None = None,
        choices: type[ChoiceEnum] | None = None,
        required: bool = False,
        metavar: str | None = None,
    ) -> None: ...
    def __call__(
        self, parser, namespace, values, option_string=None
    ) -> None: ...
