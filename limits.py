# -*- coding: utf-8 -*-
# DOCUMENT
"""DOCSTRING"""

from numpy import array

class KeithLims:
    # DOCUMENT
    pass


class TempLims:
    # DOCUMENT
    pass


class MagLims():
    """Contains instrument parameter limits for the AMI 430"""
    # TODO: Fix coil_const and its implications.
    # 1 T = 10 kG
    # coil const in {field_unit}/A
    coil_const = array([30/26.3, 3/26.3, 1])
    field = {0: 30,
             1: 3,
             2: 26.3}
    field_default = 5 * coil_const
    rate = {
        'seconds': {
            # Values are:
            # 0: (1.901e-6, 11.407),
            # 1: (1.901e-7, 1.1407)
            0: (1.0e-4/60*coil_const[0], 10*coil_const[0]),
            1: (1.0e-4/60*coil_const[1], 10*coil_const[1]),
            2: (1.0e-4/60, 10)
            },
        'minutes': {
            # Values are:
            # 0: (1.1407e-4, 684),
            # 1: (1.1407e-5, 68.4)
            0: (1.0e-4*coil_const[0], 600*coil_const[0]),
            1: (1.0e-4*coil_const[1], 600*coil_const[1]),
            2: (1.0e-4, 600)}
            }
    rate_default = 0.1*coil_const
    # TODO: Get COM address limits
    # HACK: addr limits are currently (1, 10) just to have something.
    addr = range(10, 0, -1)
    addr_default = 2
    volt = (0.001, 6)
    volt_default = 2
    curr = (0, 26.3)
    curr_default = 26.3
    seg = 10
    seg_default = 1
