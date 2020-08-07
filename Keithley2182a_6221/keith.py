# -*- coding: utf-8 -*-
"""
keith contains the logic for Keithley 2182a/6221 control and operation.

classes_
    Keith: Contains logic for taking Keithley 4-probe transport measurements.

Part of the V3 Probe Station Collection.
@author: Sarah Friedensen
"""
# import inspect
from abcs.instrument_abc import Instrument
from Keithley2182a_6221.keith_meas_types import (Delta, DiffCon, PDelta,
                                                 PDeltaLog, PDeltaStair,
                                                 filter_switch, mlims)
from Keithley2182a_6221.keith_meas_abc import KeithMeasure
# import math
from Keithley2182a_6221.visa_keith import vKeith
from limits import (KeithInfo as info, DconInfo as dcinfo,
                    DeltaInfo as deltinfo, PDeltInfo as pdinfo,
                    PDeltStairInfo as pdsinfo, PDeltLogInfo as pdlinfo, ivinfo,
                    key)
import numpy
# import time
from typing import Union, Optional, Tuple

mu = u'\xb5'


class Keith(Instrument):
    """
    Contains/implements attributes and methods for controlling the Keithleys.

    Keith inherits from the Instrument abstract base class and is used as an
    inner class in ProbeGui.  It extends __init__ and set_address and overrides
    get_instr_type_str.

    attributes_
        source_range_type_switch: dict for relating source range type indices
            to their string representations and vice versa
        source_range_switch: dict for relating source range indices to their
            numerical ranges and vice versa
        source_range_minmax_switch: dict for relating source range indices to
            their maximum and minimum values in the UI in convenient display
            units
        source_range_mult_switch: dict for converting nA, uA, and mA (used in
            UI) to uA (used internally)
        source_range_txt_switch: dict for relating source range indices to
            their unit labels
        volt_range_switch: dict for relating voltmeter range indices to their
            numerical ranges in volts
        unit_switch: dict for relating unit indices to their YAML labels and
            vice versa
        filter_switch: dict for relating filter indices to their YAML labels
            and vice versa
        diffcon: instance of inner class DiffCon
        delta: instance of inner class Delta
        pdelta: instance of inner class PDelta
        pdelt_stair: instance of inner class PDeltaStair
        pdelt_log: instance of inner class PDeltaLog
        meas_type_switch: dict for relating measurement type indices to their
            associated inner class instances (for function calls, &c.)
        visa: instance of inner class vKeith for visa communications
        source_range_type_idx: index specifying which source range type to use
        source_range_idx: index specifying which source range to use
        volt_range_idx: index specifying which voltmeter range to use
        compl_volt: compliance voltage in V for 6221 source.
        compl_abort: whether to abort measurement if 6221 leaves compliance
        meas_type_idx: index specifying which type of Keithley measurement is
            being set up.  Along with meas_type_switch, will link to inner
            class instances.
        arm_switch: dict connecting measurement type indices to their
            associated arming commands

    methods_
        get_instr_type_str()
        meas_type(int)
        get_header_string(int)
        set_address(int)
        set_source_range_type(int or str)
        source_range_type()
        set_source_range(int/float/str)
        source_range(type)
        set_volt_range(int)
        volt_range(type)
        set_unit(int or str, optional int)
        unit(optional int)
        set_compl_volt(float)
        set_compl_abort(bool)
        set_meas_type(int or str)
        meas_type_txt()
        curr_conv_div(float)
        curr_conv_mult(float)
        set_curr1(float, optional int)
        set_curr2(float, optional int)
        set_curr_step(float, optional int)
        set_curr_delta(float, optional int)
        set_meas_rate(int or float, optional int)
        set_meas_delay(float, optional int)
        set_pulse_width(float, optional int)
        set_num_sweeps(int, optional int)
        set_low_meas(bool, optional int)
        set_num_points(int, optional int)
        update_num_points(optional int)
        set_filter_type(int or str, optional int)
        filter_type(optional int, optional int)
        filter_index(optional str, optional int)
        set_filter(bool, optional int)
        set_filter_window(float, optional int)
        set_filter_count(int, optional int)
        get_diffcon_arm()
        get_delta_arm()
        get_pdelta_arm()
        get_pdelt_stair_arm()
        get_pdelt_log_arm()
        arm()
        run()
        stop()
        get_data()
        source_range_text()
        curr1_text(optional int)
        curr2_text(optional int)
        field3_text(optional int)
        field4_text(optional int)
        source_range_minmax(optional int)
    """
    source_range_type_switch = {
            0: 'Best',
            1: 'Fixed',
            'Best': 0,
            'Fixed': 1}
    source_range_switch = {
            0: 2.00e-9,
            1: 20.00e-9,
            2: 200.00e-9,
            3: 2.00e-6,
            4: 20.00e-6,
            5: 200.00e-6,
            6: 2.00e-3,
            7: 20.00e-3,
            8: 100.00e-3,
            2.00e-9: 0,
            20.00e-9: 1,
            200.00e-9: 2,
            2.00e-6: 3,
            20.00e-6: 4,
            200.00e-6: 5,
            2.00e-3: 6,
            20.00e-3: 7,
            100.00e-3: 8,
            200.00: 200.00}
    source_range_minmax_switch = {
            0: 2.0,
            1: 20.0,
            2: 200.0,
            3: 2.0,
            4: 20.0,
            5: 200.0,
            6: 2.0,
            7: 20.0,
            8: 100.0}

    source_range_mult_switch = {
        # This converts to/from Amps from/to nA, uA, and mA
        -1: 1e-9,
        0: 1e-6,
        1: 1e-3}

    source_range_txt_switch = {
            0: '(nA)',
            1: '(nA)',
            2: '(nA)',
            3: f'({mu}A)',
            4: f'({mu}A)',
            5: f'({mu}A)',
            6: '(mA)',
            7: '(mA)',
            8: '(mA)'}

    volt_range_switch = {
            2: 10.0e-3,
            3: 100.0e-3,
            4: 1.0,
            5: 10.0,
            6: 100.0,
            10.0e-3: 2,
            100.0e-3: 3,
            1.0: 4,
            10.0: 5,
            100.0: 6}

    unit_switch = {
            0: 'volts',
            1: 'siemens',
            2: 'ohms',
            3: 'avgW',
            4: 'peakW',
            'volts': 0,
            'siemens': 1,
            'ohms': 2,
            'avgW': 3,
            'peakW': 4}

    meas_type_txt_switch = {
            0: 'diffCond',
            1: 'delta',
            2: 'pulseDelta',
            3: 'sweepPulseDeltaStair',
            4: 'sweepPulseDeltaLog',
            'diffCond': 0,
            'delta': 1,
            'pulseDelta': 2,
            'sweepPulseDeltaStair': 3,
            'sweepPulseDeltaLog': 4}

    def __init__(self) -> None:
        """Initialize instance of general Keithley control."""
        print('Keith.__init__ called.')
        super().__init__()
        self.diffcon = DiffCon()
        self.delta = Delta()
        self.pdelta = PDelta()
        self.pdelt_stair = PDeltaStair()
        self.pdelt_log = PDeltaLog()

        # FIXME: Make this the 'dic' entry of KeithInfo.meas
        info.meas['typ'] = {0: self.diffcon,
                            1: self.delta,
                            2: self.pdelta,
                            3: self.pdelt_stair,
                            4: self.pdelt_log}
        self.meas_typ_idx = info.meas['def']

        self.address = info.addr['def']
        self.visa = vKeith(self.address)

        self.source_range_type_idx = info.source_range_type['def']
        self.source_range_idx = info.source_range['def']
        self.volt_range_idx = info.volt_range['def'] - 2

        self.compl_volt = info.compl_volt['def']
        self.compl_abort = info.cab_def

        # FIXME: Just call this 'arm'
        self.arm_switch = {
                0: self.get_diffcon_arm,
                1: self.get_delta_arm,
                2: self.get_pdelta_arm,
                3: self.get_pdelt_stair_arm,
                4: self.get_pdelt_log_arm}

    def get_instr_type_str(self) -> str:
        """Return name of instrument setup plus a newline."""
        return 'Keithley 6221/218sa Current Source/Nanovoltmeter\n'

    def meas_type(self, idx: Optional[int] = None) -> KeithMeasure:
        # TODO: Verify KeithMeasure is correct output type.
        """Return measurement type class instance."""
        if idx is None:
            idx = self.meas_type_idx
        elif idx not in info.meas['mes'].keys():
            idx = info.meas['def']
            print("Measurement type index out of bounds.  Setting to default "
                  + f"measurement type ({info.meas['txt'][idx]})."
                  )
        print(type(self.meas_type_switch[idx]))
        return self.meas_type_switch[idx]

    def get_header_string(self, idx: Optional[int] = None) -> str:
        """Return header string for a measurement type.

        Basically, gather all relevant attributes for a measurement type
        (e.g., start current, measurement rate) and format them into something
        you could put at the top of a text file or csv so that you know what
        you did.
        """
        # TODO: Test, verify get_header_string
        meas = self.meas_type(idx)
        curr1 = self.curr1_text()
        curr2 = self.curr2_text()
        step = self.curr_step_text()
        delta = self.curr_delta_text()
        rate = meas.meas_rate_text
        delay = meas.meas_delay_text
        pulse_width = meas.pulse_width_text
        pulse_count = meas.pulse_count_text
        out = (meas.get_meas_type_str()
               + f'{curr1}{meas.curr1}\t'
               + f'{curr2}{meas.curr2}\t'
               + (f'{step}{meas.curr_step}\t' if step is not None else '')
               + (f'{delta}{meas.curr_delta}\t' if delta is not None else '')
               + f'{rate}{meas.meas_rate}\t'
               + f'{delay}{meas.meas_delay}\t'
               + (f'{pulse_width}{meas.pulse_width}\t'
                  if pulse_width is not None else '')
               + (f'{pulse_count}{meas.num_points}\n'
                  if pulse_count is not None else '\n')
               + 'Reading (V)\tTime (s)\tCurrent (A)\tAvg Rdg(V)\tPoint\n'
               )
        print(out)
        return out

    # %% General Variables Section

    def set_address(self, addr: int) -> None:
        """Set GPIB address of the stack, then check if connected."""
        if addr not in info.addr['lim']:
            addr = info.addr['def']
            print(f"Given address not in valid range [{info.addr['lim'][0]}, "
                  + f"{info.addr['lim'][1]}].  GPIB address set to "
                  + f"default ({addr}).")
        super().set_address(addr)
        self.visa.check_connected(addr)

    def set_source_range_type(self, value: Union[int, str]) -> int:
        """Set source_range_type_idx and then update the Keithleys.

        Returns source_range_type_idx in case it was fed a string and the
        caller wants the index.
        """
        # TODO: Test set_source_range_type str input
        dic = info.sour_range['typ']['dic']
        if value in dic.values():
            value = key(dic=dic, val=value)
        elif value not in dic.keys():
            value = info.sour_range['typ']['def']
            print("Source range type invalid.  Source range type set to "
                  + f"default ({value})")
        self.source_range_type_idx = value
        self.visa.set_source_range(meas_idx=self.meas_type_idx,
                                   auto=(not value),
                                   rang=self.source_range(float))
        return value

    def source_range_type(self) -> str:
        """Look up string for source_range_type.  Convenience function."""
        return info.sour_range['typ']['dic'][self.source_range_type_idx]

    def set_source_range(self, value: Union[int, float, str]) -> int:
        """Set source_range_idx to given value and update Keithleys.

        Returns source_range_idx in case input was a float or str.
        """
        # TODO: Test set_source_range str input
        dic = info.sour_range['dic']
        if (value in dic.values() or float(value) in dic.values()):
            value = key(dic=dic, val=float(value))
        elif value not in dic.keys():
            value = info.sour_range['def']
            print("Source range index out of bounds.  Source range set to "
                  + f"default value ({dic[value]}).")
        self.source_range_idx = value
        self.visa.set_source_range(meas_idx=self.meas_type_idx,
                                   auto=(not value),
                                   rang=self.source_range(float))
        return value

    def source_range(self, typ: type = float) -> Union[float, str]:
        """Return Keithley source range as either a float or a str."""
        # TODO: Test source_range
        out = info.sour_range['dic'][self.source_range_idx]
        if typ not in (float, str):
            print('Valid output type not given.  source_range: typ '
                  + 'must be either float or str (default is float).')
            typ = float
        else:
            return (out if typ is float else format(out, '.0e'))

    def set_volt_range(self, value: Union[int, float]) -> int:
        """Set index for voltmeter range and update Keithleys.

        The math determines whether the passed value is a range or the index
        for the range.  Returns volt_range_idx in case input was a float
        """
        # TODO: Verify set_volt_range actually works
        dic = info.volt_range['dic']
        print(f'volt range value = {value} and is int = {type(value) is int}')
        if value in dic.values():
            out = value
            value = key(dic=dic, val=value)
        else:
            if isinstance(value, int):
                value += 2
            if value not in dic.keys():
                value = info.volt_range['def']
                print("Voltmeter range index out of bounds.  Setting to "
                      + f"default ({dic[value]} V).")
            out = dic[value]
        self.volt_range_idx = value
        print(f"keith volt range idx = {value}")
        print(f"volt range = {out} V")
        self.visa.set_meter_range(out)
        return value

    def volt_range(self, typ: type = float) -> Union[float, str]:
        """Return Keithley voltmeter range as either float or str."""
        # TODO: Test volt_range exhaustively as well.
        out = info.volt_range['dic'][self.volt_range_idx]
