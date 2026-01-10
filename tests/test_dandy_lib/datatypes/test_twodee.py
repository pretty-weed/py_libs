from pytest import RaisesExc

import dandy_lib.datatypes.twodee as twodee


def test_size_init(subtests):
    good_values = {float: (4.3, 5.0), int: (2, 5)}
    for data_type, values in good_values.items():
        with subtests.test(msg="init good", data_type=data_type):
            size = twodee.Size(*values)
            assert size.width == values[0]
            assert size.height == values[1]


def test_coord_init(subtests):
    good_values = {float: (4.3, 5.0), int: (2, 5)}
    for data_type, values in good_values.items():
        with subtests.test(msg="init good", data_type=data_type):
            coord = twodee.Coord(*values)
            assert coord.x == values[0]
            assert coord.y == values[1]
