"""
metaclasses.py

Module containing useful general-purpose metaclasses.
"""

from typing import Any

# Utility class

class Wrapper(type):

    def _get_wrapped(self):
        return getattr(self, self._wrapped_name)

    def __getattr__(self, name: str) -> Any:
        print("metaclass getattr")
        return getattr(self._get_wrapped(), name)

    def __getattribute__(self, name: str) -> Any:
        print("metaclass getattribute")
        return getattr(self._get_wrapped(), name)