#        out = num if int(num) > 0 else format(num, '.0e')
        if typ not in (float, str):
            typ = float
            print('Valid output type not given.  volt_rang: typ '
                  + 'must be either float or str (default is float).')
        else:
            return (out if typ is float else format(out, '.0e'))

    def set_unit(self, unit_val: Union[int, str],
                 meas_idx: Optional[int] = None) -> None:
        """Set the unit index for the measurement type and update Keithleys."""
        # TODO: Test set_unit
        dic = info.unit['dic']
        if unit_val in dic.values():
            unit_val = key(dic=dic, val=unit_val)
        elif unit_val not in dic.keys():
            unit_val = info.unit['def']
            print("Unit index out of bounds.  Setting to default "
                  + f"({dic[unit_val]}).")
        self.meas_type(meas_idx).set_unit_idx(unit_val)
        self.visa.set_unit(unit_val)

    def unit(self, meas_idx: Optional[int] = None) -> int:
        """Look up unit string for measurement index. Convenience function."""
        return info.unit['dic'][self.meas_type(meas_idx).unit_idx]

    def set_compl_volt(self, volt: float) -> None:
        """Set compliance voltage and update Keithleys."""
        lim = info.compl_volt['lim']
        if not lim[0] <= volt <= lim[1]:
            volt = info.compl_volt['def']
            print("Compliance voltage out of bounds.  Setting to default "
                  f"value ({volt} V).")
        self.compl_volt = volt
        self.visa.set_compliance_v(volt)

    def set_compl_abort(self, enable: bool) -> None:
        """Set compliance abort."""
        if not isinstance(enable, bool):
            enable = info.cab_default
            print("Setting for compliance abort not available. "
                  + f" Setting to default ({info.cab_default}).")
        self.compl_abort = enable

    def set_meas_type(self, value: Union[int, str]) -> KeithMeasure:
        """Set meas_typ_idx to index represented by value."""
        if value in info.meas['txt'].values():
            value = key(dic=info.meas['txt'], val=value)
        elif value not in info.meas['txt'].keys():
            value = info.meas['def']
            print("Measurement type index out of bounds.  Setting to default "
                  + f"value ({info.meas['txt'][value]}).")
        self.meas_type_idx = value
        return self.meas_type(value)

    def meas_type_txt(self) -> str:
        """Return str of measurement type.  Convenience function."""
        return info.meas['txt'].get(self.meas_type_idx, 'ERR')

    def curr_conv_mult(self, num: float) -> float:
        """Convert a number to Amps based on multiplication by source range."""
        val = numpy.log10(self.source_range_switch[self.source_range_idx])
        mult_idx = val // 3
        return num * self.source_range_mult_switch[mult_idx]

    def curr_conv_div(self, num: float) -> float:
        """Convert a number from Amps based on division by the source range."""
        val = numpy.log10(self.source_range_switch[self.source_range_idx])
        mult_idx = val // 3
        return num / self.source_range_mult_switch[mult_idx]

    # %% Measurement variables section

    def set_curr1(self, curr: float, meas_idx: Optional[int] = None) -> None:
        """Set curr1 of desired measurement type instance to curr in Amps."""
        self.meas_type(meas_idx).set_curr1(curr)

    def set_curr2(self, curr: float, meas_idx: Optional[int] = None) -> None:
        """Set curr2 of desired measurement type instance to curr in Amps."""
        self.meas_type(meas_idx).set_curr2(curr)

    def set_curr_step(self, curr: float,
                      meas_idx: Optional[int] = None) -> None:
        """Set curr_step of desired meas type instance to curr in Amps."""
        self.meas_type(meas_idx).set_curr_step(curr)

    def set_curr_delta(self, curr: float,
                       meas_idx: Optional[int] = None) -> None:
        """Set curr_delta of desired measurement type instance to curr in A."""
        self.meas_type(meas_idx).set_curr_delta(curr)

    def set_meas_rate(self, rate: Union[int, float],
                      meas_idx: Optional[int] = None) -> None:
        """Set meas_rate of desired meas type instance to rate."""
        self.meas_type(meas_idx).set_meas_rate(rate)

    def set_meas_delay(self, delay: float,
                       meas_idx: Optional[int] = None) -> None:
        """Set meas_delay of desired meas type instance to delay."""
        self.meas_type(meas_idx).set_meas_delay(delay)

    def set_pulse_width(self, width: float,
                        meas_idx: Optional[int] = None) -> None:
        """Set pulse_width of desired meas type instance to width."""
        self.meas_type(meas_idx).set_pulse_width(width)

    def set_num_sweeps(self, sweeps: int,
                       meas_idx: Optional[int] = None) -> None:
        """Set num_sweeps of desired meas type instance to sweeps."""
        self.meas_type(meas_idx).set_num_sweeps(sweeps)

    def set_low_meas(self, enable: bool,
                     meas_idx: Optional[int] = None) -> None:
        """Enable or disable low_meas for desired meas type instance."""
        self.meas_type(meas_idx).set_low_meas(enable)

    def set_num_points(self, points: int,
                       meas_idx: Optional[int] = None) -> None:
        """Set num_points of desired meas type instance to points."""
        self.meas_type(meas_idx).set_num_points(points)

    def update_num_points(self, meas_idx: Optional[int] = None) -> None:
        """Call update_num_points from desired meas type instance."""
        self.meas_type(meas_idx).update_num_points()

    # %% Filtering Section

    def set_filter_idx(self, ftype: Union[int, str],
                       meas_idx: Optional[int] = None) -> None:
        """Set filter_idx of meas type instance and update Keithleys."""
        findex = (ftype if isinstance(ftype, int)
                  else filter_switch[ftype])
        meas = self.meas_type(meas_idx)
        enable = meas.filter_on
        meas.set_filter_idx(findex)
        self.visa.set_filter_on(enable)
        self.visa.set_filter(enable)

    def filter_type(self, findex: Optional[Union[int, str]] = None,
                    meas_idx: Optional[int] = None) -> str:
        """Return str of filter type.  Convenience function."""
        if findex is None:
            findex = self.meas_type(meas_idx).filter_idx
        return filter_switch[findex] if isinstance(findex, int) else findex

    def filter_index(self, ftype: Optional[Union[int, str]] = None,
                     meas_idx: Optional[int] = None) -> int:
        """Return filter_idx.  Convenience function."""
        if ftype is None:
            ftype = self.meas_type(meas_idx).filter_type
        return filter_switch[ftype] if isinstance(ftype, str) else ftype

    def set_filter(self, enable: bool, meas_idx: Optional[int] = None) -> None:
        """Set filter_on of meas type to enable and update Keithleys."""
        self.meas_type(meas_idx).set_filter_on(enable)
        self.visa.set_filter_on(enable)
        self.visa.set_filter(enable)

    def set_filter_window(self, window: float,
                          meas_idx: Optional[int] = None) -> None:
        """Set filter_window of meas type to window and update Keithleys."""
        meas = self.meas_type(meas_idx)
        enable = meas.filter_on
        if not lims.filt_window[0] <= window <= lims.filt_window[1]:
            window = lims.filt_window_def
            print(f"Filter window out of bounds ([{lims.filt_window[0]}, "
                  + f"{lims.filt_window[1]}]).  Setting to default value "
                  + f"({lims.filt_window_def}).")
        meas.set_filter_window(window)
        self.visa.set_filter_window(window)
        self.visa.set_filter(enable)

    def set_filter_count(self, count: int,
                         meas_idx: Optional[int] = None) -> None:
        """Set filter_count of meas type to count and update Keithleys."""
        meas = self.meas_type(meas_idx)
        enable = meas.filter_on
        if not lims.filt_count[0] <= count <= lims.filt_count[1]:
            count = lims.filt_count_def
            print(f"Filter count out of bounds ([{lims.filt_count[0]}, "
                  + f"{lims.filt_count[1]}]).  Setting to default value "
                  + f"({lims.filt_count_def}).")
        meas.set_filter_count(count)
        self.visa.set_filter_count(count)
        self.visa.set_filter(enable)

    # %% Arming Section

    def get_diffcon_arm(self) -> str:
        """Retrieve Keithley differential conductance arming command."""
        start = self.diffcon.curr1
        stop = self.diffcon.curr2
        step = self.diffcon.curr_step
        delta = self.diffcon.curr_delta
        delay = self.diffcon.meas_delay
        points = self.diffcon.num_points
        CAB = self.compl_abort
        return self.visa.arm_diffcon(start, stop, step, delta, delay, points,
                                     CAB)

    def get_delta_arm(self) -> str:
        """Retrieve Keithley delta measurement arming command."""
        high = self.delta.curr1
        low = self.delta.curr2
        delay = self.delta.meas_delay
        count = self.delta.num_points
        CAB = self.compl_abort
        return self.visa.arm_delta(high, low, delay, count, CAB)

    def get_pdelta_arm(self) -> str:
        """Retrieve Keithley pulse delta measurement arming command."""
        high = self.pdelta.curr1
        low = self.pdelta.curr2
        width = self.pdelta.pulse_width
        delay = self.pdelta.meas_delay
        count = self.pdelta.num_points
        cycle_int = self.pdelta.cycle_int
        low_meas = self.pdelta.low_meas
        return self.visa.arm_pdelt(high, low, width, delay, count, cycle_int,
                                   low_meas)

    def get_pdelt_stair_arm(self) -> str:
        """Retrieve Keithley pulse delta staircase sweep arming command."""
        start = self.pdelt_stair.curr1
        stop = self.pdelt_stair.curr2
        step = self.pdelt_stair.curr_step
        delay = self.pdelt_stair.meas_delay
        width = self.pdelt_stair.pulse_width
        cycle_time = self.pdelt_stair.cycle_time
        points = self.pdelt_stair.num_points
        sweeps = self.pdelt_stair.num_sweeps
        low_meas = self.pdelt_stair.low_meas
        return self.visa.arm_pdelt_stair(start, stop, step, delay, width,
                                         cycle_time, points, sweeps, low_meas)

    def get_pdelt_log_arm(self) -> str:
        """Retrieve Keithley pulse delta log sweep arming command."""
        start = self.pdelt_log.curr1
        stop = self.pdelt_log.curr2
        points = self.pdelt_log.num_points
        delay = self.pdelt_log.meas_delay
        width = self.pdelt_log.pulse_width
        cycle_time = self.pdelt_log.cycle_time
        sweeps = self.pdelt_log.num_sweeps
        low_meas = self.pdelt_log.low_meas
        return self.visa.arm_pdelt_log(start, stop, points, delay, width,
                                       cycle_time, sweeps, low_meas)

    def arm(self) -> str:
        """Arm the Keithleys to perform a measurement."""
        cmd = f'{self.visa.format_cmd}{self.arm_switch[self.meas_type_idx]()}'
        # TODO: Test arming thoroughly.
        print(cmd)
        self.visa.write(cmd)
        print(f'armed = {self.visa.query(self.visa.qarm[self.meas_type_idx])}')
        return(self.visa.query(self.visa.qarm[self.meas_type_idx]))

    def run(self) -> tuple:
        """Tell the Keithleys to start a measurement."""
        self.visa.write(self.visa.abort_cmd)
        self.arm()
        self.visa.source.timeout = 10000
        self.visa.write('INIT:IMM')
        done = self.visa.query('*OPC?')
        print(f'done = {done}')
        # TODO: Determine if below is necessary
