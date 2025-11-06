from argparse import Action, ArgumentParser
from pathlib import Path, PurePath
from typing import Callable

from . import parser_types, parser_actions


type CFAType = type[parser_actions.ConditionalFailingAction]


class FileExistsError(Exception):
    pass


def add_output_force_overwrite_to_parser(
    parser: ArgumentParser,
    num_files: int | str | None = None,
    path_dest: str = "output",
    overwrite_flags: list[str] = ["--force_overwrite"],
    overwrite_dest: str = "force_overwrite",
    arg_type: Callable = Path,
    exists_exception: type[Exception] = FileExistsError,
    action_base: CFAType = parser_actions.ConditionalFailingAction,
) -> tuple[Action, Action, CFAType]:

    class OutputAction(action_base):
        EXCEPTIONS_TO_CATCH = (exists_exception,)
        FORCE_DEST = overwrite_dest
        FORCE_FLAG = overwrite_flags[0]
        FORCE_FLAGS = frozenset(overwrite_flags)

        def _do_check(
            self,
            parser,
            namespace,
            value,
            result: PurePath,
            option_string: str = None,
        ) -> None:
            if result.exists():
                raise exists_exception(
                    f"{value} exists, use {overwrite_flags[0]} to force overwrite"
                )

        def _get_val(
            self, parser, namespace, value, option_string=None
        ) -> PurePath:
            return arg_type(value)

    overwrite_act = parser.add_argument(
        *overwrite_flags, dest=overwrite_dest, action="store_true"
    )
    output_act = parser.add_argument(
        path_dest, type=arg_type, nargs=num_files, action=OutputAction
    )

    return overwrite_act, output_act, OutputAction
