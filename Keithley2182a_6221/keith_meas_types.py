# -*- coding: utf-8 -*-
"""
keith_meas_types contains the the inner classes for measurement types in Keith.

classes_
    Delta: Delta measurement inner class
    DiffCon: Differential conductance measurement inner class
    PDelta: Pulse delta measurement inner class
    PDeltaLog: Pulse delta logarithmic sweep inner class
    PdeltaStair: Pulse delta staircase sweep inner class

Part of the V3 probe station collection.
@author: Sarah Friedensen
"""

from Keithley2182a_6221.keith_meas_abc import KeithMeasure
from typing import Union
from limits import key

mu = u'\xb5'


class DiffCon(KeithMeasure):
    """Implements attributes/methods unique to differential conductance mode.

    Inherits from KeithMeasure abstract base clas and overwrites some of its
    attributes so that they apply to differential conductance measurements.
    Extends __init__, get_meas_type_str, set_curr1, and set_curr2 and overrides
    set_curr_step, update_num_points, set_curr_delta, and set_meas_rate. Used
    as an inner class in Keith.

    attributes_
        curr1: Start current for differential conductance sweep in amps
        curr2: Stop current for differential conductance sweep in amps
        curr_step: Base step size for differential conductance sweep in amps.
            Differential conductance sweeps are basically staircase sweeps
            with differentials imposed on top of the stairs. curr_step is the
            step height.
        curr_step_text: Text for what curr_step represents in labels/headers
        curr_delta: Differential above/below the current step in amps
        field4_text: Labels Delta current in Diffcon
        meas_rate: Integration rate for the 2182a in PLC
        meas_rate_text: Text for what meas_rate represents in labels/headers
        meas_delay_text: Text for what meas_delay represents in labels/headers

    methods_
        __init__()
        get_meas_type_str()
        set_curr1(float)
        set_curr2(float)
        set_curr_step(float)
        update_num_points()
        set_curr_delta(float)
        set_meas_rate(int)
    """

    num_sweeps = None

    def __init__(self) -> None:
        """Instantiate differntial conductance measurement."""
        super().__init__(0)
        info = self.info
        self.curr1 = info.curr1['def']
        self.curr2 = info.curr2['def']
        self.curr_step = info.curr_step['def']
        self.curr_delta = info.curr_delta['def']
        self.meas_rate = info.rate['def']
        self.filter_idx = info.filt['def']
        self.filter_type = info.filt['txt'][self.filter_idx]
        self.num_points = info.points['def']

    def get_meas_type_str(self) -> str:
        """Return type of measurement followed by a new line."""
        return 'differential conductance\n'

    def set_curr1(self, start: float) -> None:
        """Set curr1 to start then update the number of points in the sweep."""
        super().set_curr1(start)
        self.update_num_points()

    def set_curr2(self, stop: float) -> None:
        """Set curr2 to stop, then update the number of points in the sweep."""
        super().set_curr2(stop)
        self.update_num_points()

    def set_curr_step(self, step: float) -> None:
        """Set curr_step to step, then update number of points in the sweep."""
        info = self.info.curr_step
        if not info['lim'][0] <= step <= info['lim'][1]:
            step = info['def']
            print(f"Current step out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({step:.2e} A).")
        self.curr_step = step
        self.update_num_points()

    def update_num_points(self) -> None:
        """Calculate number of points in a sweep and set num_points to that."""
        points = self.calc_num_points(self.curr1, self.curr2, self.curr_step)
        self.set_num_points(points)

    def set_curr_delta(self, delta: float) -> None:
        """Set curr_delta to delta."""
        info = self.info.curr_delta
        if not info['lim'][0] <= delta <= info['lim'][1]:
            delta = info['def']
            print(f"{info['txt']} out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({delta:.2e} A).")
        self.curr_delta = delta

    def set_meas_rate(self, rate: Union[int, float]) -> None:
        """Set 2182a integration rate (in PLC) to rate."""
        info = self.info.rate
        if rate not in info['lim']:
            rate = info['def']
            print(f"{info['txt'][self.meas_idx]} out of bounds ({info['lim']})"
                  + f".  Setting to default value ({rate}).")
        self.meas_rate = rate


