# -*- coding: utf-8 -*-
"""
limits contains the bounds for parameter settings for all instruments.

classes_
    KeithInfo: Bounds for the Keithley 2182a/6221 stack
    DconInfo: Bounds for Keithley differential conductance measurement
    DeltaInfo: Bounds for Keithley delta measurement
    PDeltInfo: Bounds for Keithley pulse delta measurement
    PDeltStairLims: Bounds for Keithley pulse delta staircase sweep
    PDeltLogLims: Bounds for Keithley pulse delta logarithmic sweep

    TempLims: Bounds for the LakeShore 336 temperature controller
    MagLims: Bounds for the AMI 430 magnet power supply

Part of the V3 Probe Station Collection.
@author: Sarah Friedensen
"""

from numpy import array


mu = u"\xb5"


# TODO: Change veryone over to KeithInfo
class KeithInfo:
    """Contains instrument limits and defaults for the Keithley stack."""

    addr = {'lim': range(1, 32),
            'def': 12}

    meas = {'txt': {0: "diffCond",
                    1: "delta",
                    2: "pulseDelta",
                    3: "sweepPulseDeltaStair",
                    4: "sweepPulseDeltaLog"},
            'def': 0}

    unit = {'dic': {0: 'volts',
                    1: 'siemens',
                    2: 'ohms',
                    3: 'avgw',
                    4: 'peakw'},
            'def': 0}

    power = {'lim': ("AVER", "PEAK"),
             'def': 'AVER'}

    source_range = {'dic': {0: 2.0e-9,
                            1: 20.0e-9,
                            2: 200.0e-9,
                            3: 2.0e-6,
                            4: 20.0e-6,
                            5: 200.0e-6,
                            6: 2.0e-3,
                            7: 20.0e-3,
                            8: 100.0e-3},
                    'def': 5,
                    'txt': {0: "(nA)",
                            1: "(nA)",
                            2: "(nA)",
                            3: f"({mu}A)",
                            4: f"({mu}A)",
                            5: f"({mu}A)",
                            6: "(mA)",
                            7: "(mA)",
                            8: "(mA)"},
                    'mult': {-1: 1.0e-9,
                             0: 1.0e-6,
                             1: 1.0e-3},
                    'minmax': {0: 2.0,
                               1: 20.0,
                               2: 200.0,
                               3: 2.0,
                               4: 20.0,
                               5: 200.0,
                               6: 2.0,
                               7: 20.0,
                               8: 100.0}
                    }

    source_range_type = {'dic': {0: "Best",
                                 1: "Fixed"},
                         'def': 0}

    volt_range = {'dic': {2: 100.0e-3,
                          3: 10.0e-3,
                          4: 1.0,
                          5: 10.0,
                          6: 100.0},
                  'def': 2}

    compl_volt = {'lim': (0.1, 105.0),
                  'def': 10.0}
    cab_def = False

    fwindow = {'lim': (0.0, 10.0),
               'def': 0.0}
    fcount = {'lim': range(2, 301),
              'def': 10}

    def __init__(self):

        self.curr1 = {'lim': (-105.0e-3, 105.0e-3),
                      'def': -1.0e-3,
                      'txt': {0: 'Start Current ',
                              1: 'High Current ',
                              2: 'High Current ',
                              3: 'Start Current ',
                              4: 'Start Current '}
                      }
        self.curr2 = {'lim': (-105.0e-3, 105.0e-3),
                      'def': 1.0e-3,
                      'txt': {0: 'Stop Current ',
                              1: 'Low Current ',
                              2: 'Low Current ',
                              3: 'Stop Current ',
                              4: 'Stop Current '}
                      }
        self.curr_step = {'lim': (1.0e-13, 105.0e-3),
                          'def': 1.0e-5,
                          'txt': {0: 'Step Size ',
                                  1: None,
                                  2: None,
                                  3: 'Step Size ',
                                  4: None}
                          }
        self.field4 = {'lim': None,
                       'def': None,
                       'txt': {0: 'Current Delta ',
                               1: None,
                               2: None,
                               3: 'Number Points',
                               4: 'Number Points'}
                       }
        self.meas_rate = {'lim': (0.1, 60),  # This is in PLC
                          'def': 1,
                          'txt': {0: 'Measurement Rate (PLC)',
                                  1: 'Measurement Rate (PLC)',
                                  2: 'Cycle Interval (PLC)',
                                  3: 'Cycle Time (s)',
                                  4: 'Cycle Time (s)'}
                          }
        self.delay = {'lim': (1.0e-3, 9999.999),  # This is in seconds
                      'def': 2.0e-3,
                      # FIXME: Verify that that this delay is pulse delay
                      'txt': {0: "Measurement Delay (ms)",
                              1: "Measurement Delay (ms)",
                              2: f"Pulse Delay ({mu}s)",
                              3: f"Pulse Delay ({mu}s)"}
                      }
        self.width = {'lim': None,
                      'def': None,
                      'txt': {0: None,
                              1: None,
                              2: f"Pulse Width ({mu}s)",
                              3: f"Pulse Width ({mu}s)",
                              4: f"Pulse Width ({mu}s)"}
                      }
        self.count = {'lim': range(1, 65537),
                      'def': 11,
                      'txt': {0: None,
                              1: 'Pulse Count',
                              2: 'Pulse Count',
                              3: 'Number Sweeps',
                              4: 'Number Sweeps'}
                      }
        self.filt = {'dic': {0: "MOV",  # This replaces filter_switch
                             1: "REP"},
                     'def': 0,
                     'txt': {0: "Moving",
                             1: "Repeating"}
                     }


