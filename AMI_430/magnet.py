# -*- coding: utf-8 -*-
"""
magnet contains the logic for controlling and operating the magnet.

classes_
    Mag: Contains logic for controlling magnetic field and configuring sweeps

Part of the V3 probe station collection.
@author: Sarah Friedensen
"""
from abcs.instrument_abc import Instrument
from AMI_430.visa_mag import vMag as visa
from limits import MagInfo as info
from typing import Optional, Union
from pathlib import Path


class Mag(Instrument):
    """Contains the logic for controlling the magnet power supply programmer.

    Mag inherits from the Instrument abstract base class and is used as an
    inner class in ProbeGui.  It extends __init__ and set_address and overrides
    get_instr_type_str.

    attributes_
        address: Integer COM addres of the magnet power supply programmer
        visa: Visa resource for the magnet power supply programmer
        target: Target field or current to set the magnet to
        ramp_segments: Number of ramp segments for the magnet
        setpoints_list: List of magnet setpoints
        setpoints_text: Comma delimited listing of magnet setpoints
        ramps_list: list of magnet ramp rates
        ramps_text: Comma delimited listing of magnet ramp rates
        quench_detect: Bool indicating if automatic quench detection enabled.
            Based on current decrease rate, not a temperature.
        volt_limit: Voltage output limit for the power supply
        curr_limit: Current output limit for the power supply
        zero: Boolean for whether magnet should ramp to zero
        field_unit_idx: Index for which field unit to use
        time_unit_idx: Index for which time unit to use
        setpoints_label: UI label for the setpoints button
        ramp_label: UI label for the ramp rates button
        target_label: UI label for the target field spinbox
        calibration_file: Filename for calibration file
        calibration_path: Path object for calibration file

    methods_
        __init__()
        get_instr_type_str()
        set_address(int)
        set_ramp_segments(int)
        ramp_segments()
        set_setpoints_list(list)
        set_setpoints_text(str)
        set_ramps_list(list)
        set_ramps_text(str)
        set_quench_detect(bool)
        set_volt_limit(float)
        set_curr_limit(float)
        set_zero(bool)
        set_field_unit(int or str)
        field_unit(optional str)
        set_time_unit(bint or str)
        time_unit(optional str)
    """

    def __init__(self) -> None:
        """Instantiate magnet power supply control."""
        super().__init__('Mag')
        self.address = info.addr['def']
        self.visa = visa(self.address)
        self.field_unit_idx = info.field['unit']['def']
        self.time_unit_idx = info.time['unit']['def']
        self.target = info.field['def'][self.field_unit_idx]
        self.ramp_segments = info.seg['def']
        self.setpoints_list = []
        self.setpoints_text = None
        self.ramps_list = []
        self.ramps_text = None
        self.volt_limit = info.volt['def']
        self.curr_limit = info.curr['def']
        self.zero = None
        self.calibration_file = None
        self.quench_detect = None

    def get_instr_type_str(self) -> str:
        """Return a string describing this instrument."""
        return 'AMI Model 430 Power Supply Programmer\n'

    def set_address(self, addr: int) -> None:
        """Set COM address of magnet and check connection."""
        # TODO: Test set_address
        addr = super().set_address(addr)
        self.visa.check_connected(addr)
        return addr

    def set_target(self, targ: float) -> None:
        """Set the target magnetic field or current."""
        # TODO: Test set_target()
        fidx, unit = self.field_unit_idx, self.field_unit('Abbv')
        inf = info.field
        if abs(targ) > inf['lim'][fidx]:
            targ = inf['def'][fidx]
            print(f"Target out of bounds. |targ| must be < {inf['lim'][fidx]}"
                  + f"{unit}.  Target set to {targ} {unit}")
        self.target = targ
        return targ

    def set_ramp_segments(self, segs: int) -> None:
        """Set number of ramp segments for magnet range."""
        # TODO: Test set_ramp_segments
        if segs not in range(lims.seg[1], 0, -1):
            segs = lims.seg_default
            print(f"Number of segments must be between 1 and {lims.seg[1]}.  "
                  + f"Segments set to {lims.seg_default}.")
        self.ramp_segments = segs
        self.visa.set_ramp_segs(segs)
        return segs

    def set_setpoints_list(self, setpts: list) -> bool:
        """Set the list of magnet setpoints to setpts, return validation flag.

        These are the ramp interval upper bounds.
        """
        # TODO: Test set_setpoints_list
        bound = lims.field[self.field_unit_idx]
        setpts.sort()
        if len(setpts) not in range(lims.seg[1], 0, -1):
            print("Number of ramp segments must be between 1 and "
                  + f"{lims.seg[1]}.  Please try again.")
            setpts = []
        if abs(setpts[0]) > bound or abs(setpts[-1]) > bound:
            print(f"Magnet ramp setpoints must be within [{-bound}, {bound}]."
                  + "  Please try again.")
            setpts = []
        self.setpoints_list = setpts
        return setpts

    def set_setpoints_text(self, setpts: str) -> None:
        """Set the setpoints string listing to setpts.

        These are the ramp interval upper bounds.
        """
        # TODO: Test set_setpoints_text
        bound = lims.field[self.field_unit_idx]
        setpts.sort()
        if len(setpts) not in range(lims.seg[1], 0, -1):
            print("Number of ramp segments must be between 1 and"
                  + f"{lims.seg[1]}.  Please try again.")
            setpts = ''
        if abs(float(setpts[0])) > bound or abs(float(setpts[-1])) > bound:
            print(f"Magnet ramp setpoints must be within [{-bound}, {bound}]."
                  + "  Please try again.")
            setpts = ''
        self.setpoints_text = setpts
        return setpts

    def set_ramps_list(self, ramps: list) -> bool:
        """Set list of magnet ramp rates to ramps, return validation flag."""
        # TODO: Test set_ramps_list
        fidx, fabbv = self.field_unit_idx, self.field_unit['Abbv']
        tunit, tabbv = self.time_unit['Full'], self.time_unit['Abbv']
        bounds = lims.rate[tunit][fidx]
        ramps.sort()
        if len(ramps) not in range(lims.seg[1], 0, -1):
            print("Number of ramp segments must be between 1 and "
                  + f"{lims.seg[1]}.  Please try again.")
            ramps = []
        if ramps[0] < bounds[0] or ramps[-1] > bounds[1]:
            print(f"Ramp rates must be between {bounds[0]} {fabbv}/{tabbv} "
                  + f"and {bounds[1]} {fabbv}/{tabbv}.  Please try again.")
            ramps = []
        self.ramps_list = ramps
        return ramps

    def set_ramps_text(self, ramps: str) -> None:
        """Set the ramps string listing to ramps."""
        # TODO: Test set_ramps_text
        fidx, fabbv = self.field_unit_idx, self.field_unit['Abbv']
        tunit, tabbv = self.time_unit['Full'], self.time_unit['Abbv']
        bounds = lims.rate[tunit][fidx]
        ramps.sort()
        if len(ramps) not in range(lims.seg[1], 0, -1):
            print("Number of ramp segments must be between 1 and "
                  + f"{lims.seg[1]}.  Please try again")
            ramps = ''
        if float(ramps[0]) < bounds[0] or float(ramps[-1]) > bounds[1]:
            print(f"Ramp rates must be between {bounds[0]} {fabbv}/{tabbv} "
                  + f"and {bounds[1]} {fabbv}/{tabbv}.  Please try again.")
            ramps = ''
        self.ramps_text = ramps
        return ramps

    def set_quench_detect(self, enable: bool) -> None:
        """Enable/disable automatic quench detection.

        Automatic quench detection is performed by the magnet power supply
        programmer and is based on magnet current decrease rate and not
        temperature.
        """
        # TODO: Test set_quench_detect
        self.quench_detect = enable
        self.visa.set_quench_det(enable)