class Delta(KeithMeasure):
    """Implements attributes and methods specific to delta measurement mode.

    Inherits from KeithMeasure abstract base clas and overwrites some of its
    attributes so that they apply to delta IV measurements.  Extends __init__
    and overrides get_meas_type_str, set_meas_rate, and set_filter_idx.  Used
    as an inner class in Keith.

    attributes_
        curr1: Delta high current in amps
        curr2: Delta low current in amps
        num_points: Pulse count for the delta measurement
        meas_rate: Integration rate for 2182a in power line cycles (PLC).

    methods_
        __init__()
        get_meas_type_str()
        set_meas_rate(int)
        set_filter_idx(int)
    """

    def __init__(self) -> None:
        """Instantiate delta measurement."""
        super().__init__(1)
        info = self.info
        self.curr1 = info.curr1['def']
        self.curr2 = info.curr2['def']
        self.num_points = info.points['def']
        self.meas_rate = info.rate['def']
        self.set_filter_idx(info.filt['def'])

    def get_meas_type_str(self) -> str:
        """Return type of measurement followed by a new line."""
        return 'delta\n'

    def set_meas_rate(self, rate: Union[int, float]) -> None:
        """Set the measurement rate attribute to rate (in PLC)."""
        info = self.info.rate
        if rate not in info['lim']:
            rate = info['def']
            print(f"{info['txt'][self.meas_idx]} out of bounds ({info['lim']})"
                  + f".  Setting to default value ({rate}).")
        self.meas_rate = rate

    def set_filter_idx(self, index: int) -> None:
        """Set the filter index attribute to idx to set filter type."""
        info = self.info.filt
        if index not in info['dic'].keys():
            index = info['def']
            print("Filter index out of bounds.  Setting to default filter"
                  + f"({info['txt'][index]}).")
        self.filter_idx = index
        self.filter_type = info['txt'][index]


class PDelta(KeithMeasure):
    """Implements methods and attributes specific to pulse delta mode.

    Inherits from KeithMeasure abstract base class and overwrites some of its
    attributes so they apply to pulse delta IV measurements. Extends __init__
    and overrides get_meas_type_str, set_meas_rate, set_pulse_width,
    set_filter_idx, and set_low_meas. Used as an inner class in Keith.

    attributes_
        curr1: High current in amps (float)
        curr2: Low current in amps (float)
        num_points: How many delta pulses to measure (int)
        pulse_width: Length of high current pulse in seconds (float)
        cycle_int: Period of the pulse delta cycle (lo-hi-lo) in PLC (int)
        low_meas: Whether to measure voltage on second lo in the cycle (bool)

    methods_
        __init__()
        get_meas_type_str()
        set_meas_rate(int)
        set_pulse_width(float)
        set_filter_idx(int)
        set_low_meas(bool)
    """

    def __init__(self) -> None:
        """Instantiate pulse delta measurement."""
        super().__init__(2)
        info = self.info
        self.curr1 = info.curr1['def']
        self.curr2 = info.curr2['def']
        self.num_points = info.points['def']
        self.pulse_width = info.width['def']
        self.cycle_int = info.rate['def']
        self.meas_delay = info.delay['def']
        self.set_filter_idx(info.filt['def'])

    def get_meas_type_str(self) -> str:
        """Return type of measurement followed by a new line."""
        return 'Pulse Delta\n'

    def set_meas_rate(self, rate: int) -> None:
        """Set cycle_int to rate. cycle_int plays the part of meas_rate.

        cycle_int should be greater than pulse width plus measurement delay.
        """
        info = self.info.rate
        if rate not in info['lim']:
            rate = info['def']
            print(f"{info['txt'][self.meas_idx]} out of bounds ({info['lim']})"
                  + f".  Setting to default value ({rate}).")
        self.cycle_int = rate

    def set_pulse_width(self, width: float) -> None:
        """Set pulse width to width in microseconds.

        Pulse width plus measurement delay should be less than the cycle time.
        """
        info = self.info.width
        if not info['lim'][0] <= width <= info['lim'][1]:
            width = info['def']
            print(f"Pulse width out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({width}).")
        self.pulse_width = width

    def set_low_meas(self, enable: bool) -> None:
        """Enable or disable measurement on the second lo in the cycle."""
        info = self.info.low_meas
        if enable not in info['lim']:
            enable = info['def']
            print("Enable 2nd low measurement argument invalid.  Setting to "
                  + f"default value ({enable}).")
        self.low_meas = enable

    def set_filter_idx(self, ftype: Union[int, str]) -> None:
        """Set filter index to index corresponding to ftype."""
        info = self.info.filt
        dic = info['dic']
        if ftype in dic.values():
            ftype = key(dic=dic, value=ftype)
        elif ftype not in dic.keys():
            ftype = info['def']
            print("Filter type index invalid.  Setting to default value "
                  + f"({info['txt'][ftype]}).")
        self.filter_idx = ftype
        self.filter_type = info['txt'][ftype]