#        i = 0
#        while not done and i < 100:
#            done = self.visa.query('*OPC?')
#            time.sleep(2)
#            print(f'done = {done}')
        kout = self.get_data()
        self.stop()
        return kout

    def stop(self) -> None:
        """Tell the Keithleys to stop a measurement."""
        # BUG: Does not actually stop the measurement.  May need to futz w OPC.
        self.visa.write('SOUR:SWE:ABOR; CLE:IMM')
        print('Keithley stopped.')

    def get_data(self) -> Tuple[str, list, list]:
        """Retrieve data from the Keithleys and process into separate lists."""
        cols = 5
        outdelim = '\t'
        data_str = self.visa.query('TRAC:DATA?')
        data_list = data_str.split(',')
        items = len(data_list)
        data_rows = [data_list[j:j+cols] for j in range(0, items) if
                     not j % cols]
        sdata_rows = [outdelim.join([str(i) for i in j]) for j in data_rows]
        data_str = '\n'.join(j for j in sdata_rows)
        data_str = self.get_header_string() + data_str
        data_cols = [data_list[j::cols] for j in range(0, cols)]
        return (data_str, sdata_rows, data_cols)

    # %% UI Update Section

    def source_range_text(self) -> str:
        """Access the source range text conveniently."""
        return self.source_range_txt_switch.get(
                self.source_range_idx, 'ERR')

    def curr1_text(self, idx: Optional[int]) -> str:
        """Label curr1 in UI and headers."""
        return self.meas_type(idx).curr1_text + self.source_range_text()

    def curr2_text(self, idx: Optional[int]) -> str:
        """Label curr2 in UI and headers."""
        return self.meas_type(idx).curr2_text + self.source_range_text()

    def curr_step_text(self, idx: Optional[int]) -> str:
        """Label curr_step in UI and headers."""
        step = self.meas_type(idx).curr_step_text
        if step is not None:
            step += self.source_range_text()
        return step

    def field4_text(self, idx: Optional[int]) -> str:
        """Label field4 in UI and headers.  field4 changes with meas_type."""
        if idx is None:
            idx = self.meas_type_idx
        try:
            field4 = self.meas_type(idx).field4_text
        except AttributeError:
            field4 = None
        else:
            if idx == 0:
                field4 += self.source_range_text()
        return field4

    def source_range_minmax(self, idx: Optional[int] = None) -> float:
        """Retrieve minimum and maximum values for spinboxes in the UI."""
        return (self.source_range_minmax_switch[self.source_range_idx] if
                idx is None else self.source_range_minmax_switch[idx])
