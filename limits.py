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

# from numpy import array
from typing import Dict


mu = u"\xb5"
ohm = u"\u2126"


def key(dic: Dict, val, initer=False):
    """Get the 1st matching key from a dictionary dic given a value val.

    initer is an optional argument indicating that val is inside an iterable
    structure such as a tuple, and its existence within that tuple is enough
    to match it with the key.
    """
    if initer:
        return tuple(k for k, v in dic.items() if (val == v or val in v))[0]
    return tuple(k for k, v in dic.items() if val == v)[0]


class KeithInfo:
    """Contains instrument limits and defaults for the Keithley stack."""

    addr = {'lim': range(1, 32),
            'def': 12}

    measure = {'def': False}

    meas = {'txt': {0: "diffCond",
                    1: "delta",
                    2: "pulseDelta",
                    3: "sweepPulseDeltaStair",
                    4: "sweepPulseDeltaLog"},
            'labels': ["Differential Conductance",
                       "Delta",
                       "Pulse Delta",
                       "Pulse Delta Staircase Sweep",
                       "Pulse Delta Logarithmic Sweep"],
            'def': 0}

    unit = {'dic': {0: 'volts',
                    1: 'siemens',
                    2: 'ohms',
                    3: 'avgw',
                    4: 'peakw'},
            'labels': ['Voltage (V)',
                       '(Differential) Conductance (S)',
                       f'(Differential) Resistance ({ohm})',
                       'Average Power (W)',
                       'Peak Power (W)'],
            'def': 0}

    power = {'lim': ("AVER", "PEAK"),
             'def': 'AVER'}

    sour_range = {'dic': {0: 2.0e-9,
                          1: 20.0e-9,
                          2: 200.0e-9,
                          3: 2.0e-6,
                          4: 20.0e-6,
                          5: 200.0e-6,
                          6: 2.0e-3,
                          7: 20.0e-3,
                          8: 100.0e-3},
                  'def': 4,
                  'txt': {0: "(nA)",
                          1: "(nA)",
                          2: "(nA)",
                          3: f"({mu}A)",
                          4: f"({mu}A)",
                          5: f"({mu}A)",
                          6: "(mA)",
                          7: "(mA)",
                          8: "(mA)"},
                  'mult': {0: 1.0e-9,
                           1: 1.0e-6,
                           2: 1.0e-3},
                  'minmax': {0: 2.0,
                             1: 20.0,
                             2: 200.0,
                             3: 2.0,
                             4: 20.0,
                             5: 200.0,
                             6: 2.0,
                             7: 20.0,
                             8: 100.0},
                  'typ': {'dic': {0: "Best",
                                  1: "Fixed"},
                          'def': 1}
                  }

    volt_range = {'dic': {2: 10.0e-3,
                          3: 100.0e-3,
                          4: 1.0,
                          5: 10.0,
                          6: 100.0},
                  'def': 2,
                  'labels': ['10 mV', '100 mV', '1 V', '10 V', '100 V']}

    compl_volt = {'lim': (0.1, 105.0),
                  'def': 10.0}
    cab_def = False

    field4 = {'def': 0,
              'label': {0: 'Current Delta ',
                        1: None,
                        2: None,
                        3: 'Number Points',
                        4: 'Number Points'}
              }

    count = {'def': 11,
             'txt': {0: None,
                     1: 'Pulse Count',
                     2: 'Pulse Count',
                     3: 'Number Sweeps',
                     4: 'Number Sweeps'}
             }

    fwindow = {'lim': (0.0, 10.0),
               'def': 0.0}
    fcount = {'lim': range(2, 301),
              'def': 10}

    def __init__(self):
        """Initialize KeithInfo."""
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
        self.rate = {'lim': range(1, 61),  # This is in PLC
                     'def': 1,
                     'txt': {0: 'Measurement Rate (PLC)',
                             1: 'Measurement Rate (PLC)',
                             2: 'Cycle Interval (PLC)',
                             3: 'Cycle Time (s)',
                             4: 'Cycle Time (s)'},
                     'decim': {0: 0,
                               1: 0,
                               2: 0,
                               3: 3,
                               4: 3}
                     }
        self.delay = {'lim': (1.0e-3, 9999.999),  # This is in seconds
                      'def': 2.0e-3,
                      # TODO: Verify that that this delay is pulse delay
                      'txt': {0: "Measurement Delay (ms)",
                              1: "Measurement Delay (ms)",
                              2: f"Pulse Delay ({mu}s)",
                              3: f"Pulse Delay ({mu}s)",
                              4: f"Pulse Delay ({mu}s)"}
                      }
        self.width = {'lim': None,
                      'def': None,
                      'txt': {0: None,
                              1: None,
                              2: f"Pulse Width ({mu}s)",
                              3: f"Pulse Width ({mu}s)",
                              4: f"Pulse Width ({mu}s)"}
                      }
        self.points = {'lim': range(1, 65537),
                       'def': 11,
                       'txt': "Number Points",
                       'decim': 0
                       }

        self.filt = {'dic': {0: "MOV",  # This replaces filter_switch
                             1: "REP"},
                     'def': 0,
                     'txt': {0: "Moving",
                             1: "Repeating"},
                     'labels': ["Moving", "Repeating"],
                     'ondef': False
                     }


