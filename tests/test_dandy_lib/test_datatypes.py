import string
import sys
import random
import unittest

import dandy_lib.datatypes


class TestStaticDict(unittest.TestCase):

    _num_test_dicts = 10
    _random_dict_size = 10
    _random_dict_string_size = (1, 15)

    @classmethod
    def _get_random_val(cls, int_ratio=0.2, string_size=None):

        if random.random() <= int_ratio:
            return random.randint(0, sys.maxsize)
        else:
            # set up some vars, if randint or something ends up being
            # a bottleneck, could pre-cache this per-run or something.
            if string_size is None:
                string_size = cls._random_dict_string_size
            choices = string.ascii_uppercase + string.digits
            string_len = random.randint(*string_size)

            return "".join(random.choices(choices, k=string_len))

        raise AssertionError("This point should never be hit")

    @classmethod
    def _get_random_dict(cls, size=None):
        if size is None:
            size = cls._random_dict_size

        out_dict = dict(
            [
                (cls._get_random_val(), cls._get_random_val())
                for _ in range(size)
            ]
        )
        return out_dict

    @classmethod
    def setup_class(cls):
        cls.test_dicts = []

        for _ in range(cls._num_test_dicts):
            vanilla_dict = cls._get_random_dict(size=cls._random_dict_size)
            static_dict = dandy_lib.datatypes.StaticDict(vanilla_dict)

            cls.test_dicts.append((vanilla_dict, static_dict))

    def test_init(self):

        test_dict = {"a": 1, 2: "b"}

        try:
            dandy_lib.datatypes.StaticDict(test_dict)
        except Exception as exc:
            msg = "dict-provided StaticDict init failed with exception: {0}"
            msg += "\n{1}"
            msg = msg.format(type(exc).__name__, str(exc))
            self.fail(msg)

    def test_dict_equality(self):

        for vanilla, static in self.test_dicts:
            self.assertTrue(vanilla == static)

    def test_reassignment(self):
        for _v, test_dict in self.test_dicts:
            for key in test_dict:
                with self.assertRaises(TypeError):
                    test_dict[key] = None

    def test_add(self):

        # TODO
        pass

    def test_remove(self):

        for _v, test_dict in self.test_dicts:
            for key in test_dict:
                with self.assertRaises(TypeError):
                    del test_dict[key]
