import unittest

import dandy_lib.testing


class TestCaseParameters(unittest.TestCase):

    def test_creation(self):

        test_inputs = ["1, 2, 3, 4", "1 2 3 4", "1\n2\n3\n4"]
        test_results = [1, 2, 3, 4]

        for input_val, result in zip(test_inputs, test_results):
            dandy_lib.testing.CaseParameters(test_inputs, test_results)
        for input_val, result in zip(test_inputs, test_results):
            dandy_lib.testing.CaseParameters(
                result=result, input_data=input_val
            )
