# -*- coding: utf-8 -*-
"""
visa_mag contains the class definitions for Visa interaction with the AMI 430.

classes:
    vMag: Contains attributes and methods for communicating with magnet power
        supply programmer.

Part of the V3 Probe Station Collection
@author: Sarah Friedensen
"""

from abcs.visa_abc import Visa


class vMag(Visa):
    # TODO: Determine if separately saving all the commands is necessary.
    """vMag contains the logic for communicating with the AMI 430.

    vMag inherits from visa_out.Visa and extends __init__, write, query,
    and check_connected.

    atributes_
        state_table: dictionary connecting numerical output state of 430 to its
            meaning
        addr: integer specifying COM port connection to the computer
        mag: Visa resource for 430 power supply programmer
        targ_curr_cmd: Command for setting target current in amps.
        qtarg_curr: Query for target current in amps
        targ_field_cmd: Command for setting target field in fieldUnits
        qtarg_field: Query for the target field in fieldUnits
        ramp_segs_cmd: Command for setting number of ramp segments
        qramp_segs: Query for number of ramp segments
        rate_curr_cmd: Command for setting ramp rate (A/timeUnit) and current
            upper bound for a segment.
        rate_field_cmd: Command for setting the ramp rate (fieldUnit/timeUnit)
            and field upper bound for a segment. Needs a coil constant to work
        qmag_curr: Query for current in Amps flowing in magnet
        qmag_field: Query for magnetic field in fieldUnits
        qquench_det: Query for state of quench detection
        qvolt_limit: Query for voltage limit (V) for magnet
        qcurr_limit: Query for current limit (A) for magnet
        qfield_unit: Query for instrument's field unit (0 = kG, 1 = T)
        qtime_unit: Query for instrument's time unit (0 = s, 1 = min)
        enable_trig_cmd: Command for setting what data appears in the output
            and which ports (serial, ethernet) data should output to
        trig_out_reg: Trigger output register

    methods_
        __init__(int)
        write(str)
        query(str)
        check_connected(int)
        set_targ_curr(float)
        set_targ_field(float)
        set_ramp_segs(int)
        set_rate_curr(int, float, float)
        qrate_curr(int)
        set_rate_field(int, float, float)
        qrate_field(int)
        set_quench_det(bool)
        qquench_det()
        set_volt_limit(float)
        set_curr_limit(float)
        set_field_unit(bool)
        set_time_unit(bool)
        ramp()
        pause()
        zero()
        qstate()
        set_enable_trig(bool, bool, bool, bool, bool, bool, bool)
        qenable_trig()
        trig()
        quench(bool)
    """

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
    qtarg_curr = 'CURR:TARG?'
    qtarg_field = 'FIELD:TARG?'
    qramp_segs = 'RAMP:RATE:SEG?'
    qmag_curr = 'CURR:MAG?'
    qmag_field = 'FIELD:MAG?'
    qquench_det = 'QU:DET?'
    qvolt_limit = 'VOLT:LIM?'
    qcurr_limit = 'CURR:LIM?'
    qfield_unit = 'FIELD:UNIT?'
    qtime_unit = 'RAMP:RATE:UNITS?'

    def __init__(self, address: int) -> None:
        """Extend visa_out's init with 430 attributes and check connection."""
        super().__init__()
        self.mag = None
        self.targ_curr_cmd = ''
        self.targ_field_cmd = ''
        self.ramp_segs_cmd = ''
        self.rate_curr_cmd = ''
        self.rate_field_cmd = ''
        self.enable_trig_cmd = ''
        self.check_connected(address)

    def write(self, cmd: str) -> None:
        """Extend  write to automatically write to this instrument."""
        if self.mag is not None:
            super().write(self.mag, cmd)
        else:
            print('No write--magnet not connected')

    def query(self, cmd: str) -> str:
        """Extend query to automatically write to this instrument."""
        if self.mag is not None:
            return super().query(self.mag, cmd)
        else:
            print('No query--magnet not connected')

    def check_connected(self, com: int) -> None:
        """See if instrument at COM in instrument list. If so, open it."""
        magnet_list = [x for x in self.instruments
                       if (str(com) and 'ASRL') in x]
        if not magnet_list:
            self.mag = None
        else:
            self.mag = self.rm.open_resource(magnet_list[0])

    def set_targ_curr(self, curr: float) -> None:
        # TODO: Test set_targ_curr
        """Create command to set target magnet current in amps."""
        self.targ_curr_cmd = f'CONF:CURR:TARG {curr}'

    def set_targ_field(self, field: float) -> None:
        # TODO: Test set_targ_field
        """Create command to set target magnet field in fieldUnits."""
        self.targ_field_cmd = f'CONF:FIELD:TARG {field}'

    def set_ramp_segs(self, segs: int) -> None:
        # TODO: Test set_ramp_segs
        """Create command to set number of ramp segments along magnet range.

        This means the magnet will ramp at a rate specified by the segment
        when it is within range.
        """
        if segs < 1:
            raise ValueError(
                  'set_ramp_segs: segs must be a positive integer.')
        else:
            self.ramp_segs_cmd = f'CONF:RAMP:RATE:SEG {segs}'

    def set_rate(self, seg: int, rate: float, upbound: float,
                 unit: str = 'curr') -> None:
        # TODO: Test set_rate
        # TODO: Validation on max number of segments
        """Create command to set ramp rate and upper bound for segment seg.

        rate is in units of fieldUnit/timeUnit and upbound is in units of
        fieldUnit.
        """
        valid = ['curr', 'field']
        if seg < 0:
            raise ValueError('set_rate: seg must be nonnegative.')
        elif unit not in valid:
            raise ValueError('set_rate: unit must be "curr" or "field".')
        else:
            self.rate_cmd = (
                f'CONF:RAMP:RATE:{unit} {seg},{rate},{upbound}')
            self.write(self.rate_cmd)

    def qrate(self, seg: int, unit: str) -> str:
        # TODO: Test qrate
        """Return ramp rate and upper bound for segment seg.

        Ramp rate is in fieldUnit/timeUnit and upper bound is in fieldUnit.
        """
        valid = ['curr', 'field']
        if seg < 0:
            raise ValueError('qrate: seg must be nonnegative.')
        elif unit not in valid:
            raise ValueError(f'qrate: unit must be in {valid}.')
        else:
            return self.query(f'RAMP:RATE:{unit}:{seg}?')

    def set_quench_det(self, enable: bool) -> None:
        # TODO: Test set_quench_det
        """Enable/disable automatic INSTRUMENT quench detection."""
        cmd = f'CONF:QU:DET {int(enable)}'
        self.write(cmd)

    def qquench_det(self) -> str:
        # TODO: Test qquench_det
        """Return if quench detect enabled on 430 power supply programmer."""
        return self.query('QU:DET?')

    def set_volt_limit(self, limit: float) -> None:
        # TODO: Test set_volt_limit
        """Set voltage limit for magnet (V)."""
        if limit < 0:
            raise ValueError('set_volt_limit: limit must be positive.')
        else:
            cmd = f'CONF:VOLT:LIM {limit}'
            self.write(cmd)

    def set_curr_limit(self, limit: float) -> None:
        # TODO: Test set_curr_limit
        """Set current limit (A) for the magnet."""
        if limit < 0:
            raise ValueError('set_curr_limit: limit must be positive.')
        else:
            cmd = f'CONF:CURR:LIM {limit}'
            self.write(cmd)

    def set_field_unit(self, unit: bool) -> None:
        # TODO: Test set_field_unit
        """Set magnetic field unit for 430.

        0/False sets field to kilogauss; 1/True sets it to tesla.
        """
        cmd = f'CONF:FIELD:UNITS {int(unit)}'
        self.write(cmd)

    def set_time_unit(self, unit: bool) -> None:
        # TODO: Test set_time_unit
        """Set the time units for the 430.

        0/False sets the time unit to seconds; 1/True sets it to minutes.
        """
        cmd = f'CONF:RAMP:RATE:UNITS {int(unit)}'
        self.write(cmd)

    def ramp(self) -> None:
        # TODO: Test ramp
        """Tell 430 to ramp to target field/current with preset rates."""
        self.write('RAMP')

    def pause(self) -> None:
        # TODO: Test pause
        """Tell 430 to pause at present field/current."""
        self.write('PAUSE')

    def zero(self) -> None:
        # TODO: Test zero
        """Ramp current down until output current is <0.1% Imax."""
        self.write('ZERO')

    def qstate(self) -> str:
        # TODO: Test qstate
        """Return ramp/general state of instrument."""
        return self.state_table[self.query('STATE?')]

    def set_enable_trig(self, mag_volt: bool, mag_curr: bool, mag_field: bool,
                        time: bool, format_out: bool, serial_out: bool,
                        ethernet_out: bool) -> None:
        # TODO: Test set_enable_trig
        """Create command to let trigger func send data from buffer to outputs.

        If this is enabled, when the 430 receives the *trg command, it will
        place the return data into the output buffers and transmit immediately.
        If format_out is false, data will be comma delimited and returned in
        the following order:
            time, magnet field, magnet current, magnet voltage
        Only enabled data will appear.
        """
        bw_sum = (1*mag_volt + 2*mag_curr + 4*mag_field + 8*time
                  + 32*format_out + 64*serial_out + 128*ethernet_out)
        self.enable_trig_cmd = f'*ETE {bw_sum}'
        self.write(self.enable_trig_cmd)

    def qenable_trig(self) -> bin:
        # TODO: Test qenable_trig
        """Query the state of the trigger register and return the bitstring.

        The bitstring corresponds to which bits of the register are
        enabled/disabled.
        """
        return bin(self.query('*ETE?'))

    def trig(self) -> str:
        # TODO: Test trig
        """Trigger output of data to the enabled interfaces."""
        return self.query('*TRG')

    def quench(self, do: bool) -> None:
        # TODO: Test quench
        """Trigger a quench alert to shut down the magnet or clear a quench."""
        self.write(f'QU {1 if do else 0}')
