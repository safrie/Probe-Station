# -*- coding: utf-8 -*-
"""
This module contains class definitions for saving data and loading configs.

Part of the probe station V3 collection.

Classes:
    Save
    Config

@author: sfrie
"""

import os
from pathlib import Path
from ruamel_yaml import YAML


print('file_io imports allegedly complete.')


class Save():
    """Save contains the methods and attributes necessary for saving data.

    attributes_
        name: filename as a string
        file: file object that is the actual file
        base: base name of the file
        ext: file extension for the file
        data: the actual information to be saved to the file

    methods_
        __init__()
        new(str list)
        header(str)
        data(str)
    """

    def __init__(self) -> None:
        """Create the empty attributes for making and saving a file."""
        self.name = None
        self.file = None
        self.base = None
        self.ext = None
        self.data = None

    def new(self, name) -> None:
        """Specify or create text file in which to save data."""
        self.name = None
        if name[0]:
            self.name = name
            self.file = open(self.name[0], 'w+')
            (self.base, self.ext) = os.path.splitext(name[0])
            self.file.close()

        def header(self, hdr: str) -> None:
            """Open the file and write the header information."""
            if self.name[0] is not None:
                with open(self.name[0], 'a') as self.file:
                    self.file.write(hdr)

        def data(self, data: str) -> None:
            """Open the file and write the data to it."""
            if self.name[0] is not None:
                with open(self.name[0], 'a') as self.file:
                    self.file.write(data)


class Config():
    """Config contains methods and attributes for handling configuration files.

    attributes_
        name: Filename (base + ext)
        file: File path for config file (path object).
        params: Actual YAML dictionary loaded from the file
        base: Basename for the filename.
        ext: extension for the filename.
        new: New config file, used as a placeholder.

    methods_
        __init__()
        load(str list)
        save(str list)
    """

    yaml = YAML()

    def __init__(self) -> None:
        """Create empty attributes for loading/saving configuration data."""
        self.name = None
        self.file = None
        self.params = None
        self.base = None
        self.ext = None
        self.new = None

    def load(self, name) -> None:
        """Load parameters from a config file.  Currently accepts only YAML."""
        self.name = name
        self.file = Path(self.name)
        self.params = self.yaml.load(self.file)

    def save(self, name) -> None:
        """Save current parameters to new config file as YAML."""
        if name[0]:
            self.name = name
            self.file = None
            (self.base, self.ext) = os.path.splitext(name[0])
            self.file = Path(name[0])
            self.yaml.dump(self.new, self.file)
