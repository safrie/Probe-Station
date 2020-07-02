# -*- coding: utf-8 -*-
"""
visa_keith.py contains logic for communicating with the Keithley 6221/2182a.

Part of the V3 Probe Station Collection.

Classes:
    vKeith: Contains attributes and methods for communicating with Keithleys.

@author: Sarah Friedensen
"""

from abcs.visa_abc import Visa
# import inspect


class vKeith(Visa):
    """vKeith contains the logic for communicating with the Keithleys.

    vKeith creates, updates, and sends commands to the Keithley 6221 and 2182a
    over GPIB.  It also queries these instruments and returns their responses.
    vKeith inherits from Visa and extends __init__, write, query, and
    check_connected.  It is used as an inner class in Keith.

    attributes_
        source_range_type_cmd: Command to set fixed or best source ranging
        filter_on_cmd: Command to enable/disable filtering
        filter_type_cmd: Command to specify filter type
        filter_window_cmd: Command to specify filter window
        filter_count_cmd: Command to specify filter count
        diffcon_arm_cmd: Command to arm differential conductance measurement
        delta_arm_cmd: Command to arm delta measurement
        pdelt_arm_cmd: Command to arm pulse delta measurement
        pdelt_stair_arm_cmd: Command to arm pulse delta staircase sweep
        pdelt_log_arm_cmd: Command to arm pulse delta logarithmic sweep
        source: Visa instrument for 6221
        meter_connected: boolean for if 2182a connected to 621
        abort_cmd: Command to abort measurement
        in_buffer: Number of points in the data buffer
        qdata: Command to query data in buffer
        source_range_type_cmd_switch: Dict for commands about source range type
        source_range_type_bool_switch: Dict to specify autorange on/off or
            fixed/best when combined with source_range_type_cmd_switch
        qsource_range_type: Query dict for source range type
        unit_cmd_switch: Dict to access commands for setting measurement units
        qarm: Dict to query if a measurement type is armed
        format_cmd: Command to format data output

    methods_
        __init__(int)
        write(str)
        query(str)
        check_connected(int)
        set_source_range(int, bool, str)
        set_meas_rate(int)
        set_meter_range(float)
        set_compliance_v(float)
        set_unit(int)
        set_filter_on(bool)
        set_filter_type(bint)
        set_filter_window(float)
        set_filter_count(int)
        set_filter(bool/bint)
        arm_diffcon(float, float, float, float, float, int, bool)
        arm_delta(float, float, float, int, bool)
        arm_pdelt(float, float, float, float, int, int, bool)
        arm_pdelt_stair(float, float, float, float, float, int, int, bool)
        arm_pdelt_log(float, float, int, float, float, int, int, bool)
        reset()
    """

    abort_cmd = 'SOUR:SWE:ABOR'
    qdata = 'TRAC:DATA?'
    source_range_type_cmd_switch = {
            0: '',
            1: 'CURR:RANG:AUTO ',
            2: 'SOUR:PDEL:RANG ',
            3: 'SOUR:SWE:RANG ',
            4: 'SOUR:SWE:RANG '}
    source_range_type_bool_switch = {
            0: {0: '',
                1: 'OFF',
                2: 'FIXED',
                3: 'FIXED',
                4: 'FIXED'},
            1: {0: '',
                1: 'ON',
                2: 'BEST',
                3: 'BEST',
                4: 'BEST'}
            }
    qsource_range_type = {
            0: 'CURR:RANG:AUTO?',
            1: 'CURR:RANG:AUTO?',
            2: 'SOUR:PDEL:RANG?',
            3: 'SOUR:SWE:RANG?',
            4: 'SOUR:SWE:RANG?'}
    unit_cmd_switch = {
            0: 'UNIT V',
            1: 'UNIT SIEM',
            2: 'UNIT OHMS',
            3: 'UNIT W; POWER AVER',
            4: 'UNIT W; POWER PEAK',
            'volts': 'UNIT V',
            'siemens': 'UNIT SIEM',
            'ohms': 'UNIT OHMS',
            'avgW': 'UNIT W; POWER AVER',
            'peakW': 'UNIT W; POWER PEAK'}
    qarm = {
            0: 'SOUR:DCON:ARM?',
            1: 'SOUR:DEL:ARM?',
            2: 'SOUR:PDEL:ARM?',
            3: 'SOUR:PDEL:ARM?',
            4: 'SOUR:PDEL:ARM?'}

    # TODO: Determine preferred format command.
    format_cmd = ':FORM:ELEM RNUM, TST, SOUR, READ, AVOL; '

    def __init__(self, address: int) -> None:
        """Create a new instance and open resource at address."""
        super().__init__()
