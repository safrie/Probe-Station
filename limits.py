# -*- coding: utf-8 -*-
# DOCUMENT
"""DOCSTRING"""

from numpy import array


class KeithLims:
    # DOCUMENT
    pass


class TempLims():
    """Contains instrument parameter limits and defaults for LakeShore 336."""
    addr = range(1, 32)
    addr_default = 11
    out = (1, 2)
    inpt = range(0, 9)
    # Output modes are 0=Off, 1=Closed loop PID, 2=Zone, 3=Open loop
    outmode = range(0, 4)
    outmode_default = 0
    # Heater modes are 0=Off, 1=Low, 2=Med, 3=High
    heatmode = range(0, 4)
    heatmode_default = 0
    # Rate is in K/min. 0 means "ramp as fast as possible."
    rate = (0.1, 100, 0)
    rate_default = 1
    setpt = (3, 350)
    setpt_default = 4.0


class MagLims():
    """Contains instrument parameter limits for the AMI 430."""
    # TODO: Get COM address limits
    # HACK: addr limits are currently (1, 10) just to have something.
    addr = range(1, 11)
    addr_default = 2
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
    seg = (1, 10)
    seg_default = 1
    field_unit_default = (1, 'Tesla', 'T')
    time_unit_default = (0, 'Seconds', 's')
    volt = (0.001, 6)
    volt_default = 2
    curr = (0, 26.3)
    curr_default = 26.3
