# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 16:14:14 2020

@author: sfrie
"""

import sys
from qtpy import QtWidgets
from qtpy.QtWidgets import (QPushButton, QLabel, QWidget)


class SubWindow(QWidget):
    """Presenting a docstring."""

    def __init__(self, parent=None):
        """Presenting a docstring."""
        super(SubWindow, self).__init__(parent)
        label = QLabel("Sub Window",  self)

    def closeEvent(self, event):
        """Presenting a docstring."""
        self.deleteLater()
        event.accept()


class MainWindow(QWidget):
    """Presenting a class docstring."""

    def __init__(self, parent=None):
        """Presenting a docstring."""
        super(MainWindow, self).__init__(parent)
        openButton = QPushButton("Open Sub Window",  self)
        openButton.clicked.connect(self.openSub)

    def openSub(self):
        """Presenting a docstring."""
        self.sub = SubWindow()
        self.sub.show()

    def closeEvent(self, event):
        """Presenting a docstring."""
        widgetList = QtWidgets.QApplication.topLevelWidgets()
        numWindows = len(widgetList)
        if numWindows > 1:
            event.ignore()
        else:
            event.accept()


app = QtWidgets.QApplication(sys.argv)
mainWin = MainWindow()
mainWin.show()