class DconInfo(KeithInfo):
    """DconInfo contains limits specific to differential conductance.

    DconInfo inherits from KeithInfo"""

    idx = 0

    def __init__(self):
        super().__init__()
        self.curr1['def'] = -10.0e-6
        self.curr2['def'] = 10.0e-6
        self.curr_step['lim'] = (0, 105.0e-3)
        self.curr_step['def'] = 1.0e-6
        self.curr_delta = {'lim': (0, 105.0e-3),
                           'def': 1.0e-6,
                           'txt': self.field4['label'][self.idx],
                           'decim': 5}

        self.points['def'] = abs(
            ((self.curr2['def'] - self.curr1['def']) // self.curr_step['def'])
            + 1)

        del self.filt['dic'][0]
        del self.filt['txt'][0]
        self.filt['def'] = 1


class DeltaInfo(KeithInfo):
    """DeltaInfo contains limits specific to delta measurements.

    DeltaInfo inherits from KeithInfo."""

    idx = 1

    def __init__(self):
        super().__init__()
        self.curr1['lim'] = (0, 105.0e-3)
        self.curr1['def'] = 10.0e-3
        self.curr2['lim'] = (-105.0e-3, 0)
        self.curr2['def'] = 0

        self.points['def'] = 100


class PDeltInfo(KeithInfo):
    """PDeltInfo contains limits specific to pulse delta measurements.

    PDeltInfo inherits from KeithInfo."""
    idx = 2
    low_meas = {'lim': (1, 2),
                'def': 2}

    def __init__(self):
        super().__init__()
        self.curr1['def'] = 1.0e-3
        self.curr2['def'] = 0.0
        self.rate['lim'] = range(5, 1000000)
        self.rate['def'] = 5
        self.delay['lim'] = (16.0e-6, 11.966e-3)
        self.delay['def'] = 16.0e-6
        self.width['lim'] = (50.0e-6, 12.0e-3)
        self.width['def'] = 110.0e-6

        self.points['def'] = 100


# TODO: Determine if I need separate classes for PDeltStair and PDeltLog
class SweepInfo(PDeltInfo):
    """SweepInfo contains limits specific to both types of pulse delta sweeps.

    SweepInfo inherits from PDeltInfo."""

    idx = 3

    def __init__(self):
        super().__init__()
        # TODO: Determine if negative currents OK in pulse delta sweeps
        self.points['lim'] = range(1, 65535)
        self.points['def'] = 11
        self.rate['lim'] = (1.0e-3, 999999.999)
        self.rate['def'] = 0.1
        self.sweeps = {'txt': "Number Sweeps",
                       'lim': range(1, 10000),
                       'def': 1}

        del self.filt['dic'][1]
        del self.filt['txt'][1]
        self.filt['def'] = 0


class PDeltLogInfo(SweepInfo):
    """PDeltLogInfo contains limits specific to pulse delta measurements.

    PDeltLogInfo inherits from SweepInfo."""

    idx = 4

    def __init__(self):
        super().__init__()


# FIXME: Maybe??? change 3, 4 to both SweepInfo
ivinfo = {'dic': {0: DconInfo,
                  1: DeltaInfo,
                  2: PDeltInfo,
                  3: SweepInfo,
                  4: PDeltLogInfo},
          'def': KeithInfo().meas['def'],
          # 'txt': {0: "Differential Conductance",
          #         1: "Delta",
          #         2: "Pulse Delta",
          #         3: "Pulse Delta Staircase Sweep",
          #         4: "Pulse Delta Logarithmic Sweep"},
          'field4': {0: DconInfo().curr_delta,
                     1: None,
                     2: None,
                     3: SweepInfo().points,
                     # TODO: Determine if 4 can be the same as 3
                     4: PDeltLogInfo().points}}


class TempInfo():
    """Contains instrument parameter limits and defaults for LakeShore 336."""
    addr = {'lim': range(1, 32),
            'def': 11}

    measure = {'def': True}

    out = {'lim': (1, 2),  # FIXME: Is this ever used? .keys() works fine...
           'def': 2,
           'txt': {1: 'Radiation Shield Heater',
                   2: 'Sample Heater'},
           'name': {1: ('out1', 'rad'),
                    2: ('out2', 'stage')}
           }

    inpt = {'lim': range(0, 8),
            'def': 5,
            'txt': {0: ('A', 'Cryocooler 1 first stage'),
                    1: ('B', 'Cryocooler 1 second stage'),
                    2: ('C', 'Magnet Plate'),
                    3: ('D1', 'Magnet Top'),
                    4: ('D2', 'Cryocooler 2 second stage'),
                    5: ('D3', 'Radiation Shield'),
                    6: ('D4', 'Sample Control'),
                    7: ('D5', 'Inner Radiation Shield')}
            }
    to_measure = {'dic': {0: 'controlled',
                          1: 'all'},
                  'def': 0}

    outmode = {'lim': range(0, 4),
               'def': 0,
               'labels': {0: 'Off',
                          1: 'Closed loop PID',
                          2: 'Zone',
                          3: 'Open loop'}}
    power = {'lim': range(0, 4),
             'def': 0,
             'labels': {0: 'Off',
                        1: 'Low',
                        2: 'Medium',
                        3: 'High'}}
    # Rate is in K/min. 0 means "ramp as fast as possible."
    # TODO: Fix lim to work with new validators
    rate = {'lim': (0.1, 100.0, 0),
            'def': 1.0}

    setpt = {'lim': (3, 325),
             'def': 4.0}

    rad_cont = {'def': True}
    stage_cont = {'def': True}


class MagInfo():
    """Contains instrument parameter info and limits for the AMI 430.

    This is ONLY for reader reference and has no effect on the software."""
    addr = {'lim': range(1, 11),
            'def': 2}

    time = {'unit': {0: 'Seconds',
                     1: 'Minutes'},
            'def': 0}

    volt = {'lim': (0.001, 6),
            'def': 0.55}  # DO NOT CHANGE THE VOLT CEILING

    curr = {'lim': (0, 39.37),
            'def': 39.37}    # 1 T = 10 kG

    # coil const in {field_unit}/A
    # coil_const = (30/26.3, 3/26.3, 1)
    coil_const_center = (70/39.37, 7/39.37, 1)
    coil_const_stage = (0, 0, 1)  # TODO: Test coil constant at stage

    quench_temp = {'range': [0.0, 8.0],
                   'def': 6.0}

    state_table = {
            1: 'RAMPING to target value',
            2: 'HOLDING at target value',
            3: 'PAUSED',
            4: 'Ramping in MANUAL UP mode',
            5: 'Ramping in MANUAL DOWN mode',
            6: 'ZEROING CURRENT',
            7: 'Quench detected',
            8: 'At ZERO current',
            9: 'Heating persistent switch',
            10: 'Cooling persistent switch'}

    trig_out_reg = {
            0: 'Magnet Voltage',
            1: 'Magnet Current',
            2: 'Magnet Field',
            3: 'Date and Time',
            4: 'None',
            5: 'Formatted Output',
            6: 'Serial Interface',
            7: 'Ethernet Interface'}

    def __init__(self):
        """Init all the variables that need to refer to something else."""
        self.field = {
            'lim': {0: 70,
                    1: 7,
                    2: 39.37},
            'def': {i: 0 for i, v in enumerate(self.coil_const_stage)},
            'unit': {0: 'Kilogauss',
                     1: 'Tesla',
                     2: 'Amps'}
        }
        self.rate = {
            # values for seconds are:
            # {0: (1.90e-6, 11.4), 1: (1.90e-7, 1.14), 2: (2.67e-6, 10)}
            # values for minutes are:
            # {0: (1.14e-4, 684), 1: (1.14e-5, 68.4), 2: (1.0e-4, 600)}
            # TODO: Verify this is correct
            'lim': {'seconds': {i: (1.0e-4/60*val, 10*val)
                                for i, val in enumerate(self.coil_const)},
                    'minutes': {i: (1.0e-4*val, 600*val)
                                for i, val in enumerate(self.coil_const)}
                    },
            # Rate segments have the unit (field)/seconds
            # DO NOT CHANGE THE RATES
            'rates': {'seg1': (1.48e-2/60*val for i, val in enumerate(
                        self.coil_const_stage)),
                      'seg2': (3.45e-3/60*val for i, val in enumerate(
                          self.coil_const_stage))}
        }
