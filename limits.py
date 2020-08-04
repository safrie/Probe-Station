# -*- coding: utf-8 -*-
# DOCUMENT
"""DOCSTRING"""

from numpy import array


class KeithLims:
    """Contains instrument limits and defaults for the Keithley stack."""

    addr = range(1, 32)
    addr_default = 0  # FIXME: Find default address

    unit = ("V", "OHMS", "W", "SIEM")
    unit_default = "V"
    power = ("AVER", "PEAK")
    power_default = "AVER"

    source_range = (2.0e-9, 20.0e-9, 200.0e-9, 2.0e-6, 20.0e-6, 200.0e-6,
                    2.0e-3, 20.0e-3, 100.0e-3)
    source_range_default = 200.0e-6
    source_range_type = ("ON", "OFF")
    source_range_type_default = "OFF"
    meter_rate = (0.01, 60.0)
    meter_rate_default = 5.0
    meter_range = (100.0e-3, 10.0e-3, 1.0, 10.0, 100.0)
    meter_range_default = 100.0
    compliance_volt = (0.1, 105.0)
    compliance_volt_default = 10
    cab = ("ON", "OFF")
    cab_default = "OFF"

    points = range(1, 65537)
    points_default = 10

    # Currents are in Amps
    curr1 = (-105.0e-3, 105.0e-3)
    curr1_default = 1.0e-3
    curr2 = (-105.0e-3, 105.0e-3)
    curr2_default = 1.0e-3
    curr_step = (0.0, 105.0e-3)
    curr_step_default = 1.0e-5
    meas_rate = (0.1, 60)  # This is in PLC
    meas_rate_default = 1
    delay = (1.0e-3, 9999.999)  # This is in seconds
    delay_default = 2.0e-3

    filt = ((0, "MOV"), (1, "REP"))
    filt_default = filt[0]
    filt_window = (0.0, 10.0)
    filt_window_default = 0.0
    filt_count = range(2, 301)
    filt_count_default = 10


class DconLims(KeithLims):
    """DconLims contains limits specific to differential conductance.

    DconLims inherits from KeithLims"""
    curr_delta = (0, 105.0e-3)
    curr_delta_default = 1.0e-6

    def __init__(self):
        super().__init__()
        self.filt = super().filt[1]
        self.curr1_default = -10.0e-6
        self.curr2_default = 10.0e-6
        self.curr_step_default = 1.0e-6


class DeltaLims(KeithLims):
    """DeltaLims contains limits specific to delta measurements.

    DeltaLims inherits from KeithLims."""

    def __init__(self):
        super().__init__()
        self.curr1 = (0, 105.0e-3)
        self.curr1_default = 10.0e-3
        self.curr2 = (-105.0e-3, 0)
        self.curr2_default = 0


class PDeltaLims(KeithLims):
    """PDeltaLims contains limits specific to pulse delta measurements.

    PDeltaLims inherits from KeithLims."""

    width = (50.0e-6, 12.0e-3)
    width_default = 110.0e-6
    low_meas = (1, 2)
    low_meas_default = 2

    def __init__(self):
        super().__init__()
        self.curr1_default = 1.0e-3
        self.curr2_default = 0.0
        self.delay = (16.0e-6, 11.966e-3)
        self.delay_default = 16.0e-6
        self.meas_rate = (5, 999999)  # This is in PLC
        self.meas_rate_default = 5


class PDeltStairLims(PDeltaLims):
    """PDeltStairLims contains limits specific to pulse delta measurements.

    PDeltStairLims inherits from PDeltaLims."""

    sweeps = range(1, 10000)
    sweeps_default = 1

    def __init__(self):
        super().__init__()
        # ???: Can you have a negative curr2?
        # self.curr2 = (0.0, 105.0e-3)
        self.curr2_default = -1.0
        self.meas_rate = (1.0e-3, 999999.999)
        self.meas_rate_default = 0.1


class PDeltLogLims(KeithLims):
    """PDeltLogLims contains limits specific to pulse delta measurements.

    PDeltLogLims inherits from PDeltaLims."""

    sweeps = range(1, 10000)
    sweeps_default = 1

    def __init__(self):
        super().__init__()
        # ???: Do I need to set curr2 bounds for this to avoid negative?
        self.curr2_default = 0
        self.meas_rate = (1.03e-3, 999999.999)
        self.meas_rate_default = 0.1


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
    setpt = (3, 325)
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
