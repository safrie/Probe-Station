# -*- coding: utf-8 -*-
"""
visa_temp contains definitions for VISA interaction with the LakeShore 336.

classes_
    vTemp: Creates and writes commands for controlling the temperature
        controller. Subclass of Visa.

Part of the V3 probe station collection
@author: Sarah Friedensen
"""

from abcs.visa_abc import Visa
from typing import Optional

BINT1 = (1, 2)


class vTemp(Visa):
    """Generate and write commands to the LakeShore 336.

    vTemp inherits from Visa and extends __init__, check_connected, write_cmd,
    and query_cmd.

    Output indices: 1 = radiation shield, 2 = stage.

    attributes_
        input_idx_switch: Dict connecting input type indices to their names.
        thermo: VISA resource for the temperature controller
        rad_setpt: String specifying temperature setpoint for rad shield
        rad_ramp: String for specifying rad shield ramp rate
        stage_setpt: String specifying temperature setpoint for stage
        stage_ramp: String specifying ramp rate for stage temperature

    methods_
        write(string)
        query(string)
        check_connected(int)
        set_ramp(bint+1, float)
        qramp(bint+1)
        set_setpt(bint+1, float)
        qsetpt(bint+1)
        qtemp(int)
        enable_output(bint+1, int, int)
        enable_heater(bint+1, int)
    """

    input_idx_switch = {
        0: None,
        1: 'A',
        2: 'B',
        3: 'C',
        4: 'D1',
        5: 'D2',
        6: 'D3',
        7: 'D4',
        8: 'D5'}

    def __init__(self, address) -> None:
        """Instantiate VISA control of LakeShore 336 Temperature Controller."""
        super().__init__()
        self.thermo = None
        self.check_connected(address)
        self.rad_setpt = ''
        self.stage_setpt = ''
        self.rad_ramp = ''
        self.stage_ramp = ''

    def write(self, cmd: str) -> None:
        """Extend visa_abc's write_cmd to write to this instrument."""
        if self.thermo is not None:
            super().write(self.thermo, cmd)
        else:
            print('No write--temperature controller not connected')

    def query(self, cmd: str) -> None:
        """Extend visa_abc's query_cmd to write to this instrument."""
        if self.thermo() is not None:
            return super().query(self.thermo, cmd)
        else:
            print('No query--temperature controller not connected.')

    def check_connected(self, gpib: int) -> None:
        """See if instrument in pyvisa instrument list. If so, open it."""
        thermo_list = [x for x in self.instruments
                       if (str(gpib) and 'GPIB') in x]
        if not thermo_list:
            self.thermo = None
        else:
            self.thermo = self.rm.open_resource(thermo_list[0])

    def set_ramp(self, out_idx: int, rate: float,
                 enable: Optional[bool] = True) -> None:
        """Specify a ramp setting for one of the two heaters.

        out_idx specifies the output the ramp applies to, and rate is the ramp
        rate in K/min. A rate of 0 will act as if the rate is infinite, and the
        output will try to get where it's going as fast as possible.
        """
        if out_idx not in (1, 2):
            print('set_ramp: out_idx must be 1 or 2.')
            return
        cmd = f'RAMP {out_idx}, {int(enable)}, {rate}'
        if out_idx == 1:
            self.rad_ramp = cmd
        else:
            self.stage_ramp = cmd
        self.write(cmd)

    def qramp(self, out_idx: int) -> str:
        """Query the 336 to determine ramp rate for specified output."""
        if out_idx not in (1, 2):
            print('query_ramp: out_idx must be 1 or 2.')
            return None
        cmd = f'RAMP? {out_idx}'
        out = self.query(cmd)
        return out

    def set_setpt(self, out_idx: int, temp: float) -> None:
        """Change output out_idx setpoint to value (in Kelvin)."""
        cmd = f'SETP {out_idx}, {temp}'
        if out_idx not in (1, 2):
            print('set_setpt: out_idx must be 1 or 2.')
            return
        if out_idx == 1:
            self.rad_setpt = cmd
        else:
            self.stage_setpt = cmd
        self.write(cmd)

    def qsetpt(self, out_idx: int) -> str:
        """Query the 336 for the output out_idx's setpoint in Kelvin."""
        if out_idx not in (1, 2):
            print('qsetpt: out_idx must be 1 or 2.')
            return None
        cmd = f'SETP? {out_idx}'
        out = self.query(cmd)
        return out

    def qtemp(self, in_idx: int) -> str:
        """Query temperature of speficied input and return value in Kelvin.

        This function accepts integers in [1, 8] and will look up proper label.
        """
        if in_idx not in range(1, 9):
            print('qtemp: in_idx must be in range(1, 9).')
            return None
        cmd = f'KRDG? {self.input_idx_switch[in_idx]}'
        out = self.query(cmd)
        return out

    def enable_output(self, out_idx: int, mode_idx: int) -> None:
        """Enable/disable temperature control and specify mode for an output.

        Modes: 0 = Off, 1 = Closed Loop PID, 2 = Zone, 3 = Open Loop,
        4 = Monitor Out, 5 = Warmup Supply. 'Off' is NOT for when you want to
        hold steady at a temperature.
        """
        if out_idx not in (1, 2):
            print('enable_output: out_idx must be 1 or 2.')
            return None
        if mode_idx not in range(0, 6):
            print('enable_output: mode_idx must be in range(0, 6).')
            return None
        in_idx = out_idx + 5
        cmd = f'OUTMODE {out_idx}, {mode_idx}, {in_idx}, 1'
        self.write(cmd)

    def enable_heater(self, out_idx: int, htr_idx: int) -> None:
        """Enable/disable heater output and set level.

        Heater modes: 0 = Off, 1 = Low, 2 = Medium, 3 = High.
        """
        if out_idx not in (1, 2):
            print('enable_heater: out_idx must be 1 or 2.')
            return None
        if htr_idx not in range(0, 4):
            print(f'ENABLE_HEATER: htr_idx must be in {range(0, 4)}.')
            return None
        cmd = f'RANGE {out_idx}, {htr_idx}'
        self.write(cmd)
