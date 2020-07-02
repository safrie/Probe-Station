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
from typing import Optional, Union
from pathlib import Path


class Mag(Instrument):
    """Contains the logic for controlling the magnet power supply programmer.

    Mag inherits from the Instrument abstract base class and is used as an
    inner class in ProbeGui.  It extends __init__ and set_address and overrides
    get_instr_type_str.

    attributes_
        field_unit_switch: Dict for converting between unit indices and units.
        time_unit_switch: Dict for converting between unit indices and units.
        field_upper_limit: Dict for field limit in different units.
        ramp_upper_limit: Dict for ramp rate limit in different units
        setpoints_title: Label for setpoints dialog box
        ramp_title: Label for ramp rates dialog box
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

    field_unit_switch = {'Full': {0: 'Kilogauss',
                                  1: 'Tesla',
                                  2: 'Amps',
                                  'Kilogauss': 0,
                                  'Tesla': 1,
                                  'Amps': 2,
                                  'A': 'Amps',
                                  'T': 'Tesla',
                                  'kG': 'Kilogauss'},
                         'Abbv': {0: 'kG',
                                  1: 'T',
                                  2: 'A',
                                  'kG': 0,
                                  'T': 1,
                                  'A': 2,
                                  'Amps': 'A',
                                  'Tesla': 'T',
                                  'Kilogauss': 'kG'}
                         }
    time_unit_switch = {
            'Full': {0: 'Seconds',
                     1: 'Minutes',
                     2: 'second',
                     3: 'minute',
                     'Seconds': 0,
                     'Minutes': 1,
                     's': 'Seconds',
                     'min': 'Minutes'},
            'Abbv': {0: 's',
                     1: 'min',
                     's': 0,
                     'min': 1,
                     'Seconds': 's',
                     'Minutes': 'min'}
            }

    # TODO: put in correct values for field_upper_limit
    field_upper_limit = {0: 30,
                         1: 3,
                         2: 'limit in A'}

    # TODO: put in correct values for ramp_upper_limit
    ramp_upper_limit = {'seconds': {0: 'limit in kG/s',
                                    1: 'limit in T/s',
                                    2: 'limit in A/s'},
                        'minutes': {0: 'limit in kG/min',
                                    1: 'limit in T/min',
                                    2: 'limit in A/min'}
                        }
    setpoints_title = 'Magnetic Field Setpoints'
    ramp_title = 'Magnetic Field Ramp Rates'
    target_label = 'Target Magnet'
    setpoints_label = 'Ramp Setpoints '
    ramps_label = 'Ramp Rates '

    def __init__(self) -> None:
        """Instantiate magnet power supply control."""
        super().__init__()
        self.address = 2
        self.visa = visa(self.address)
        self.target = 0
        self.ramp_segments = None
        self.setpoints_list = []
        self.setpoints_text = None
        self.ramps_list = []
        self.ramps_text = None
        self.quench_detect = None
        self.volt_limit = None
        self.curr_limit = None
        self.zero = None
        self.field_unit_idx = 1
        self.time_unit_idx = 0
        self.calibration_file = None

    def get_instr_type_str(self) -> str:
        """Return a string describing this instrument."""
        return 'AMI Model 430 Power Supply Programmer\n'

    def set_address(self, addr: int) -> None:
        """Set COM address of magnet and check connection."""
        super().set_address(addr)
        self.visa.check_connected(addr)

    def set_target(self, targ: float) -> None:
        """Set the target magnetic field or current."""
        self.target = targ

    def set_ramp_segments(self, segs: int) -> None:
        """Set number of ramp segments for magnet range."""
        # TODO: Test set_ramp_segments
        if int < 0:
            raise ValueError('set_ramp_segments: segs must be positive.')
        else:
            self.ramp_segments = segs
            self.visa.set_ramp_segs(segs)

    def set_setpoints_list(self, setpts: list) -> None:
        """Set the list of magnet setpoints to setpts.

        These are the ramp interval upper bounds.
        """
        self.setpoints_list = setpts

    def set_setpoints_text(self, setpts: str) -> None:
        """Set the setpoints string listing to setpts.

        These are the ramp interval upper bounds.
        """
        self.setpoints_text = setpts

    def set_ramps_list(self, ramps: list) -> None:
        """Set the list of magnet ramp rates to ramps."""
        # TODO: Verify the length requirement for set_ramps_list
        self.ramps_list = ramps

    def set_ramps_text(self, ramps: str) -> None:
        """Set the ramps string listing to ramps."""
        # TODO: Verify the length requirement for set_ramps_text
        self.ramps_text = ramps

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
        self.volt_limit = limit
        self.visa.set_volt_lim(limit)

    def set_curr_limit(self, limit: float) -> None:
        """Set the current output limit in A for the magnet."""
        # TODO: Test set_curr_limit
        self.curr_limit = limit
        self.visa.set_curr_lim(limit)

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
        index = (unit_val if isinstance(unit_val, int)
                 else self.field_unit_switch['Full'][unit_val]
                 if len(unit_val) > 2
                 else self.field_unit_switch['Abbv'][unit_val])
        if index < 2:
            self.visa.set_field_unit(index)
        self.field_unit_idx = index

    def field_unit(self, form: Optional[str] = 'Full') -> str:
        """Look up the unit string for field unit.

        form can be either 'full' or 'abbv', with any case.
        """
        # TODO: Test field_unit
        valid = ('full', 'abbv')
        if form.lower() not in valid:
            raise ValueError(f'field_unit: form must be in {valid}.')
        else:
            return self.field_unit_switch[form.capitalize()][
                    self.field_unit_idx]

    def set_time_unit(self, unit_val: Union[int, str]) -> None:
        """Set unit for time and update magnet."""
        # TODO: Test set_time_unit
        index = (unit_val if isinstance(unit_val, int)
                 else self.time_unit_switch['Full'][unit_val]
                 if len(unit_val) > 3
                 else self.time_unit_switch['Abbv'][unit_val])
        self.visa.set_time_unit(index)
        self.time_unit_idx = index

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
