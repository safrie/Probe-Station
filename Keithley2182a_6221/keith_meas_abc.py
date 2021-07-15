# -*- coding: utf-8 -*-
"""
Abstract base class for shared methods/attributes for Keithley measurements.

Classes_
    KeithMeasure

Part of the probe station V3 collection.
@author: Sarah Friedensen
"""
from abc import ABCMeta, abstractmethod
from typing import Union
from limits import KeithInfo as kinfo, ivinfo, key


class KeithMeasure():
    """ABC for universal attributes/methods for Keithley IV measurements.

    attributes_
        curr1_text: What curr1 represents in labels/headers.
        curr2_text: What curr2 represents in labels/headers.
        curr_step_text: What curr_step represents in labels/headers.
        curr_delta_text: What curr_delta represents in labels/headers.
        meas_rate_text: What meas_rate represents in labels/headers.
        meas_delay_text: What meas_delay represents in labels/headers.
        pulse_width_text: What pulse_width represents in labels/headers.
        pulse_count_text: What pulse_count represents in labels/headers.
        unit_idx: Index for what unit measurement uses.
        curr1: Float for current1.
        curr2: Float for current2.
        num_points: Number of points for the measurement.
        meas_delay: How long 2182A will wait to measure after current change by
            6221 (units vary).
        low_meas: Whether or not 2nd 'low' measurement occurs (if applicable).
        filter_idx: Index specifying filter type.
        filter_type: String specifying filter type.
        filter_on: Whether or not filtering is enabled.
        filter_window: Filter window by % of measurement.  Range is 0-10.
        filter_count: Number of measurements to bin in order to filter.

    methods_
        __init__()
        get_meas_type_str()
        set_unit_idx(int)
        set_curr1(float)
        set_curr2(float)
        set_curr_step(float)
        set_curr_delta(float)
        set_num_points(int)
        calc_num_points(float, float, float)
        set_num_sweeps(int)
        set_meas_rate(int)
        set_meas_delay(float)
        set_pulse_width(float)
        set_pulse_count(int) MAYBE
        set_low_meas(bool)
        set_filter_idx(int)
        set_filter_on(bool)
        set_filter_window(int)
        set_filter_count(int)
        get_total_points()
        update_num_points()
    """

    __metaclass__ = ABCMeta
    curr1_text = ''
    curr2_text = ''
    curr_step_text = ''
    curr_delta_text = ''
    meas_rate_text = ''
    meas_delay_text = ''
    pulse_width_text = ''
    pulse_count_text = ''

    def __init__(self, meas_idx: int) -> None:
        """Instantiate general Keithley 6221/2182A transport measurement."""
        self.info = ivinfo['dic'][meas_idx]()
        self.meas_idx = meas_idx
        self.unit_idx = kinfo().unit['def']
        self.curr1 = self.info.curr1['def']
        self.curr2 = self.info.curr2['def']
        self.num_points = self.info.points['def']
        self.meas_delay = self.info.delay['def']
        # NOTE: This generator expression may break initialization?
        self.low_meas = (self.info.low_meas['def'] if meas_idx > 1 else None)
        self.num_sweeps = (self.info.sweeps['def'] if meas_idx > 2 else None)
        self.filter_idx = self.info.filt['def']
        self.filter_on = kinfo().filt['ondef']
        self.filter_window = kinfo().fwindow['def']
        self.filter_count = kinfo().fcount['def']
        self.pulse_width = self.info.width['def']

    @abstractmethod
    def get_meas_type_str(self) -> None:
        """Return a string of the type of measurement."""

    def set_unit(self, unit: Union[int, str]) -> int:
        """Set the unit index for Keithleys to unit or corresponding index."""
        dic = kinfo().unit['dic']
        if unit in dic.values():
            unit = key(dic=dic, val=unit)
        elif unit not in dic.keys():
            unit = kinfo().unit['def']
            print(f"Unit index invalid.  Setting to default ({unit}).")
        self.unit_idx = unit
        return unit

    def set_curr1(self, curr: float) -> None:
        """Set curr1 to curr."""
        info = self.info.curr1
        if not info['lim'][0] <= curr <= info['lim'][1]:
            curr = info['def']
            print(f"{info['txt'][self.meas_idx]}out of bounds ({info['lim']})."
                  + f"  Setting to default value ({curr:.2e} A).")
        self.curr1 = curr

    def set_curr2(self, curr: float) -> None:
        """Set curr2 to curr."""
        info = self.info.curr2
        if not info['lim'][0] <= curr <= info['lim'][1]:
            curr = info['def']
            print(f"{info['txt'][self.meas_idx]}out of bounds ({info['lim']})."
                  + f"  Setting to default value ({curr:.2e} A).")
        self.curr2 = curr

    def set_curr_step(self, num: float) -> None:
        """Overidden in daughter classes in which current step functions."""
        pass

    def set_curr_delta(self, num: float) -> None:
        """Overidden in daughter classes in which current delta functions."""
        pass

    # FIXME: Figure out what happens when overflow occurs b/c update_num_points
    def set_num_points(self, points: int) -> None:
        """Set the number of points for a measurement to points.

        Delta, pulse delta, and pulse delta log sweep measurements require the
        user to specify the number of points to measure.
        """
        info = self.info.points
        if points not in info['lim']:
            points = info['def']
            print(f"{info['txt']} out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({points}).")
        self.num_points = points

    def calc_num_points(self, start: float, stop: float, step: float) -> int:
        """Calculate the number of points in a staircase sweep."""
        # TODO: Verify this works with ZeroDivisionError and without
        try:
            out = (abs((stop - start) // step) + 1)
        except ZeroDivisionError:
            out = 1
        return out

    def set_num_sweeps(self, sweeps: int) -> None:
        """Overridden in daughter classes in that allow multiple sweeps."""
        pass

    @abstractmethod
    def set_meas_rate(self, rate: int) -> None:
        """Set integration rate or equivalent for 6221/2182A to rate.

        For differential conductance and delta measurements, this is the
        integration rate of the 2182a.  For pulse delta measurements, this is
        the cycle interval (or period) of the measurement.  Refer to the
        manuals for more information.
        """
        pass

    def set_meas_delay(self, delay: float) -> None:
        """Set the delay time between changing applied current and measurement.

        The delay time is a pause between when the 6221 applies a new current
        and when the 2182a measures a voltage, which gives the current time to
        settle.  num is in units of seconds.
        """
        info = self.info.delay
        if not info['lim'][0] <= delay <= info['lim'][1]:
            delay = info['def']
            print(f"{info['txt'][self.meas_idx]} out of bounds ({info['lim']})"
                  + f".  Setting to default value ({delay}).")
        self.meas_delay = delay

    def set_pulse_width(self, num: float) -> None:
        """Overridden in daughter classes that have pulse widths."""
        pass

    def set_low_meas(self, enable: bool) -> None:
        """Overridden in daughter classes that have a low measure option."""
        pass

    def set_filter_idx(self, idx: int) -> None:
        """Overridden in daughter classes that can specify the filter type."""
        pass

    def set_filter_on(self, enable: bool) -> None:
        """Enable or disable internal Keithley data filtering."""
        self.filter_on = enable

    def set_filter_window(self, wind: int) -> None:
        """Set the filter window to wind.

        Filter window is the percent deviation from the average that will not
        trigger starting a new filtering bin. Basically, the window tells the
        program what change in measurement it should consider a measurement of
        a different thing (e.g., applied current).
        """
        info = self.info.fwindow
        if not info['lim'][0] <= wind <= info['lim'][1]:
            wind = info['def']
            print(f"Filter window out of bounds. ([{info['lim'][0]}, "
                  + f"{info['lim'][1]}]).  Setting to default value ({wind}).")
        self.filter_window = wind
        return wind

    def set_filter_count(self, count: int) -> None:
        """Set the number of measurements to average to count."""
        info = self.info.fcount
        if count not in info['lim']:
            count = info['def']
            print(f"Filter count out of bounds ({info['lim']}).  Setting to "
                  + f"default value ({count}).")
        self.filter_count = count
        return count

    def get_total_points(self) -> None:
        """Overridden in daughter classes that have a number of sweeps."""
        return self.num_points

    def update_num_points(self) -> None:
        """Overridden in daughter classes for which this is important."""
        pass
