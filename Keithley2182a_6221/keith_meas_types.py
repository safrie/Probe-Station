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

filter_switch = {
        0: 'Moving',
        1: 'Repeating'}


class Delta(KeithMeasure):
    """Implements attributes and methods specific to delta measurement mode.

    Inherits from KeithMeasure abstract base clas and overwrites some of its
    attributes so that they apply to delta IV measurements.  Extends __init__
    and overrides get_meas_type_str, set_meas_rate, and set_filter_idx.  Used
    as an inner class in Keith.

    attributes_
        curr1: Delta high current in microamps
        curr2: Delta low current in microamps
        num_points: Pulse count for the delta measurement
        meas_rate: Integration rate for 2182a in power line cycles (PLC).

    methods_
        __init__()
        get_meas_type_str()
        set_meas_rate(int)
        set_filter_idx(int)
    """

    curr1_text = 'High Current '
    curr2_text = 'Low Current '
    meas_rate_text = 'Measurement Rate (PLC) '
    meas_delay_text = 'Measurement Delay (ms) '
    pulse_count_text = 'Pulse Count'

    def __init__(self) -> None:
        """Instantiate delta measurement."""
        super().__init__()
        self.curr1 = 10.00
        self.num_points = 100
        self.meas_rate = 1
        self.set_filter_idx(0)

    def get_meas_type_str(self) -> str:
        """Return type of measurement followed by a new line."""
        return 'delta\n'

    def set_meas_rate(self, rate: Union[int, float]) -> None:
        """Set the measurement rate attribute to rate (in PLC)."""
        self.meas_rate = rate

    def set_filter_idx(self, index: int) -> None:
        """Set the filter index attribute to idx to set filter type."""
        self.filter_idx = index
        self.filter_type = filter_switch[index]


class DiffCon(KeithMeasure):
    """Implements attributes/methods unique to differential conductance mode.

    Inherits from KeithMeasure abstract base clas and overwrites some of its
    attributes so that they apply to differential conductance measurements.
    Extends __init__, get_meas_type_str, set_curr1, and set_curr2 and overrides
    set_curr_step, update_num_points, set_curr_delta, and set_meas_rate. Used
    as an inner class in Keith.

    attributes_
        curr1: Start current for differential conductance sweep in microamps
        curr2: Stop current for differential conductance sweep in microamps
        curr_step: Base step size for differential conductance sweep in
            microamps. Differential conductance sweeps are basically staircase
            sweeps with differentials imposed on top of the stairs. curr_step
            is the step height.
        curr_step_text: Text for what curr_step represents in labels/headers
        curr_delta: Differential above/below the current step in microamps
        field4_text: Text for what field4 represents in labels/headers
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

    curr1_text = 'Start Current '
    curr2_text = 'Stop Current '
    curr_step_text = 'Step Size '
    curr_delta_text = field4_text = 'Delta Current '
    meas_rate_text = 'Measurement Rate (PLC)'
    meas_delay_text = 'Measurement Delay (ms)'

    num_sweeps = None

    def __init__(self) -> None:
        """Instantiate differntial conductance measurement."""
        super().__init__()
        self.curr1 = -1000.00
        self.curr2 = 1000.00
        self.curr_step = 10.00
        self.curr_delta = 1.00
        self.meas_rate = 1
        self.filter_idx = 1
        self.filter_type = 'Repeating'
        self.num_points = 0

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
        self.curr_step = step
        self.update_num_points()

    def update_num_points(self) -> None:
        """Calculate number of points in a sweep and set num_points to that."""
        points = self.calc_num_points(self.curr1, self.curr2, self.curr_step)
        self.set_num_points(points)

    def set_curr_delta(self, delta: float) -> None:
        """Set curr_delta to delta."""
        self.curr_delta = delta

    def set_meas_rate(self, rate: Union[int, float]) -> None:
        """Set 2182a integration rate (in PLC) to rate."""
        self.meas_rate = rate


class PDelta(KeithMeasure):
    """Implements methods and attributes specific to pulse delta mode.

    Inherits from KeithMeasure abstract base class and overwrites some of its
    attributes so they apply to pulse delta IV measurements. Extends __init__
    and overrides get_meas_type_str, set_meas_rate, set_pulse_width,
    set_filter_idx, and set_low_meas. Used as an inner class in Keith.

    attributes_
        curr1: High current in microamps (float)
        curr2: Low current in microamps (float)
        num_points: How many delta pulses to measure (int)
        pulse_width: Length of high current pulse in microseconds (float)
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

    curr1_text = 'High Current '
    curr2_text = 'Low Current '
    meas_rate_text = 'Cycle Interval (PLC)'
    meas_delay_text = 'Source Delay (\N{GREEK SMALL LETTER MU}s)'
    pulse_width_text = 'Pulse Width (\N{GREEK SMALL LETTER MU}s)'
    pulse_count_text = 'Pulse Count'

    def __init__(self) -> None:
        """Instantiate pulse delta measurement."""
        super().__init__()
        self.curr1 = 10.00
        self.curr2 = 0.00
        self.num_points = 100
        self.pulse_width = 110
        self.cycle_int = 5
        self.meas_delay = 16.00
        self.set_filter_idx(0)

    def get_meas_type_str(self) -> str:
        """Return type of measurement followed by a new line."""
        return 'Pulse Delta\n'

    def set_meas_rate(self, rate: int) -> None:
        """Set cycle_int to rate. cycle_int plays the part of meas_rate.

        cycle_int should be greater than pulse width plus measurement delay.
        """
        self.cycle_int = rate

    def set_pulse_width(self, width: float) -> None:
        """Set pulse width to width in microseconds.

        Pulse width plus measurement delay should be less than the cycle time.
        """
        self.pulse_width = width

    def set_low_meas(self, enable: bool) -> None:
        """Enable or disable measurement on the second lo in the cycle."""
        self.low_meas = enable

    def set_filter_idx(self, index: int) -> None:
        """Set filter index to index."""
        self.filter_idx = index
        self.filter_type = filter_switch[index]