class PDeltaStair(KeithMeasure):
    """Implements methods and attributes unique to pulse delta stair sweeps.

    Inherits from KeithMeasure abstract base class and overwrites some of its
    attributes so they apply to pulse delta staircase sweeps.  Extends
    __init__, set_curr1, set_curr2.  Overrides set_curr_step, set_meas_rate,
    set_pulse_width, set_num_sweeps, set_low_meas, update_num_points, and
    get_total_points.  Used as an inner class in Keith.

    attributes_
        curr1: Start current in amps (float)
        curr2: End current in amps (float)
        curr_step: Current step size in amps (float)
        num_points: Number of points in a single sweep (int)
        num_sweeps: Number of sweeps to perform (int)
        pulse_width: Length of the high current pulse in seconds (float)
        cycle_time: Quasiperiod of the pulse delta cycle (lo-hi-lo) in seconds
                    (float)
        low_meas: Whether to measure voltage on second lo in the cycle (bool)

    methods_
        __init__()
        get_meas_type_str()
        set_curr1(float)
        set_curr2(float)
        set_curr_step(float)
        update_num_points()
        set_meas_rate(float)
        set_pulse_width(float)
        set_num_sweeps(int)
        set_low_meas(bool)
        get_total_points()
    """

    def __init__(self) -> None:
        """Instantiate pulse delta staircase sweep measurement."""
        super().__init__(3)
        info = self.info
        self.curr1 = info.curr1['def']
        self.curr2 = info.curr2['def']
        self.curr_step = info.curr_step['def']
        self.num_points = self.calc_num_points(self.curr1, self.curr2,
                                               self.curr_step)
        self.num_sweeps = info.sweeps['def']
        self.pulse_width = info.width['def']
        self.meas_delay = info.delay['def']
        self.cycle_time = info.rate['def']
        self.filter_idx = info.filt['def']
        self.filter_type = info.filt['txt'][self.filter_idx]

    def get_meas_type_str() -> str:
        """Return the type of measurement followed by a new line."""
        return 'Pulse Delta Staircase Sweep\n'

    def set_curr1(self, start: float) -> None:
        """Set curr1 to start and update number of points in the sweep."""
        super().set_curr1(start)
        self.update_num_points()

    def set_curr2(self, stop: float) -> None:
        """Set curr2 to stop and update number of points in the sweep."""
        super().set_curr2(stop)
        self.update_num_points()

    def set_curr_step(self, step: float) -> None:
        """Set curr_step to step and update number of points in the sweep."""
        info = self.info.curr_step
        if not info['lim'][0] <= step <= info['lim'][1]:
            step = info['def']
            print(f"Current step out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({step:.2e} A).")
        self.curr_step = step
        self.update_num_points()

    def update_num_points(self) -> None:
        """Calculate number of points in a sweep and set num_points to that."""
        points = self.calc_num_points(self.curr1, self.curr2, self.curr_step)
        self.set_num_points(points)

    def set_meas_rate(self, rate: float) -> None:
        """Set cycle_time to rate.  cycle_time plays the part of meas_rate.

        cycle_time should be greater than pulse width plus measurement delay.
        """
        info = self.info.rate
        if not info['lim'][0] <= rate <= info['lim'][1]:
            rate = info['def']
            print(f"{info['txt'][self.meas_idx]} out of bounds ({info['lim']})"
                  + f".  Setting to default value ({rate}).")
        self.cycle_time = rate

    def set_pulse_width(self, width: float) -> None:
        """Set pulse_width to width.

        Pulse width plus measurement delay should be less than cycle_time.
        """
        info = self.info.width
        if not info['lim'][0] <= width <= info['lim'][1]:
            width = info['def']
            print(f"Pulse width out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({width}).")
        self.pulse_width = width

    def set_num_sweeps(self, sweeps: int) -> None:
        """Set num_sweeps to sweeps."""
        info = self.info.sweeps
        if sweeps not in info['lim']:
            sweeps = info['def']
            print(f"{info['txt']} out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({sweeps}).")
        self.num_sweeps = sweeps

    def set_low_meas(self, enable: bool) -> None:
        """Set low_meas to enable."""
        info = self.info.low_meas
        if enable not in info['lim']:
            enable = info['def']
            print("Enable 2nd low measurement argument invalid.  Setting to "
                  + f"default value ({enable}).")
        self.low_meas = enable

    def get_total_points(self) -> int:
        """Return total number of points for the set of sweeps."""
        return self.num_points * self.num_sweeps


