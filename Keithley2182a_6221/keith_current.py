# -*- coding: utf-8 -*-
"""
Class for working with the electrical current variables with the Keithleys.

Part of the probe station V3 collection

@author Sarah Friedensen
"""

from limits import KeithInfo as kinfo, ivinfo, key


class Current:

    def __init__(self, curr, meas_idx):
        self.info = ivinfo['dic'][meas_idx]()
        self.amps = curr
        self._name = ''

    def __set_name__(self, owner, name):
        self._name = name

    @property
    def amps(self):
        return self._amps

    @amps.setter
    def amps(self, value):
        if :
            # Put in correct limits here.
            pass
        self._amps = value
    pass

