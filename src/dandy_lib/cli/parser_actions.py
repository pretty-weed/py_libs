from argparse import ArgumentParser, Action

from typing import Any


class ConditionalFailingAction(Action):
    EXCEPTIONS_TO_CATCH = (NotImplementedError,)
    FORCE_DEST = "force"
    FORCE_FLAG = "--force"
    FORCE_FLAGS = frozenset(["--force"])

    _force_parsers = {}

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

    def __call__(self, parser, namespace, values, option_string=None):
        single_result: bool = None
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