class PDeltaLog(KeithMeasure):
    """Implements attributes and methods unique to pulse delta log sweeps.

    Inherits from KeithMeasure abstract base class and overwrites some of its
    attributes so that they apply to pulse delta log sweeps.  Extends __init__
    and overrides get_meas_type_str, set_meas_rate, set_pulse_width,
    set_num_sweeps, set_low_meas, and get_total_points.  Used as an inner class
    in Keith.

    attributes_
        curr1: Start current in microamps (float)
        curr2: End current in microamps (float)
        num_points: Number of points in a single sweep (int)
        num_sweeps: Number of sweeps to perform (int)
        pulse_width: Length of the high current pulse in microseconds (float)
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

    curr1_text = 'Start Current '
    curr2_text = 'Stop Current '
    field4_text = 'Number Points '
    meas_rate_text = 'Cycle Time (s)'
    meas_delay_text = 'Source Delay (\N{GREEK SMALL LETTER MU}s)'
    pulse_width_text = 'Pulse Width (\N{GREEK SMALL LETTER MU}s)'
    pulse_count_text = 'Number Sweeps'

    def __init__(self) -> None:
        """Instantiate pulse delta log sweep."""
        super().__init__()
        self.curr1 = 1.00
        self.curr2 = 10.00
        self.num_points = 10
        self.num_sweeps = 1
        self.pulse_width = 120
        self.meas_delay = 16
        self.cycle_time = 5.0
        self.filter_idx = 0
        self.filter_type = 'Moving'

    def get_meas_type_str(self) -> None:
        """Return type of measurement followed by a new line."""
        return 'Pulse Delta Logarithmic Sweep\n'

    def set_meas_rate(self, rate: float) -> None:
        """Set cycle_time to rate. cycle_time plays the part of meas_rate.

        cycle_time should be greater than pulse width plus measurement delay.
        """
        self.cycle_time = rate

    def set_pulse_width(self, width: float) -> None:
        """Set pulse width to width.

        Pulse width plus measurement delay should be less than cycle_time.
        """
        self.pulse_width = width

    def set_num_sweeps(self, sweeps: int) -> None:
        """Set num_sweeps to sweeps."""
        self.num_sweeps = sweeps

    def set_low_meas(self, enable: bool) -> None:
        """Set low_meas to enable."""
        self.low_meas = enable

    def get_total_points(self) -> int:
        """Return the number of points for the set of sweeps."""
        return self.num_points * self.num_sweeps


class PDeltaStair(KeithMeasure):
    """Implements methods and attributes unique to pulse delta stair sweeps.

    Inherits from KeithMeasure abstract base class and overwrites some of its
    attributes so they apply to pulse delta staircase sweeps.  Extends
    __init__, set_curr1, set_curr2.  Overrides set_curr_step, set_meas_rate,
    set_pulse_width, set_num_sweeps, set_low_meas, update_num_points, and
    get_total_points.  Used as an inner class in Keith.

    attributes_
        curr1: Start current in microamps (float)
        curr2: End current in microamps (float)
        curr_step: Current step size in microamps (float)
        num_points: Number of points in a single sweep (int)
        num_sweeps: Number of sweeps to perform (int)
        pulse_width: Length of the high current pulse in microseconds (float)
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

    curr1_text = 'Start Current '
    curr2_text = 'Stop Current '
    curr_step_text = 'Step Size '
    field4_text = 'Number Points '
    meas_rate_text = 'Cycle Time (s)'
    meas_delay_text = 'Source Delay (\N{GREEK SMALL LETTER MU}s)'
    pulse_width_text = 'Pulse Width (\N{GREEK SMALL LETTER MU}s)'
    pulse_count_text = 'Number Sweeps'

    def __init__(self) -> None:
        """Instantiate pulse delta staircase sweep measurement."""
        super().__init__()
        self.curr1 = 1.00
        self.curr2 = 10.00
        self.curr_step = 0.100
        self.num_points = self.calc_num_points(self.curr1, self.curr2,
                                               self.curr_step)
        self.num_sweeps = 1
        self.pulse_width = 120
        self.meas_delay = 16
        self.cycle_time = 5.0
        self.filter_idx = 0
        self.filter_type = 'Moving'

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
        self.cycle_time = rate

    def set_pulse_width(self, width: float) -> None:
        """Set pulse_width to width.

        Pulse width plus measurement delay should be less than cycle_time.
        """
        self.pulse_width = width

    def set_num_sweeps(self, sweeps: int) -> None:
        """Set num_sweeps to sweeps."""
        self.num_sweeps = sweeps

    def set_low_meas(self, enable: bool) -> None:
        """Set low_meas to enable."""
        self.low_meas = enable

    def get_total_points(self) -> int:
        """Return total number of points for the set of sweeps."""
        return self.num_points * self.num_sweeps
