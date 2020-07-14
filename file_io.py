# -*- coding: utf-8 -*-
"""
This module contains class definitions for saving data and loading configs.

Part of the probe station V3 collection.

Classes:
    Save
    Config

@author: sfrie
"""

from pathlib import Path
from ruamel_yaml import YAML


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
        _write(str)
        header(str)
        data(str)
    """

    def __init__(self) -> None:
        """Create the empty attributes for making and saving a file."""
        self.file = None
        self.data = None

    def new(self, name: str) -> None:
        """Specify or create text file in which to save data."""
        self.file = None
        if name:
            Path(name).touch()
            self.file = Path(name)

    def _write(self, text: str, mode: str) -> None:
        """Open the file and write information to it."""
        # TODO: Input validate _write mode
        if self.file is not None:
            with self.file.open(mode) as f:
                f.write(text)

    # def header(self, hdr: str) -> None:
    #     """Open the file and write the header information."""
    #     if self.name[0] is not None:
    #         self.file.write_text(hdr)
    #     # if self.name[0] is not None:
    #     #     with open(self.name[0], 'a') as self.file:
    #     #         self.file.write(hdr)

    # def data(self, data: str) -> None:
    #     """Open the file and write the data to it."""
    #     if self.name[0] is not None:
    #         self.file.write_text(data)
            # with open(self.name[0], 'a') as self.file:
            #     self.file.write(data)


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
        self.file = None
        self.params = None
        self.new = None

    def load(self, file: Path) -> None:
        """Load parameters from a config file.  Currently accepts only YAML."""
        self.file = file
        self.params = self.yaml.load(file)

    def save(self, file: Path) -> None:
        """Save current parameters to new config file as YAML."""
        self.file = file
        self.yaml.dump(self.new, file)