class PDeltaLog(KeithMeasure):
    """Implements attributes and methods unique to pulse delta log sweeps.

    Inherits from KeithMeasure abstract base class and overwrites some of its
    attributes so that they apply to pulse delta log sweeps.  Extends __init__
    and overrides get_meas_type_str, set_meas_rate, set_pulse_width,
    set_num_sweeps, set_low_meas, and get_total_points.  Used as an inner class
    in Keith.

    attributes_
        curr1: Start current in amps (float)
        curr2: End current in amps (float)
        num_points: Number of points in a single sweep (int)
        num_sweeps: Number of sweeps to perform (int)
        pulse_width: Length of the high current pulse in seconds (float)
        cycle_time: Quasiperiod of the pulse delta cycle (lo-hi-lo) in seconds
                    (float)
        low_meas: Whether to measure voltage on second lo in the cycle (bool)

    methods_
        __init__()
        get_meas_type_str()
        set_meas_rate(float)
        set_pulse_width(float)
        set_num_sweeps(int)
        set_low_meas(bool)
        get_total_points()
    """

    def __init__(self) -> None:
        """Instantiate pulse delta log sweep."""
        super().__init__(4)
        info = self.info
        self.curr1 = info.curr1['def']
        self.curr2 = info.curr2['def']
        self.num_points = info.points['def']
        self.num_sweeps = info.sweeps['def']
        self.pulse_width = info.width['def']
        self.meas_delay = info.delay['def']
        self.cycle_time = info.rate['def']
        self.filter_idx = info.filt['def']
        self.filter_type = info.filt['txt'][self.filter_idx]

    def get_meas_type_str(self) -> None:
        """Return type of measurement followed by a new line."""
        return 'Pulse Delta Logarithmic Sweep\n'

    def set_meas_rate(self, rate: float) -> None:
        """Set cycle_time to rate. cycle_time plays the part of meas_rate.

        cycle_time should be greater than pulse width plus measurement delay.
        """
        info = self.info.rate
        if not info['lim'][0] <= rate <= info['lim'][1]:
            rate = info['def']
            print(f"{info['txt'][self.meas_idx]} out of bounds ({info['lim']})"
                  + f".  Setting to default value ({rate}).")
        self.cycle_time = rate

    def set_pulse_width(self, width: float) -> None:
        """Set pulse width to width.

        Pulse width plus measurement delay should be less than cycle_time.
        """
        info = self.info.width
        if not info['lim'][0] <= width <= info['lim'][1]:
            width = info['def']
            print(f"Pulse width out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({width}).")
        self.pulse_width = width

    def set_num_sweeps(self, sweeps: int) -> None:
        """Set num_sweeps to sweeps."""
        info = self.info.sweeps
        if sweeps not in info['lim']:
            sweeps = info['def']
            print(f"{info['txt']} out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({sweeps}).")
        self.num_sweeps = sweeps

    def set_low_meas(self, enable: bool) -> None:
        """Set low_meas to enable."""
        info = self.info.low_meas
        if enable not in info['lim']:
            enable = info['def']
            print("Enable 2nd low measurement argument invalid.  Setting to "
                  + f"default value ({enable}).")
        self.low_meas = enable

    def get_total_points(self) -> int:
        """Return the number of points for the set of sweeps."""
        return self.num_points * self.num_sweeps
