# -*- coding: utf-8 -*-
"""
ABC for program states of measurement instruments for the probe station.

Part of the probe station V3 collection

@author Sarah Friedensen
"""

from abc import ABCMeta, abstractmethod


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

    def __init__(self) -> None:
        # self.do_control = False
        self.do_measure = False
        self.address = 0

    @abstractmethod
    def get_instr_name(self) -> None:
        """Return a string giving the name of the instrument.

        NOT sent through VISA.
        """

    def set_control(self, val: bool) -> None:
        """Change instrument do_control attribute to val."""
        self.do_control = val

    def set_measure(self, val: bool) -> None:
        """Change instrument do_measure attribute to val."""
        self.do_measure = val

    def set_address(self, addr: int) -> None:
        """Change instrument address atribute to addr."""
        self.address = addr

    def get_control(self) -> bool:
        """Return instrument do_control attribute. MAYBE DELETE."""
        return self.do_control

    def get_measure(self) -> bool:
        """Return instrument do_measure attribute. MAYBE DELETE."""
        return self.do_measure

    def get_address(self) -> int:
        """Return instrument GPIB/COM address."""
        return self.address
