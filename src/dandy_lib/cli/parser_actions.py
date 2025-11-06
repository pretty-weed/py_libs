from argparse import ArgumentParser, Action

from typing import Any


class ForceableFailingAction(Action):
    EXCEPTIONS_TO_CATCH = (NotImplementedError,)
    FORCE_DEST = "force"
    FORCE_FLAG = "--force"

    _force_parsers = {}

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if self.FORCE_FLAG not in self._force_parsers:
            force_parser = ArgumentParser()
            force_parser.add_argument(
                self.FORCE_FLAG, dest=self.FORCE_DEST, action="store_true"
            )
            self.__class__._force_parsers[self.FORCE_FLAG] = force_parser

        parsed, _unparsed = self._force_parsers[
            self.FORCE_FLAG
        ].parse_known_args()
        self.force = getattr(parsed, self.FORCE_DEST)
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def _get_val(self, parser, namespace, values, option_string=None) -> Any:
        raise NotImplementedError()

    def _do_check(
        self, parser, namespace, values, result, option_string=None
    ) -> None:
        raise NotImplementedError()

    def __call__(self, parser, namespace, values, option_string=None):

        print("%r %r %r" % (namespace, values, option_string))
        results = [
            self._get_val(parser, namespace, value, option_string)
            for value in values
        ]
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

        setattr(namespace, self.dest, results)


"""
####### Example

from argparse import ArgumentParser
import pathlib

class FileExistsError(Exception):
    pass

class TestAction(ForceableFailingAction):
    EXCEPTIONS_TO_CATCH = (FileExistsError, )

    def _get_val(self, parser, namespace, value, option_string=None) -> pathlib.PurePath:
        return pathlib.Path(value)

    def _do_check(self, parser, namespace, value, result: pathlib.PurePath, option_string=None) -> None:
        if result.exists():
            raise FileExistsError(f"{value} exists")


def testme():
    parser = ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("check_files", action=TestAction, nargs="+", type=pathlib.Path)
    print(" ##### PARSER CREATED ##### ")

    parsed = parser.parse_args()

    print(parsed)

if __name__ == "__main__":
    testme()"""
