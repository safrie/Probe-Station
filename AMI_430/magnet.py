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
from limits import MagInfo as info, key as key
from typing import Optional, Union, Tuple
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
            print(f"Target out of bounds. |targ| must be < "
                  f"{inf['lim'][fidx]}{unit}.  Target set to {targ} {unit}")
        self.target = targ
        return targ

    def set_ramp_segments(self, segs: int) -> None:
        """Set number of ramp segments for magnet range."""
        # TODO: Test set_ramp_segments
        if segs not in info.seg['lim']:
            segs = info.seg['def']
            print(f"Number of segments must be in {info.seg['lim']}.  "
                  + f"Segments set to default ({segs}).")
        self.ramp_segments = segs
        self.visa.set_ramp_segs(segs)
        return segs

    def set_setpoints(self, stpts: Union[list, str]) -> Tuple:
        """Set the list of magnet setpoints to setpts, return list or str.

        These are the ramp interval upper bounds.
        """
        # TODO: Test set_setpoints
        lim = info.field['lim'][self.field_unit_idx]
        if isinstance(stpts, str):
            stpts = [float(x) for x in stpts.split(', ')]
        if len(stpts) not in info.seg['lim']:
            print("Number of ramp segments must be in {info.seg['lim']}.  "
                  + "Please try again.")
            stpts = []
        else:
            for i in range(0, len(stpts)):
                if abs(stpts[i]) > lim:
                    print(f"Magnet ramp setpoints must be within "
                          f"[{-lim}, {lim}].  Please try again.")
                    stpts = []
                    break
        self.setpoints_text = str(stpts).strip('[]')
        self.setpoints_list = stpts
        return (stpts, self.setpoints_text)

    def set_ramps(self, ramps: Union[list, str]) -> Tuple:
        """Set list of magnet ramp rates to ramps, return tuple of values."""
        # TODO: Test set_ramps
        fidx, fabbv = self.field_unit_idx, self.field_unit['Abbv']
        tunit, tabbv = self.time_unit['Full'], self.time_unit['Abbv']
        bounds = info.rate['lim'][tunit][fidx]
        if isinstance(ramps, str):
            ramps = [float(x) for x in ramps.split(', ')]
        if len(ramps) not in info.seg['lim']:
            print(f"Number of ramp segments must be in {info.seg['lim']}.  "
                  + "Please try again.")
            ramps = []
        else:
            for i in range(0, len(ramps)):
                if ramps[i] < bounds[0] or ramps[i] > bounds[1]:
                    print(f"Ramp rates must be between {bounds[0]} {fabbv}/"
                          + f"{tabbv} and {bounds[1]} {fabbv}/{tabbv}.  "
                          + "Please try again.")
                    ramps = []
                    break
        self.ramps_list = ramps
        self.ramps_text = str(ramps).strip('[]')
        return (ramps, self.ramps_text)

    def query_rate(self, seg: int) -> str:
        """Return ramp rate and upper bound for segment seg.

        This method wraps vMag.qrate in order to apply input validation."""
        typ = self.field_type()
        if seg not in info.seg['lim']:
            print("Segment number out of bounds.  Please fix and try again.")
            return
        return self.visa.qrate(seg, typ)

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
        if not info.volt['lim'][0] <= limit <= info.volt['lim'][1]:
            limit = info.volt['def']
            print(f"Magnet voltage limit must be within {info.volt['lim']}."
                  + f"Value set to {info.volt['def']} V.")
        self.volt_limit = limit
        self.visa.set_volt_lim(limit)
        return limit

    def set_curr_limit(self, limit: float) -> None:
        """Set the current output limit in A for the magnet."""
        # TODO: Test set_curr_limit
        if not info.curr['lim'][0] <= limit <= info.curr['lim'][1]:
            limit = info.curr['def']
            print(f"Magnet current must be within {info.curr['lim'][0]}.  "
                  f"Value set to {info.curr['def']} A.")
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
        inf = info.field['unit']
        index = (unit_val if unit_val in (0, 1, 2)
                 else key(dic=inf['Full'], val=unit_val) if len(unit_val) > 2
                 else key(dic=inf['Abbv'], val=unit_val)
                 )
        if index is None:
            index = inf['def']
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
            return info.field['unit'][form.capitalize()][self.field_unit_idx]

    def field_type(self) -> str:
        """Look up the field type string for the field unit."""
        return info.field['unit']['typ'][self.field_unit_idx]

    def set_time_unit(self, unit_val: Union[int, str]) -> None:
        """Set unit for time and update magnet."""
        # TODO: Test set_time_unit
        inf = info.time['unit']
        index = (unit_val if unit_val in (0, 1)
                 else key(dic=inf['Full'], val=unit_val) if len(unit_val) > 3
                 else key(dic=inf['Abbv'], val=unit_val)
                 )
        if index is None:
            index = inf['def']
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
            print(f'time_unit: form must be in {valid}.')
        else:
            return info.time['unit'][form.capitalize()][self.time_unit_idx]

    def set_pars(self) -> None:
        # TODO: Test set_pars.
        """Send parameters to the AMI 430 but do not start ramping."""
        self.visa = visa
        if self.field_unit_idx == 2:
            visa.set_targ_curr(self.target)  # Magnet unit is Amps
        else:
            visa.set_targ_field(self.target)  # Magnet unit is kG or Tesla
        visa.set_ramp_segs(self.ramp_segments)
        for i in range(0, self.ramp_segments):
            visa.set_rate(seg=i, rate=self.ramps_list[i],
                          upbound=self.setpoints_list[i])
