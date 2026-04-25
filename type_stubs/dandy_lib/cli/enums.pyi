import abc
import enum
from argparse import Action
from curses import meta as meta
from typing import Any, Callable, Protocol, _ProtocolMeta

class ChoiceEnumMeta(enum.EnumMeta, _ProtocolMeta): ...
class _EnumMixinProtocol(Protocol): ...

class _CallableEnumMixinProtocol(_EnumMixinProtocol, metaclass=abc.ABCMeta):
    value: Callable[..., Any]

class ChoiceEnumMixin(_EnumMixinProtocol, metaclass=abc.ABCMeta):
    @classmethod
    def choices(cls) -> list[str]: ...

class CallableChoiceEnumMixin(
    ChoiceEnumMixin, _CallableEnumMixinProtocol, metaclass=abc.ABCMeta
):
    def __call__(self, *args, **kwargs): ...

class EnumAction(Action):
    enum_choices: type[ChoiceEnumMixin] | None
    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        nargs: str | int | None = None,
        const: Any = None,
        default: Any = None,
        type: type[ChoiceEnumMixin] | Callable[..., Any] | None = None,
        choices: type[ChoiceEnumMixin] | None = None,
        required: bool = False,
        metavar: str | None = None,
    ) -> None: ...
    def __call__(
        self, parser, namespace, values, option_string=None
    ) -> None: ...
