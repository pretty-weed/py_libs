from . import parser_actions as parser_actions, parser_types as parser_types
from argparse import Action, ArgumentParser
from typing import Callable, TypeAlias

CFAType: TypeAlias = type[parser_actions.ConditionalFailingAction]

class FileExistsError(Exception): ...

def add_output_force_overwrite_to_parser(
    parser: ArgumentParser,
    num_files: int | str | None = None,
    path_dest: str = "output",
    overwrite_flags: list[str] = ["--force_overwrite"],
    overwrite_dest: str = "force_overwrite",
    arg_type: Callable = ...,
    exists_exception: type[Exception] = ...,
    action_base=...,
) -> tuple[Action, Action, CFAType]: ...