#        self.source_range_type_cmd = ''
        self.filter_on_cmd = ''
        self.filter_type_cmd = ''
        self.filter_window_cmd = ''
        self.filter_count_cmd = ''
        self.diffcon_arm_cmd = ''
        self.delta_arm_cmd = ''
        self.pdelt_arm_cmd = ''
        self.pdelt_stair_arm_cmd = ''
        self.pdelt_log_arm_cmd = ''

        self.source = None
        # HACK: Change meter_connected back to False after testing
        self.meter_connected = True
        self.in_buffer = 0
        self.check_connected(address)

    def write(self, cmd: str) -> None:
        """Write cmd to the Keithleys."""
        super().write(self.source, cmd)

    def query(self, cmd: str) -> str:
        """Return Keithleys' answer to the query cmd."""
        return super().query(self.source, cmd)

    def check_connected(self, addr: int) -> None:
        """Attempt to locate and connect to GPIB resource at addr.

        Also, check to see if 2182a is connected to the 6221 if 6221 found.
        """
        # TODO: Test check_connected
        source_list = [x for x in super().__init__() if
                       str(addr) in x and 'GPIB' in x]
        if not source_list:
            self.source = False
            print('Keithleys not connected.')
        else:
            self.source = self.rm.open_resource(source_list[0])
            self.meter_connected = self.query('SOUR:DCON:NVPR?')

    def set_source_range(self, meas_idx: int, auto: bool, rang: float) -> None:
        """Set the Keithley source type and range."""
        # TODO: Test set_source_range
        cmd_1 = (self.source_range_type_cmd_switch[meas_idx]
                 + self.source_range_type_bool_switch[int(auto)][meas_idx])
        cmd_2 = '\n' + f'CURR:RANG {rang}'
        # BUG: Verify the conditional below will set source range appropriately
        cmd = cmd_1 + ('' if auto else cmd_2)
        print(cmd)
        self.write(cmd)

    def set_meas_rate(self, rate: int) -> None:
        # TODO: Test set_meas_rate
        """Set the voltmeter measurement rate in power line cycles."""
        cmd = f"SYST:COMM:SER:SEND ':SENS:VOLT:NPLC {rate}'"
        self.write(cmd)

    def set_meter_range(self, rang: float) -> None:
        # TODO: Test set_meter_range
        """Set the voltmeter range.

        The dev finds specifying the voltmeter range rather than allowing auto-
        range superior, but feel free to add an autorange option.
        """
        cmd = f"SYST:COMM:SER:SEND 'SENS:VOLT:RANG {rang}'"
        self.write(cmd)

    def set_compliance_v(self, volt: float) -> None:
        # TODO: Test set_compliance_v
        """Set the compliance voltage."""
        cmd = f'CURR:COMP {volt}'
        self.write(cmd)

    def set_unit(self, key: int) -> None:
        # TODO: Test set_unit
        """Set measurement units for the voltmeter."""
        cmd = self.unit_cmd_switch[key]
        self.write(cmd)

    def set_filter_on(self, enable: bool) -> None:
        # TODO: Test set_filter_on
        """Enable/disable filtering."""
        self.filter_on_cmd = f'SENS:AVER {"ON" if enable else "OFF"}; '

    def set_filter_type(self, idx: int) -> None:
        # TODO: Test set_filter_type
        """Set the filter type based on binary integer idx."""
        self.filter_type_cmd = f'TCON {"REP" if idx else "MOV"}; '

    def set_filter_window(self, wind: float) -> None:
        # TODO: Test set_filter_window
        """Set the filter window."""
        self.filter_window_cmd = f'WIND: {wind}; '

    def set_filter_count(self, count: int) -> None:
        # TODO: Test set_filter_count
        """Set the filter count."""
        self.filter_count_cmd = f'COUN {count}; '

    def set_filter(self, filter_on: bool) -> None:
        # TODO: Test set_filter
        """Set the filter parameters."""
        cmd = (self.filter_on_cmd
               + (self.filter_type_cmd
                  + self.filter_window_cmd
                  + self.filter_count_cmd) if filter_on else '')
        print(cmd)  # Testing only
        if len(cmd) > 0:
            self.write(cmd)

    # %% Arming Commands

    def arm_diffcon(self, start: float, stop: float, step: float, delta: float,
                    delay: float, count: int, compl_abort: bool) -> str:
        # TODO: Test arm_diffcon
        """Return the command to arm a differential conductance measurement.

        start, stop, step, and delta are passed to the method in microamps;
        delay is passed to the method in milliseconds.
        """
        cmd = (f':TRAC:CLE; POIN {count}; '
               + f':SOUR:DCON:STAR {round(start * 1e-6, 9)}; '
               + f'STOP {round(stop * 1e-6, 9)}; '
               + f'STEP {round(step * 1e-6, 9)}; '
               + f'DELTA {round(delta * 1e-6, 9)}; '
               # TODO: Test delay in arm_diffcon for proper units.
               + f'DELAY {round(delay * 1e-3, 6)}; '
               + f'CAB {"ON" if compl_abort else "OFF"}; '
               + 'ARM')
        print(cmd)
        return cmd

    def arm_delta(self, high: float, low: float, delay: float, count: int,
                  compl_abort: bool) -> str:
        # TODO: Test arm_delta
        """Return the command to arm a current delta measurement.

        high and low are passed to the method in microamps; delay is passed in
        milliseconds.
        """
        cmd = (f':TRAC:CLE; POIN {count}; '
               + f':SOUR:DELT:HIGH {round(high * 1e-6, 9)}; '
               + f'LOW {round(low * 1e-6, 9)}; '
               # TODO: Test delay in arm_delta for proper units.
               + f'DELAY {round(delay * 1e-3, 6)}; '
               + f'COUN {count}; '
               + f'CAB {"ON" if compl_abort else "OFF"}; '
               + 'ARM')
        print(cmd)
        return cmd

    def arm_pdelt(self, high: float, low: float, width: float, delay: float,
                  count: int, cycle_int: int, low_meas: bool) -> str:
        # TODO: Test arm_pdelt
        """Return the command to arm a pulse delta measurement.

        high and low are passed to the method in microamps; width and source
        delay are passed in microseconds; and cycle_int is passed in PLC.
        """
        cmd = (f':TRAC:CLE; POIN {count}; '
               + f':SOUR:PDEL:HIGH {round(high * 1e-6, 9)}; '
               + f'LOW {round(low * 1e-6, 9)}; '
               # TODO: Test width in arm_pdelt for proper units.
               + f'WIDT {round(width * 1e-6, 9)}; '
               # TODO: Test source delay in arm_pdelt for proper units.
               + f'SDEL {round(delay * 1e-6, 9)}; '  # Pulse delay
               + f'COUN {count}; '
               + f'INT {cycle_int}; '  # Quasiperiod
               + f'LME {2 if low_meas else 1}; '
               + 'SWE OFF; ARM')
        print(cmd)
        return cmd

    def arm_pdelt_stair(self, start: float, stop: float, step: float,
                        delay: float, width: float, cycle_time: float,
                        count: int, sweeps: int, low_meas: bool) -> str:
        # TODO: Test arm_pdelt_stair.
        # TODO: Verify the units on delay and width in arm_pdelt_stair.
        """Return the command to arm a pulse delta staircase sweep.

        start, stop, and step are passed in microamps; delay and width are
        passed in microseconds; and cycle_time is passed in seconds.
        """
        cmd = (f':TRAC:CLE; POIN {count * sweeps}; '
               + ':SOUR:SWE:SPAC LIN; '
               + f'COUN {sweeps}; '
               # TODO: Check to make sure don't need to back out of menu (pds)
               + f'DEL {round(cycle_time, 6)}; '  # Sweep delay/period
               # TODO: Check to make sure don't need to back out of menu (pds)
               + f'CURR:STAR {round(start * 1e-6, 9)}; '
               + f'STOP {round(stop * 1e-6, 9)}; '
               + f'STEP {round(step * 1e-6, 9)}; '
               # TODO: Check to make sure don't need to back out of menu (pds)
               + f'PDEL:WIDT {round(width * 1e-3, 9)}; '
               + f'SDEL {round(delay * 1e-6, 9)}; '  # Pulse delay
               + f'COUN {count}; '
               + f'LME {2 if low_meas else 1}; '
               + 'SWE ON; ARM')
        print(cmd)
        return cmd

    def arm_pdelt_log(self, start: float, stop: float, points: int,
                      delay: float, width: float, cycle_time: float,
                      sweeps: int, low_meas: bool) -> str:
        # TODO: Test arm_pdelt_log
        # TODO: Verify input units for delay and width in arm_pdelt_log.
        """Return command to arm a pulse delta logarithmic sweep.

        start and stop are passed in microamps; delay and width are passed in
        microseconds.
        """
        cmd = (f':TRAC:CLE; POIN {points * sweeps}; '
               + 'SOUR:SWE:SPAC LOG; '
               # TODO: Verify 'SOUR:SWE:POIN' not covered by 'SOUR:PDEL:COUN'
               + f'POIN {points}; '
               + f'COUN {sweeps}; '
               # TODO: Check to make sure don't need to back out of menu (pdl)
               + f'DEL {round(cycle_time, 6)}; '  # Sweep delay/period
               # TODO: Check to make sure don't need to back out of menu (pdl)
               + f'CURR:STAR {round(start * 1e-6, 9)}; '
               + f'STOP {round(stop * 1e-6, 9)}; '
               # TODO: Check to make sure don't need to back out of menu (pdl)
               + f'PDEL:WIDT {round(width * 1e-6, 9)}; '
               + f'SDEL {round(delay * 1e-6, 9)}; '  # Pulse delay
               + f'COUN {points}; '
               + f'LME {2 if low_meas else 1}; '
               + 'SWE ON; ARM')
        print(cmd)
        return cmd

    def reset(self) -> None:
        """Reset the keithleys to default values and clear data buffer."""
        self.write('*rst; trac:cle; outp:resp slow')
