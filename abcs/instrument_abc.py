# -*- coding: utf-8 -*-
"""
ABC for program states of measurement instruments for the probe station.

Part of the probe station V3 collection

@author Sarah Friedensen
"""

from abc import ABCMeta, abstractmethod
from limits import (KeithInfo as kinfo, TempInfo as tinfo, MagInfo as minfo)


class Instrument():
    """Abstract base class for universal program states of instruments.

    attributes_
        do_control: Boolean specifying whether or not program should send
            commands to this instrument during measurement.
        do_measure: Boolean specifying whether or not the program monitors
            output from this instrument during measurement.
        address: integer VISA communications address of this instrument.

    methods_
        __init__()
        get_instr_name()
        set_control(bool)
        set_measure(bool)
        set_address(int)
        *get_control()
        *get_measure()
        *get_address()
    """

    __metaclass__ = ABCMeta
    infodic = {'Keith': kinfo,
               'Temp': tinfo,
               'Mag': minfo}

    def __init__(self, instr: str) -> None:
        if instr in self.infodic.keys():
            self.info = self.infodic[instr]
            self.measure = self.info.measure['def']
            # TODO: Figure out how to initialize control
            # self.do_measure = self.info.measure['def']
            # self.do_control = False
            # self.do_measure = False
        else:
            # Consider not doing this and raising an exception instead after
            # testing
            self.info = self.infodic['Keith']
            print("Invalid instrument given.  Setting to default instrument "
                  + "(Keith).")
        self.address = self.info.addr['def']

    @abstractmethod
    def get_instr_name(self) -> None:
        """Return a string giving the name of the instrument.

        NOT sent through VISA.
        """
        pass

    @property
    def control(self) -> bool:
        return self._control

    @control.setter
    def control(self, val: bool) -> None:
        self._control = val

    @property
    def measure(self) -> bool:
        return self._measure

    @measure.setter
    def measure(self, val: bool) -> None:
        self._measure = val

    # def set_control(self, val: bool) -> None:
    #     """Change instrument do_control attribute to val."""
    #     self.do_control = val

#     def set_measure(self, val: bool) -> None:
#         """Change instrument do_measure attribute to val."""
#         self.do_measure = val

    @property
    def address(self) -> int:
        """GPIB address of the instrument"""
        return self._address

    @address.setter
    def address(self, addr: int) -> None:
        """Change instrument address property to addr."""
        if addr not in self.info.addr['lim']:
            addr = self.info.addr['def']
            print(f"Given address out of bounds ({self.info.addr['lim']}).  "
                  + f"GPIB address set to default ({addr}).")
        self._address = addr

    # def set_address(self, addr: int) -> None:
    #     """Change instrument address atribute to addr."""
    #     if addr not in self.info.addr['lim']:
    #         addr = self.info.addr['def']
    #         print(f"Given address out of bounds ({self.info.addr['lim']}).  "
    #               + f"GPIB address set to default ({addr}).")
    #     self.address = addr
    #     return addr

    # def get_control(self) -> bool:
    #     """Return instrument do_control attribute. MAYBE DELETE."""
    #     return self.do_control

    # def get_measure(self) -> bool:
    #     """Return instrument do_measure attribute. MAYBE DELETE."""
    #     return self.do_measure

    # def get_address(self) -> int:
    #     """Return instrument GPIB/COM address."""
    #     return self.address