class DconInfo(KeithInfo):
    """DconInfo contains limits specific to differential conductance.

    DconInfo inherits from KeithInfo"""
    curr_delta = (0, 105.0e-3)
    curr_delta_def = 1.0e-6

    def __init__(self):
        super().__init__()
        self.filt_def = 1
        self.filt = {self.filt_def: self.filt[self.filt_def]}
        self.filt_text = self.filt_text[self.filt_def]
        self.curr1_def = -10.0e-6
        self.curr2_def = 10.0e-6
        self.curr_step_def = 1.0e-6
        self.points_def = 0


class DeltaInfo(KeithInfo):
    """DeltaInfo contains limits specific to delta measurements.

    DeltaInfo inherits from KeithInfo."""

    def __init__(self):
        super().__init__()
        self.curr1 = (0, 105.0e-3)
        self.curr1_def = 10.0e-3
        self.curr2 = (-105.0e-3, 0)
        self.curr2_def = 0


class PDeltInfo(KeithInfo):
    """PDeltInfo contains limits specific to pulse delta measurements.

    PDeltInfo inherits from KeithInfo."""

    width = (50.0e-6, 12.0e-3)
    width_def = 110.0e-6
    low_meas = (1, 2)
    low_meas_def = 2

    def __init__(self):
        super().__init__()
        self.curr1_def = 1.0e-3
        self.curr2_def = 0.0
        self.delay = (16.0e-6, 11.966e-3)
        self.delay_def = 16.0e-6
        self.meas_rate = (5, 999999)  # This is in PLC
        self.meas_rate_def = 5


class PDeltStairInfo(PDeltInfo):
    """PDeltStairInfo contains limits specific to pulse delta measurements.

    PDeltStairInfo inherits from PDeltInfo."""

    sweeps = range(1, 10000)
    sweeps_def = 1

    def __init__(self):
        super().__init__()
        # ???: Can you have a negative curr2?
        # self.curr2 = (0.0, 105.0e-3)
        self.curr2_def = -1.0
        self.meas_rate = (1.0e-3, 999999.999)
        self.meas_rate_def = 0.1


class PDeltLogInfo(PDeltInfo):
    """PDeltLogInfo contains limits specific to pulse delta measurements.

    PDeltLogInfo inherits from PDeltInfo."""

    sweeps = range(1, 10000)
    sweeps_def = 1

    def __init__(self):
        super().__init__()
        # ???: Do I need to set curr2 bounds for this to avoid negative?
        self.curr2_def = 0
        self.meas_rate = (1.03e-3, 999999.999)
        self.meas_rate_def = 0.1


# TODO: Change to TempInfo
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


# TODO: Change to MagInfo
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
