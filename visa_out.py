# -*- coding: utf-8 -*-
"""
ABC for controlling program interactions with instruments over pyvisa.

Part of the V3 probe station collection.
@author: Sarah Friedensen
"""

import visa
from abc import ABCMeta, abstractmethod
from typing import Union


class Visa():
    """Abstract base class for communicating with instruments over pyvisa.

    Opens communications, sends commands and queries, and includes commands for
    communicating 'universal' IEEE-488 commands.

    attributes_
        reset: command to reset an instrument.
        clear: command to clear status byte.
        idn: command to request instrument identity
        rm: pyvisa resource manager
        instruments: list of connected instruments by their address name.

    methods_
        __init__()
        check_connected()
        write(visa resource, str)
        query(visa resource, str)
        get_idn(visa resource)
    """

    __metaclass__ = ABCMeta

    reset = '*RST'
    clear = '*CLS'
    idn = '*IDN?'

    def __init__(self) -> list:
        """Open pyvisa resource manager and list connected instruments."""
        self.rm = visa.ResourceManager()
        self.instruments = self.rm.list_resources()
        return self.instruments

    @abstractmethod
    def check_connected(self) -> None:
        """Overridden in daughter classes."""
        pass

    def write(self, instr: visa.Resource, cmd: str) -> None:
        """If instr connected, write cmd to it."""
        try:
            instr.write(cmd)
        except AttributeError:
            print(f'{instr.__name__} is not connected.')

    def query(self, instr: visa.Resource, cmd: str) -> Union[str, None]:
        """If instr connected, query cmd and return result."""
        try:
            out = instr.query(cmd)
        except AttributeError:
            print(f'{instr.__name__} is not connected.')
            out = None
        finally:
            return out

    def get_idn(self, instr: visa.Resource) -> None:
        """If instr connected, query its ID and print result."""
        try:
            out = instr.query(self.idn)
        except AttributeError:
            print(f'{instr.__name__} is not connected.')
        else:
            print(out)