#    def set_quench_temp(self, temp: float) -> None:
#        """Set magnet quench temperature.
#
#        This is the temperature at which THE SOFTWARE will assert a quench.
#        """
#        self.quench_temp = temp

    def set_volt_limit(self, limit: float) -> None:
        """Set the voltage output limit in V for the magnet."""
        # TODO: Test set_volt_limit
        if not lims.volt[0] <= limit <= lims.volt[1]:
            limit = lims.volt_default
            print("Magnet voltage limit must be between "
                  + f"{lims.volt[0]} and {lims.volt[1]}.  Value set to "
                  + f"{lims.volt_default} V.")
        self.volt_limit = limit
        self.visa.set_volt_lim(limit)
        return limit

    def set_curr_limit(self, limit: float) -> None:
        """Set the current output limit in A for the magnet."""
        # TODO: Test set_curr_limit
        if not lims.curr[0] <= limit <= lims.curr[1]:
            limit = lims.curr_default
            print("Magnet current must be between "
                  + f"{lims.curr[0]} and {lims.curr[1]}.  Value set to "
                  + f"{lims.curr_default} A.")
        self.curr_limit = limit
        self.visa.set_curr_lim(limit)
        return limit

    def set_zero(self, enable: bool) -> None:
        """Start/stop magnet zeroing."""
        # TODO: Implement visa.
        self.zero = enable

    def set_calibration_file(self, calib: str) -> None:
        # TODO: Test and complete set_calibration_file
        """Set the magnet calibration file."""
        self.calibration_file = calib
        self.calibration_path = Path(calib)
        # TODO: VISA implementation

    def set_field_unit(self, unit_val: Union[int, str]) -> None:
        """Set unit for magnetic field and update magnet."""
        # TODO: Test set_field_unit
        index = (unit_val if unit_val in (0, 1, 2)
                 else self.field_unit_switch['Full'].get(
                     unit_val, lims.field_unit_default[1]) if len(unit_val) > 2
                 else self.field_unit_switch['Abbv'].get(
                     unit_val, lims.field_unit_default[2])
                 )
        if index < 2:
            self.visa.set_field_unit(index)
        self.field_unit_idx = index
        return index

    def field_unit(self, form: Optional[str] = 'Full') -> str:
        """Look up the unit string for field unit.

        form can be either 'full' or 'abbv', with any case.
        """
        # TODO: Test field_unit
        valid = ('full', 'abbv')
        if form.lower() not in valid:
            print(f'field_unit form must be in {valid}.')
        else:
            return self.field_unit_switch[form.capitalize()][
                    self.field_unit_idx]

    def set_time_unit(self, unit_val: Union[int, str]) -> None:
        """Set unit for time and update magnet."""
        # TODO: Test set_time_unit
        index = (unit_val if unit_val in (0, 1)
                 else self.time_unit_switch['Full'].get(
                     unit_val, lims.time_unit_default[1]) if len(unit_val) > 3
                 else self.time_unit_switch['Abbv'].get(
                     unit_val, lims.time_unit_default[2])
                 )
        self.visa.set_time_unit(index)
        self.time_unit_idx = index
        return index

    def time_unit(self, form: Optional[str] = 'full') -> str:
        """Look up the unit string for time unit.

        form can be either 'full' or 'abbv', with any case.
        """
        # TODO: Test time_unit
        valid = ('full', 'abbv')
        if form.lower() not in valid:
            raise ValueError(f'time_unit: form must be in {valid}.')
        else:
            return self.time_unit_switch[form][self.time_unit_idx]

    def set_pars(self) -> None:
        # TODO: Test set_pars.
        """Send parameters to the AMI 430 but do not start ramping."""
        self.visa = visa
        if self.field_unit('Abbv') == 'A':
            visa.set_targ_curr(self.target)
            # unit = 'curr'
        else:
            visa.set_targ_field(self.target)
            # unit = 'field'
        visa.set_ramp_segs(self.ramp_segments)
        for i in range(0, self.ramp_segments):
            visa.set_rate(seg=i, rate=self.ramps_list[i],
                          upbound=self.setpoints_list[i])
