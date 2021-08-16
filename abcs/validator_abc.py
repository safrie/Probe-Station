# -*- coding: utf-8 -*-

"""
Abstract base class for validators.

Classes_
    ValABC

Part of the probe station V3 collection.
@author Sarah Friedensen
"""

from abc import ABC, abstractmethod


class ValABC(ABC):
    """Create an abstract base class for validators that act like properties.

    This class can be used as a decorator and has setter and getter methods.
    """

    def __init__(self, fget, fset):
        """Initialize the validator abstract base class."""
        self.fget = fget
        self.fset = fset
        self._name = ''

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return self.fget(instance)

    def __set__(self, instance, value):
        name = getattr(self, '_name')
        lims = getattr(instance.info, name)['lim']
