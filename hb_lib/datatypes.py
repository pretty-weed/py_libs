"""
datatypes.py

module containing some general-purpose data types and structures that
are or may be used across projects.
"""

import hb_lib.metaclasses



class StaticDict(dict):
    """
    I think 'static' is the wrong term for what I'm going for here,
    but:

    StaticDict is a dictionary where keys/vals can be added, but
    deletion and reassignment are not supported (so the only valid
    modifying actions are init and add)
    """

    _MSG_ALREADY_ASSIGNED = 'The key {0} has been assigned and StaticDict does not allow reassignment'
    _MSG_NO_DEL = 'Static Dicts do not allow item deletion'

    def __setitem__(self, key, val):
        if key in self:
            raise TypeError(self._MSG_ALREADY_ASSIGNED.format(key))
        super(StaticDict, self).__setitem__(key, val)

    def __delitem__(self, key):
        raise TypeError(self._MSG_NO_DEL)
