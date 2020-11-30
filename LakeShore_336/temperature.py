# -*- coding: utf-8 -*-
"""
temperature.py contains logic for operating the LakeShore 336 controller.

classes_
    Temp: Contains logic for controlling heaters and measuring temperature.

Part of the V3 Probe Station Collection.
@author: Sarah Friedensen
"""

from abcs.instrument_abc import Instrument
import LakeShore_336.visa_temp as visa
import time
from typing import Union, Tuple
from limits import TempInfo as info, key


class Temp(Instrument):
    """
    Contains/implements attributes and methods for operating the LakeShore 336.

    Temp inherits from the Instrument abstract base class and is used as an
    inner class in ProbeGUI.  It extends __init-- and set_address and overrides
    get_instr_type_str.

    attributes_
        rad_control: bool for whether to control rad shield heaters
        rad_setpoint: temperature setpoint in K for rad shield
        rad_ramp: ramp rate in K/minute for rad shield
        rad_power: Power setting for rad shield heater
        stage_control: bool for whether to control stage heater
        stage_setpoint: temperature setpoint in K for stage
        stage_ramp: ramp rate in K/minute for stage
        stage_power: Power setting for stage heater
        address: GPIB address for the LakeShore 336
        to_measure_idx: bool index for whether to measure controlled/all temps
        to_measure_str: label indicating if measuring controlled or all temps
        visa: Visa Instrument Resource for the LakeShore 336
        data: list of temperature data

    methods_
        __init__()
        get_instr_type_str()
        set_address(int)
        set_rad_control(bool)
        set_stage_control(bool)
        set_setpoint(float, str)
        set_ramp(float, str)
        set_power(int, str)
        set_to_measure(bint or str)
        measure()
        ramp_status(int)
        set_pars()
        run()
        stop()
        warm()
        process_data(list)
    """

    def __init__(self) -> None:
        """Initialize the LakeShore 336 and open visa communications."""
        super().__init__('Temp')
        self.rad_control = info.rad_cont['def']
        self.rad_setpoint = info.setpt['def']
        self.rad_ramp = info.rate['def']
        self.rad_power = info.power['def']
        self.stage_control = info.stage_cont['def']
        self.stage_setpoint = info.setpt['def']
        self.stage_ramp = info.rate['def']
        self.stage_power = info.power['def']
        self.address = info.addr['def']
        self.to_measure_idx = info.to_measure['def']
        self.to_measure_str = info.to_measure['dic'][self.to_measure_idx]
        self.outnames = (j for i in info.out.name.values() for j in i)
        self.visa = visa.vTemp(self.address)
        self.running = False

    def get_instr_type_str(self) -> str:
        """Return a string identifying the instrument."""
        return 'LakeShore Model 336 Temperature Controller\n'

    def set_address(self, addr: int) -> None:
        """Set GPIB address of 336, then check it's connected."""
        # TODO: Test set_address
        addr = super().set_address(addr)
        self.visa.check_connected(addr)
        return addr

    def set_rad_control(self, enable: bool) -> None:
        # TODO: Test set_rad_control
        """Toggle whether or not to control rad shield temperature."""
        self.rad_control = enable

    def set_stage_control(self, enable: bool) -> None:
        # TODO: Test set_stage_control
        """Toggle whether or not to control the stage temperature."""
        self.stage_control = enable

    def set_setpoint(self, temp: float, output: str = 'stage') -> None:
        # TODO: Test set_setpoint
        """Set temperature target for either stage or rad shield in Kelvin."""
        valid = self.outnames
        if output not in valid:
            print(f'set_setpoint: output must be in {valid}. Please try again')
            return
        if not info.setpt['lim'][0] <= temp <= info.setpt['lim'][1]:
            temp = info.setpt['def']
            print("Temperature setpoint not in valid range.  Setting to "
                  + f"default value instead ({temp} K).")
        if output in info.out.name[1]:
            self.rad_setpoint = temp
        else:
            self.stage_setpoint = temp
        return temp

    def set_ramp(self, rate: float, output: str) -> None:
        # TODO: Test set_ramp
        """Set the ramp rate for either stage or rad shield in Kelvin/sec."""
        valid = self.outnames
        lim = info.rate['lim']
        if output not in valid:
            print(f'Output must be in {valid}.  Please try again.')
            return
        if not (lim[0] <= rate <= lim[1] or rate == lim[2]):
            rate = info.rate['def']
            print(f"Ramp rate must be within [{lim[0]}, {lim[1]}] or equal to "
                  + f"{lim[2]}.  Setting to default value ({rate}).")
        if output in info.out.name[1]:
            self.rad_ramp = rate
        else:
            self.stage_ramp = rate
        return rate

    def set_power(self, power: int, output: str = 'stage') -> None:
        # TODO: Test set_power
        """Set internal heater power variable for stage or rad shield."""
        valid = self.outnames
        if output not in valid:
            print(f'Output must be in {valid}.  Please try again.')
            return
        if power not in info.power['lim']:
            power = info.power['def']
            print(f"Heater power must be in {list(info.power['lim'])}.  "
                  + f"Setting to default heater power ({power}).")
        if output in info.out.name[1]:
            self.rad_power = power
        else:
            self.stage_power = power
        return power

    def set_to_measure(self, measured: Union[int, str]) -> None:
        # TODO: Test set_to_measure
        """Set whether to measure only rad shield and stage or all temps."""
        if measured in info.to_measure['dic'].values():
            measured = key(measured)
        elif measured not in info.to_measure['dic'].keys():
            measured = info.to_measure['def']
            print("Argument for temperatures to measure must be in "
                  + f"{info.to_measure['dic']}.  Setting to default value "
                  + f"({measured}, {info.to_measure['dic'][measured]}).")
        self.to_measure_idx = measured
        self.to_measure_str = info.to_measure['dic'][measured]
        return measured

    def measure(self, t0: float) -> float:
        # TODO: Test measure
        """Collect a single set of temperature measurements.

        t0 is the initial time from which the elapsed time will be calculated.
        """
        inputs = list(range(1, 9)) if self.to_measure_idx else [6, 7]
        outT = [self.visa.query_temp(i)[1:-2] for i in inputs]
        return outT + [time.monotonic() - t0]

    def ramp_status(self, output: int) -> int:
        """Query the ramp status of the specified output."""
        return int(self.visa.query(f'RAMPST? {output}'))

    def set_pars(self) -> None:
        # TODO: Test set_pars
        """Send all VISA parameters to the 336 but do not enable output."""
        self.visa.set_ramp(1, self.rad_ramp, enable=int(self.rad_control))
        self.visa.set_setpt(1, self.rad_setpoint)

        self.visa.set_ramp(2, self.stage_ramp, enable=int(self.stage_control))
        self.visa.set_setpt(2, self.stage_setpoint)

    def run(self, wait: float) -> str:
        # TODO: Test run and rewrite to allow interrupt
        """Adjust to the target temperature(s) and take data.

        wait is the length of time in seconds to wait between measurements.
        """
        print('Temperature control running.')
        data = []
        self.set()

        self.visa.enable_output(1, int(self.rad_control))
        self.visa.enable_heater(1, self.rad_power)

        self.visa.enable_output(2, int(self.stage_control))
        self.visa.enable_heater(2, self.stage_power)

        self.running = True
        t0 = time.monotonic()
        while self.running:
            data += [self.measure(t0)]
            test_rad = (self.ramp_status(1) if self.rad_control else 0)
            test_stage = (self.ramp_status(2) if self.stage_control else 0)
            self.running = ((bool(test_rad) or bool(test_stage))
                            and self.running)
            if self.running:
                time.sleep(wait)
        self.stop()
        self.data = self.process_data(data)
        return self.data

    def stop(self) -> None:
        # TODO: Test stop
        """Halt ramp and hold temperature."""
        print('Temperature control stopped.')
        self.running = False
        if self.rad_control:
            self.visa.set_ramp(1, 0, 0)
            self.visa.enable_heater(1, 1)
            self.visa.enable_output(1, 1)
        if self.stage_control:
            self.visa.set_ramp(2, 0, 0)
            self.visa.enable_heater(2, 1)
            self.visa.enable_output(2, 1)

    def warm(self) -> None:
        # TODO: Test warm
        """Return temperature to 300K in a controlled way."""
        self.visa.enable_output(1, 1)
        self.visa.enable_output(2, 1)
        self.visa.enable_heater(1, 3)
        self.visa.enable_heater(2, 3)
        self.visa.set_ramp(1, 15, 1)
        self.visa.set_ramp(2, 15, 1)
        self.visa.set_setpt(1, 300)
        self.visa.set_setpt(2, 300)
        print('Ramping to 300K begun.')
        ramping = True
        while ramping:
            ramping = (bool(self.ramp_status(1))
                       or bool(self.ramp_status(2)))
            if self.visa.query_temp(6) >= 300:
                self.visa.enable_heater(1, 2)
            if self.visa.query_temp(7) >= 300:
                self.visa.enable_heater(2, 2)
            if ramping:
                time.sleep(600)
        print('Ramping to 300K complete.')

    def process_data(data: list, outdelim: str = '\t') -> Tuple[
            str, list, list]:
        """Convert data from LakeShore 336 to a list."""
        cols = len(data[0])
        sdata_rows = [outdelim.join([i for i in j])
                      for j in data]
        data_cols = [[float(row[i]) for row in data]
                     for i in range(0, cols)]
        data_str = '\n'.join(j for j in sdata_rows)
        return (data_str, sdata_rows, data_cols)
