"""
testing.py

shared conts and code used by the unnecessary testing framework.
You know, because I'm a belt and suspenders and jackhammer gal.
Why is there a jackhammer? maybe I need to be in practice with
using a jackhammer for something, despite the fact that I never
have before? Who knows?

-d
"""

import collections
import unittest

CaseParameters = collections.namedtuple(
    "CaseParameters", ["input_data", "result"]
)


class ParameterizedCase(unittest.TestCase):

    def __init__(self, case_params, method="runTest", run_function=None):
        self._case_params = case_params
        self._run_function = run_function

        super(ParameterizedCase, self).__init__(method)

    def runTest(self):

        if self._run_function is None:
            msg = "this {} has not been set up properly".format(
                self.__class__.__name__
            )
            raise NotImplementedError(msg)

        res = self._run_function(self._case_params.input_data)
        self.assertEqual(res, self._case_params.result)
