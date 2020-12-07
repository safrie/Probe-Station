# -*- coding: utf-8 -*-
"""
design.py contains all the logic for creating the user interface.

@author: Sarah Friedensen
"""

from limits import (mu, KeithInfo as kinfo, DconInfo as dcinfo,
                    DeltaInfo as delinfo, PDeltInfo as pdinfo,
                    SweepInfo as swinfo, PDeltLogInfo as pdloginfo, ivinfo,
                    TempInfo as tinfo, MagInfo as minfo)
from PyQt5 import QtCore, QtWidgets
# from PyQt5 import  QtGui
from PyQt5.QtWidgets import (QWidget, QFrame, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox)
import pyqtgraph as pg
# import sys
from typing import Tuple

from abc import ABCMeta, abstractmethod
# import inspect


class Ui_MainWindow(object, metaclass=ABCMeta):
    """Abstract base class for universal properties of the UI windows.

    attributes_

    methods_
        setupUi(QMainWindow, opt bool, opt bool)
        add_top(QWidget)
        add_config(QWidget)
        add_save(QWidget)
        add_param(QWidget)
        add_lower(QWidget)
    """

    # def __init__(self):
    #     print(f'caller = {inspect.stack()[1]}')

    @abstractmethod
    def setupUi(self, Window) -> Tuple[QWidget, QVBoxLayout]:
        """Set up the window's UI.  Extended/overridden in daughter methods."""
        Window.setObjectName(str(Window))
        centralWidget = QWidget(Window, objectName='CentralWidget')
        Window.setCentralWidget(centralWidget)

        centralLayout = QVBoxLayout(centralWidget,
                                    objectName='CentralWidgetLayout')
        return (centralWidget, centralLayout)

    def add_top(self, widget) -> Tuple[QFrame, QGridLayout]:
        """Create a top frame for the window."""
        topFrame = QFrame(widget, objectName='TopFrame')
        style = QFrame.Panel | QFrame.Raised
        topFrame.setFrameStyle(style)
        topFrame.setLineWidth(2)
        topLayout = QGridLayout(topFrame, objectName='TopFrameLayout')
        return (topFrame, topLayout)

    def add_config(self, widget) -> Tuple[QHBoxLayout, QLineEdit, QPushButton,
                                          QPushButton]:
        """Add a config layout to a window."""
        configLayout = QHBoxLayout(widget, objectName='ConfigLayout')
        configLabel = QLabel(widget, objectName='ConfigLabel',
                             text='Configuration File')
        configLayout.addWidget(configLabel)
        configFile = QLineEdit(widget, objectName='ConfigFile')
        configFile.setToolTip(
            'Configuration file for measurement settings.  YAML files only.')
        configLayout.addWidget(configFile)
        configLoadButton = QPushButton(widget, objectName='ConfigLoadButton',
                                       text='Load')
        configLoadButton.setToolTip(
            'Load measurement parameters from a YAML file.')
        configLayout.addWidget(configLoadButton)
        configSaveButton = QPushButton(widget, objectName='ConfigSaveButton',
                                       text='Save')
        configSaveButton.setToolTip(
            'Save measurement parameters defined in UI to a YAML file.')
        configLayout.addWidget(configSaveButton)
        return (configLayout, configFile, configLoadButton, configSaveButton)

    def add_save(self, widget) -> Tuple[QHBoxLayout, QLineEdit, QPushButton]:
        """Add a save layout to a window."""
        saveLayout = QHBoxLayout(widget, objectName='SaveLayout')
        saveLabel = QLabel(widget, objectName='SaveFileLabel',
                           text='Save File')
        saveLayout.addWidget(saveLabel)
        saveFile = QLineEdit(widget, objectName='SaveFile')
        saveLayout.addWidget(saveFile)
        saveButton = QPushButton(widget, objectName='SaveButton',
                                 text='Save As')
        saveLayout.addWidget(saveButton)
        return(saveLayout, saveFile, saveButton)

    def add_param(self, widget) -> Tuple[QWidget, QGridLayout]:
        """Add a parameter layout to a window."""
        paramWidget = QWidget(widget, objectName='ParamWidget')
        paramLayout = QGridLayout(paramWidget, objectName='ParamLayout')
        return(paramWidget, paramLayout)

    def add_lower(self, widget) -> Tuple[QFrame, QGridLayout]:
        """Add a lower frame and layout to a window."""
        lowerFrame = QFrame(widget, objectName='LowerFrame')
        style = QFrame.Panel | QFrame.Raised
        lowerFrame.setFrameStyle(style)
        lowerFrame.setLineWidth(2)
        lowerLayout = QGridLayout(lowerFrame, objectName='LowerFrameLayout')
        return(lowerFrame, lowerLayout)


class Ui_PlotWindow(Ui_MainWindow):
    """Contains UI for save, save/load config, plotting.

    Inherits from Ui_MainWindow.

    attributes_
        configFile: QLineEdit for configuration file
        configLoadButton: QPushButton for loading configuration files
        configSaveButton: QPushButton for saving configuration files
        saveFile: QLineEdit for the filename of the save file.
        saveButton: QPushButton for saving data
        plotFrame: Frame for the plotting functionality.
        graphicsWidget: pyqtgraph GraphicsLayoutWidget for the graphing.

    methods_
        setupUi(QMainWindow)
        closeEvent(event): Overrides original behavior.
    """

    def __init__(self):
        super().__init__()

    def setupUi(self, PlotWindow) -> None:
        """Set up the main window UI (where plotting and stuff happens)."""
        (centralWidget, centralLayout) = super().setupUi(PlotWindow)
        PlotWindow.setWindowTitle('Probe Station Measurement')
        # TODO: Find appropriate size
        PlotWindow.resize(500, 500)

        (topFrame, topLayout) = self.add_top(centralWidget)
        centralLayout.addWidget(topFrame)

        configFrame = QFrame(topFrame, objectName='ConfigFrame')
        topLayout.addWidget(configFrame, 1, 0, 1, 1)
        (configLayout, self.configFile, self.configLoadButton,
         self.configSaveButton) = self.add_config(configFrame)

        saveFrame = QFrame(topFrame, objectName='SaveFrame')
        topLayout.addWidget(saveFrame, 0, 0, 1, 1)
        (saveLayout, self.saveFile, self.saveButton) = self.add_save(saveFrame)

        plotFrame = QFrame(centralWidget, objectName='PlotFrame')
        centralLayout.addWidget(plotFrame)
        self.graphicsWidget = pg.GraphicsLayoutWidget(plotFrame)

    def closeEvent(self, event) -> None:
        """Determine what to do when main window closed."""
        event.accept()


class Ui_KeithWindow(Ui_MainWindow):
    """Contains UI for setting up Keithley 6221/2182a parameters.

    attributes_
        configFile: QLineEdit containing the filename for the config file.
        configLoadButton: QPushButton for opening file load dialog box.
        configSaveButton: QPushButton for saving settings into a config file.
        GPIBSpinBox: QSpinBox for GPIB address.
        measureTypeCombobox: QComboBox for selecting type of IV measurement.
        unitsCombobox: QComboBox for selecting measurement unit.
        sourceRangeTypeCombobox: QComboBox for selecting fixed or best ranging.
        sourceRangeCombobox: QComboBox for selecting current source range.
        complianceSpinbox: QDoubleSpinBox for setting voltage compliance.
        CABCheckbox: QCheckBox for enabling/disabling compliance abort.
        meterRangeCombobox: QComboBox for selecting voltmeter range.
        current1Label: QLabel for the current1 parameter.
        current1Spinbox: QDoubleSpinBox for current1 parameter.
        current2Label: QLabel for the current2 parameter.
        current2Spinbox: QDoubleSpinBox for current2 parameter.
        currStepLabel: QLabel for parameters that appear in 3rd field.
        currStepSpinbox: QDoubleSpinBox for parameters that appear in field 3.
        field4Label: QLabel for parameters that appear in 4th field.
        field4Spinbox: QDoubleSpinBox for parameters that ppear in 4th field.
        rateLabel: QLabel for measurement rate parameter.
        rateSpinbox: QDoubleSpinBox for measurement rate.
        delayLabel: QLabel for measurement/pulse delay.
        delaySpinbox: QDoubleSpinBox for measurement/pulse delay.
        pulseWidthLabel: QLabel for pulse width UI element.
        pulseWidthSpinbox: QDoubleSpinBox for pulse width parameter.
        countLabel: QLabel for pulse/point count UI element.
        countSpinbox: QSpinbox for pulse/point count.
        lowMeasCheckbox: QCheckbox for low measure option.
        filterCheckbox: QCheckbox for enabling/disabling filtering.
        filterTypeCombobox: QComboBox for selecting filter type.
        filterWindowLayout: QHboxLayout for filter window UI elements.
        filterWindowLabel: QLabel for filter window element.
        filterWindowSpinbox: QDoubleSpinBox for setting filter window.
        filterCountSpinbox: QSpinBox for setting filter count.
        armButton: QPushButton for arming a Keithley measurement.
        startButton: QPushButton for starting measurements.

    methods_
        setupUi(QMainWindow)
        closeEvent(event)
    """

    def __init__(self):
        super().__init__()

    def setupUi(self, KeithWindow) -> None:
        """Initialize the UI elements for the Keithley window."""
        (centralWidget, centralLayout) = super().setupUi(KeithWindow)
        KeithWindow.setWindowTitle('Keithley 6221/2182a Stack')
        # TODO: Find appropriate size and place
        KeithWindow.resize(300, 300)

        (topFrame, topLayout) = self.add_top(centralWidget)
        centralLayout.addWidget(topFrame)

        configFrame = QFrame(topFrame, objectName='ConfigFrame')
        topLayout.addWidget(configFrame, 0, 0, 1, 1)
        (configLayout, self.configFile, self.configLoadButton,
         self.configSaveButton) = self.add_config(configFrame)

        (paramWidget, paramLayout) = self.add_param(centralWidget)
        centralLayout.addWidget(paramWidget)

        (lowerFrame, lowerLayout) = self.add_lower(centralWidget)

        # TODO: Determine if () not needed at end of below line
        info = ivinfo['dic'][kinfo.meas['def']]()

        GPIBLabel = QLabel(paramWidget, text='GPIB Address: ',
                           objectName='GPIBLabel')
        paramLayout.addWidget(GPIBLabel, 0, 0, 1, 1)

        self.GPIBSpinbox = QSpinBox(paramWidget, objectName='GPIBSpinBox')
        self.GPIBSpinbox.setToolTip('GPIB address of Keithley 6221/2182a')
        self.GPIBSpinbox.setRange(info.addr['lim'][0], info.addr['lim'][-1])
        self.GPIBSpinbox.setValue(info.addr['def'])
        paramLayout.addWidget(self.GPIBSpinbox, 0, 1, 1, 1)

        measureTypeLabel = QLabel(paramWidget, text='Measurement Type: ',
                                  objectName='MeasurementTypeLabel')
        paramLayout.addWidget(measureTypeLabel, 1, 0, 1, 1)

        self.measureTypeCombobox = QComboBox(paramWidget,
                                             objectName='MeasureTypeComboBox')
        # TODO: Test that AddItems behaves properly
        self.MeasureTypeComboBox.addItems(info.meas['labels'])
        # TODO: Determine that info.idx calls properly
        self.measureTypeCombobox.setCurrentIndex(info.idx)
        print(f"For measure type combobox, idx = {info.idx}")
        paramLayout.addWidget(self.measureTypeCombobox, 1, 1, 1, 1)

        unitsLabel = QLabel(paramWidget, text='Units:', objectName='UnitLabel')
        paramLayout.addWidget(unitsLabel, 2, 0, 1, 1)

        self.unitsCombobox = QComboBox(paramWidget, objectName='UnitsComboBox')
        # TODO: Determine if below loads correctly
        self.unitsCombobox.addItems(info.unit['labels'])
        self.unitsCombobox.setCurrentIndex(info.unit['def'])
        paramLayout.addWidget(self.unitsCombobox, 2, 1, 1, 1)

        sourceRangeTypeLabel = QLabel(
            paramWidget, text='Source (6221) range type:',
            objectName='SourceRangeTypeLabel')
        paramLayout.addWidget(sourceRangeTypeLabel, 3, 0, 1, 1)

        self.sourceRangeTypeCombobox = QComboBox(
            paramWidget, objectName='SourceRangeTypeComboBox')
        self.sourceRangeTypeCombobox.addItems(
            str(info.sour_range['typ']['dic'].items()))
        self.sourceRangeTypeCombobox.setCurrentIndex(
            info.sour_range['typ']['def'])
        paramLayout.addWidget(self.sourceRangeTypeCombobox, 3, 1, 1, 1)

        sourceRangeLayout = QGridLayout(paramWidget,
                                        objectName='SourceRangeLayout')
        paramLayout.addLayout(
            sourceRangeLayout, 4, 1, 1, 1, QtCore.Qt.AlignHCenter)

        sourceRangeLabel = QLabel(paramWidget, text='Range:',
                                  objectName='SourceRangeLabel')
        sourceRangeLayout.addWidget(
            sourceRangeLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)

        self.sourceRangeCombobox = QComboBox(paramWidget,
                                             objectName='SourceRangeComboBox')
        sr_items = [str(info.sour_range['minmax'][i]) + ' '
                    + info.sour_range['txt'][i]
                    for i in info.sour_range['dic'].keys()]
        # self.sourceRangeCombobox.addItem('2 nA')
        # self.sourceRangeCombobox.addItem('20 nA')
        # self.sourceRangeCombobox.addItem('200 nA')
        # self.sourceRangeCombobox.addItem('2 \u03BCA')
        # self.sourceRangeCombobox.addItem('20 \u03BCA')
        # self.sourceRangeCombobox.addItem('200 \u03BCA')
        # self.sourceRangeCombobox.addItem('2 mA')
        # self.sourceRangeCombobox.addItem('20 mA')
        # self.sourceRangeCombobox.addItem('100 mA')
        self.sourceRangeCombobox.setCurrentIndex(sr_items)
        sourceRangeLayout.addWidget(self.sourceRangeCombobox, 0, 1, 1, 1)

        complianceLayout = QHBoxLayout(paramWidget,
                                       objectName='ComplianceLayout')
        paramLayout.addLayout(complianceLayout, 5, 0, 1, 1)

        complianceLabel = QLabel(paramWidget, text='Compliance Voltage (V)',
                                 objectName='ComplianceLabel')
        complianceLayout.addWidget(complianceLabel)

        self.complianceSpinbox = QDoubleSpinBox(paramWidget,
                                                objectName='ComplianceSpinBox')
        comp_lim = info.compl_volt['lim']
        self.complianceSpinbox.setRange(comp_lim[0], comp_lim[1])
        self.complianceSpinbox.setValue(info.compl_volt['def'])
        complianceLayout.addWidget(self.complianceSpinbox)

        self.CABCheckbox = QCheckBox(paramWidget, text='Compliance Abort',
                                     objectName='CABCheckBox')
        self.CABCheckbox.setChecked(info.cab_def)
        paramLayout.addWidget(
           self.CABCheckbox, 5, 1, 1, 1, QtCore.Qt.AlignHCenter)

        # TODO: Determine if I want autorange option

        meterRangeLabel = QLabel(paramWidget, text='Voltmeter (2182a) Range:',
                                 objectName='MeterRangeLabel')
        paramLayout.addWidget(meterRangeLabel, 6, 0, 1, 1)

        self.meterRangeCombobox = QComboBox(paramWidget,
                                            objectName='MeterRangeComboBox')
        self.meterRangeCombobox.addItems(info.volt_range['labels'])
        # self.meterRangeCombobox.addItem('10 mV')
        # self.meterRangeCombobox.addItem('100 mV')
        # self.meterRangeCombobox.addItem('1 V')
        # self.meterRangeCombobox.addItem('10 V')
        # self.meterRangeCombobox.addItem('100 V')
        self.meterRangeCombobox.setCurrentIndex(info.volt_range['def'])
        paramLayout.addWidget(self.meterRangeCombobox, 6, 1, 1, 1)

        measureWidget = QWidget(centralWidget, objectName='MeasureWidget')
        centralLayout.addWidget(measureWidget)

        measureLayout = QGridLayout(measureWidget, objectName='MeasureLayout')

        current1Layout = QHBoxLayout(objectName='Curr1Layout')
        measureLayout.addLayout(current1Layout, 0, 0, 1, 1)

        label = (info.curr1['txt'][info.idx] +
                 info.sour_range['txt'][info.sour_range['def']])
        self.current1Label = QLabel(measureWidget, text=label,
                                    objectName='Curr1Label')
        current1Layout.addWidget(self.current1Label)

        self.current1Spinbox = QDoubleSpinBox(measureWidget,
                                              objectName='Curr1SpinBox')
        # TODO: Verify curr1 range, value set correctly
        self.current1Spinbox.setRange(info.curr1['lim'][0],
                                      info.curr1['lim'][1])
        self.current1Spinbox.setValue(info.curr1['def'])
        current1Layout.addWidget(self.current1Spinbox)

        current2Layout = QHBoxLayout(objectName='Curr2Layout')
        measureLayout.addLayout(current2Layout, 1, 0, 1, 1)

        label = (info.curr2['txt'][info.idx]
                 + info.sour_range['txt'][info.sour_range['def']])
        self.current2Label = QLabel(measureWidget, text=label,
                                    objectName='Curr2Label')
        current2Layout.addWidget(self.current2Label)

        self.current2Spinbox = QDoubleSpinBox(measureWidget,
                                              objectName='Curr2SpinBox')
        # TODO: Verify curr2 range, value set correctly
        self.current2Spinbox.setRange(info.curr2['lim'][0],
                                      info.curr2['lim'][1])
        self.current2Spinbox.setValue(info.curr2['def'])
        current2Layout.addWidget(self.current2Spinbox)

        currStepLayout = QHBoxLayout(objectName='CurrStepLayout')
        measureLayout.addLayout(currStepLayout, 2, 0, 1, 1)
        label = (info.curr_step['txt'][info.idx]
                 + info.sour_range['txt'][info.sour_range['def']])
        self.currStepLabel = QLabel(measureWidget, text=label,
                                    objectName='CurrStepLabel')
        currStepLayout.addWidget(self.currStepLabel)

        self.currStepSpinbox = QDoubleSpinBox(measureWidget,
                                              objectName='CurrStepSpinBox')
        self.currStepSpinbox.setRange(info.curr_step['lim'][0],
                                      info.curr_step['lim'][1])
        self.currStepSpinbox.setValue(info.curr_step['def'])
        currStepLayout.addWidget(self.currStepSpinbox)

        field4Layout = QHBoxLayout(objectName='Field4Layout')
        measureLayout.addLayout(field4Layout, 3, 0, 1, 1)

        # TODO: Verify this prints the correct label
        label = (info.field4['labels'][info.idx]
                 + (info.sour_range['txt'][info.sour_range['def']] if
                    info.idx == 0 else ''))
        print(f"Field4 Label = {label}")
        self.field4Label = QLabel(measureWidget, text=label,
                                  objectName='Field4Label')
        field4Layout.addWidget(self.field4Label)

        f4dic = ivinfo['field4'][info.idx]
        self.field4Spinbox = QDoubleSpinBox(measureWidget,
                                            objectName='Field4SpinBox')
        if ivinfo['field4'][info.idx] is not None:
            self.field4Spinbox.setRange(f4dic['lim'][0], f4dic['lim'][-1])
        self.field4Spinbox.setValue(f4dic['def'])
        self.field4Spinbox.setDecimals(f4dic['decim'])
        field4Layout.addWidget(self.field4Spinbox)

        rateLayout = QHBoxLayout(objectName='RateLayout')
        measureLayout.addLayout(rateLayout, 4, 0, 1, 1)

        self.rateLabel = QLabel(measureWidget,
                                text=info.rate['txt'][info.idx],
                                objectName='RateLabel')
        rateLayout.addWidget(self.rateLabel)

        self.rateSpinbox = QDoubleSpinBox(measureWidget,
                                          objectName='RateSpinBox')
        self.rateSpinbox.setRange(info.rate['lim'][0], info.rate['lim'][-1])
        self.rateSpinbox.setValue(info.rate['def'])
        rateLayout.addWidget(self.rateSpinbox)

        delayLayout = QHBoxLayout(objectName='DelayLayout')
        measureLayout.addLayout(delayLayout, 5, 0, 1, 1)

        self.delayLabel = QLabel(measureWidget,
                                 text=info.delay['txt'][info.idx],
                                 objectName='DelayLabel')
        delayLayout.addWidget(self.delayLabel)

        self.delaySpinbox = QDoubleSpinBox(measureWidget,
                                           objectName='DelaySpinBox')
        self.delaySpinbox.setRange(info.delay['lim'][0],
                                   info.delay['lim'][-1])
        self.delaySpinbox.setValue(info.delay['def'])
        delayLayout.addWidget(self.delaySpinbox)

        pulseWidthLayout = QHBoxLayout(objectName='PulseWidthLayout')
        measureLayout.addLayout(pulseWidthLayout, 6, 0, 1, 1)

        self.pulseWidthLabel = QLabel(
            measureWidget, text=info.width['txt'][info.idx],
            objectName='PulseWidthLabel')
        pulseWidthLayout.addWidget(self.pulseWidthLabel)

        self.pulseWidthSpinbox = QDoubleSpinBox(measureWidget,
                                                objectName='PulseWidthSpinBox')
        if info.width['lim'] is not None:
            self.pulseWidthSpinbox.setRange(info.width['lim'][0],
                                            info.width['lim'][-1])
        pulseWidthLayout.addWidget(self.pulseWidthSpinbox)

        countLayout = QHBoxLayout(objectName='CountLayout')
        measureLayout.addLayout(countLayout, 7, 0, 1, 1)

        self.countLabel = QLabel(measureWidget,
                                 text=info.count['txt'][info.idx],
                                 objectName='CountLabel')
        countLayout.addWidget(self.countLabel)

        self.countSpinbox = QSpinBox(measureWidget, objectName='CountSpinBox')
        if info.idx in (1, 2):
            self.countSpinbox.setRange(info.points['lim'][0],
                                       info.points['lim'][-1])
            self.countSpinbox.setValue(info.points['def'])
        elif info.idx in (3, 4):
            self.countSpinbox.setRange(info.sweeps['lim'][0],
                                       info.sweeps['lim'][-1])
            self.countSpinbox.setValue(info.sweeps['def'])
        countLayout.addWidget(self.countSpinbox)

        self.lowMeasCheckbox = QCheckBox(measureWidget, text='Low Measure',
                                         objectName='LowMeasCheckBox')
        measureLayout.addWidget(self.lowMeasCheckbox,
                                1, 1, 1, 1, QtCore.Qt.AlignHCenter)
        if info.idx > 1:
            self.lowMeasCheckbox.setChecked(info.low_meas['def'])

        self.filterCheckbox = QCheckBox(measureWidget, text='Filter on',
                                        objectName='FilterCheckBox')
        measureLayout.addWidget(self.filterCheckbox,
                                4, 1, 1, 1, QtCore.Qt.AlignRight)
        self.filterCheckbox.setChecked(info.filt['ondef'])

        filterTypeLayout = QHBoxLayout(objectName='FilterTypeLayout')
        measureLayout.addLayout(filterTypeLayout, 5, 1, 1, 1)

        filterTypeLabel = QLabel(measureWidget, text='Filter Type:',
                                 objectName='FilterTypeLabel',
                                 alignment=QtCore.Qt.AlignRight)
        filterTypeLayout.addWidget(filterTypeLabel)

        self.filterTypeCombobox = QComboBox(measureWidget,
                                            objectName='FilterTypeComboBox')
        self.filterTypeCombobox.addItems(info.filt['labels'])
        filterTypeLayout.addWidget(self.filterTypeCombobox)

        filterWindowLayout = QHBoxLayout(objectName='FilterWindowLayout')
        measureLayout.addLayout(filterWindowLayout, 6, 1, 1, 1)

        filterWindowLabel = QLabel(measureWidget, text='Filter Window:',
                                   objectName='FilterWindowLabel',
                                   alignment=QtCore.Qt.AlignRight)
        filterWindowLayout.addWidget(filterWindowLabel)

        self.filterWindowSpinbox = QDoubleSpinBox(
            measureWidget, objectName='FilterWindowSpinBox')
        self.filterWindowSpinbox.setRange(info.fwindow['lim'][0],
                                          info.fwindow['lim'][-1])
        self.filterWindowSpinbox.setValue(info.fwindow['def'])
        self.filterWindowSpinbox.setToolTip('EXPLANATORY TOOLTIP HERE')
        # TODO: Add tooltip
        filterWindowLayout.addWidget(self.filterWindowSpinbox)

        filterCountLayout = QHBoxLayout(objectName='FilterCountLayout')
        measureLayout.addLayout(filterCountLayout, 7, 1, 1, 1)

        filterCountLabel = QLabel(measureWidget, text='Filter Count:',
                                  objectName='FilterCountLabel',
                                  alignment=QtCore.Qt.AlignRight)
        filterCountLayout.addWidget(filterCountLabel)

        self.filterCountSpinbox = QSpinBox(measureWidget,
                                           objectName='FilterCountSpinBox')
        self.filterCountSpinbox.setRange(info.fcount['lim'][0],
                                         info.fcount['lim'][-1])
        self.filterCountSpinbox.setValue(info.fcount['def'])
        self.filterCountSpinbox.setToolTip('EXPLANATORY TOOLTIP HERE')
        # TODO: Add tooltip
        filterCountLayout.addWidget(self.filterCountSpinbox)

        centralLayout.addWidget(lowerFrame)
        self.armButton = QPushButton(lowerFrame, text='Arm',
                                     objectName='ArmButton')
        lowerLayout.addWidget(self.armButton, 0, 0, 1, 1)
        self.startButton = QPushButton(lowerFrame, text='Start',
                                       objectName='StartButton')
        self.startButton.setCheckable(True)
        self.startButton.setChecked(False)
        lowerLayout.addWidget(self.startButton, 0, 1, 1, 1)

    def closeEvent(self, event) -> None:
        """Determine what to do when the window is closed."""
        widgetList = QtWidgets.QApplication.topLevelWidgets()
        numWindows = len(widgetList)
        if numWindows > 1:
            event.ignore()
        else:
            event.accept()


class Ui_MagnetWindow(Ui_MainWindow):
    """Contains UI for setting magnet parameters and ramping magnet.

    Inherits from Ui_MainWindow.

    attributes_
        configFile: QLineEdit for path to configuration file.
        configLoadButton: QPushButton for loading configuration files.
        configSaveButton: QPushButton for saving configuration files.
        mMeasureCheckbox: QCheckBox to enable/disable measuring magnetic field.
        addressSpinbox: QSpinBox for magnet COM address.
        fieldUnitCombobox: QComboBox for selecting field units.
        timeUnitCombobox: QComboBox for selecting time units.
        segmentsSpinbox: QSpinBox for selecting number of ramp segments.
        setpointsLabel: QLabel for magnet setpoints.
        setpointsButton: QPushButton to open dialog to enter magnet setpoints.
        ratesLabel: QLabel for ramp rates element.
        ratesButton: QPushButton to open dialog to enter magnet ramp rates.
        holdLabel: QLabel for hold times element.
        holdButton: QPushButton to open dialog to enter magnet hold times.
        quenchDetCheckbox: QCheckBox for enabling/disabling quench detect.
        quenchTempSpinbox: QDoubleSpinBox for magnet quench temperature.
        voltLimitSpinbox: QDoubleSpinBox for magnet voltage limit setting.
        currLimitSpinbox: QDoubleSpinBox for magnet current limit setting.
        zeroButton: QPushButton for zeroing magnet.
        # TODO: If using, enter rampdown stuff.
        mCalibrationFile: QLineEdit for calibration file path.
        calibrationLoadButton: QPushButton for loading magnet calibration.
        setButton: QPushButton for setting parameters.
        startButton: QPushButton for starting a ramp.

    methods_
        setupUi(QMainWindow)
    """

    def __init__(self):
        super().__init__()

    def setupUi(self, MagWindow) -> None:
        """Set up UI window for magnet control."""
        (centralWidget, centralLayout) = super().setupUi(MagWindow)
        MagWindow.setWindowTitle('AMI 430 Magnet Power Supply Programmer')
        MagWindow.resize(300, 300)

        (topFrame, topLayout) = self.add_top(centralWidget)
        centralLayout.addWidget(topFrame)

        configFrame = QFrame(topFrame, objectName='ConfigFrame')
        topLayout.addWidget(configFrame, 0, 0, 1, 1)
        (configLayout, self.configFile, self.configLoadButton,
         self.configSaveButton) = self.add_config(configFrame)

        (paramWidget, paramLayout) = self.add_param(centralWidget)
        centralLayout.addWidget(paramWidget)

        (lowerFrame, lowerLayout) = self.add_lower(centralWidget)

        fidx = minfo.field['unit']['def']
        tidx = minfo.time['unit']['def']

        self.mMeasureCheckbox = QCheckBox(topFrame,
                                          text='Record magnetic field',
                                          objectName='mMeasureCheckBox')
        topLayout.addWidget(self.mMeasureCheckbox, 1, 0, 1, 1)

        COMLabel = QLabel(paramWidget, text='COM Address',
                          objectName='COMLabel')
        paramLayout.addWidget(COMLabel, 0, 0, 1, 1)
        self.COMSpinbox = QSpinBox(paramWidget, objectName='COMSpinBox')
        self.COMSpinbox.setRange(minfo.addr['lim'][0], minfo.addr['lim'][-1])
        self.COMSpinbox.setValue(minfo.addr['def'])
        paramLayout.addWidget(self.COMSpinbox, 0, 1, 1, 1)

        self.targetLabel = QLabel(paramWidget, text='Target TEXT',
                                  objectName='TargetLabel')
        paramLayout.addWidget(self.targetLabel, 1, 0, 1, 1)

        self.targetSpinbox = QDoubleSpinBox(paramWidget,
                                            objectName='TargetSpinBox')
        self.targetSpinbox.setRange(-minfo.field['lim'][fidx],
                                    minfo.field['lim'][fidx])
        self.targetSpinbox.setValue(minfo.field['def'][fidx])
        paramLayout.addWidget(self.targetSpinbox, 1, 1, 1, 1)

        fieldUnitLabel = QLabel(paramWidget, text='Field Units',
                                objectName='FieldUnitLabel')
        paramLayout.addWidget(fieldUnitLabel, 2, 0, 1, 1)

        # TODO: Test fieldUnitCombobox to ensure proper items added
        unit_list = [minfo.field['unit']['Full'][i]
                     for i in range(len(minfo.coil_const))]
        self.fieldUnitCombobox = QComboBox(paramWidget,
                                           objectName='FieldUnitComboBox')
        self.fieldUnitCombobox.addItems(unit_list)
        # self.fieldUnitCombobox.addItem('Kilogauss')
        # self.fieldUnitCombobox.addItem('Tesla')
        # self.fieldUnitCombobox.addItem('Amps')
        paramLayout.addWidget(self.fieldUnitCombobox, 2, 1, 1, 1)

        timeUnitLabel = QLabel(paramWidget, text='Time Units',
                               objectName='TimeUnitLabel')
        paramLayout.addWidget(timeUnitLabel, 3, 0, 1, 1)

        # TODO: test timeUnitCombobox to ensure proper items added
        self.timeUnitCombobox = QComboBox(paramWidget,
                                          objectName='TimeUnitComboBox')
        self.timeUnitCombobox.addItems([minfo.time['unit']['Full'][i]
                                        for i in (0, 1)])
        # self.timeUnitCombobox.addItem('Seconds')
        # self.timeUnitCombobox.addItem('Minutes')
        paramLayout.addWidget(self.timeUnitCombobox, 3, 1, 1, 1)

        segmentsLabel = QLabel(paramWidget, text='Ramp Segments',
                               objectName='SegmentsLabel')
        paramLayout.addWidget(segmentsLabel, 4, 0, 1, 1)

        self.segmentsSpinbox = QSpinBox(paramWidget,
                                        objectName='SegmentsSpinBox')
        self.segmentsSpinbox.setRange(minfo.seg['lim'][0],
                                      minfo.seg['lim'][-1])
        paramLayout.addWidget(self.segmentsSpinbox, 4, 1, 1, 1)

        self.setpointsLabel = QLabel(paramWidget, text='Ramp Setpoints UNIT',
                                     objectName='SetpointsLabel')
        paramLayout.addWidget(self.setpointsLabel, 5, 0, 1, 1)

        self.setpointsButton = QPushButton(paramWidget, text='List',
                                           objectName='SetpointsButton')
        # TODO: Set tooltip for SetpointsButton
        self.setpointsButton.setToolTip('A TOOLTIP')
        paramLayout.addWidget(self.setpointsButton, 5, 1, 1, 1)

        rate_txt = (f"{minfo.rate['txt'][1]}"
                    + f"{minfo.field['unit']['Abbv'][fidx]}/"
                    + f"{minfo.time['unit']['Abbv'][tidx]}")
        self.ratesLabel = QLabel(paramWidget, text=f"{rate_txt}",
                                 objectName='RatesLabel')
        paramLayout.addWidget(self.ratesLabel, 6, 0, 1, 1)

        self.ratesButton = QtWidgets.QPushButton(paramWidget, text='List',
                                                 objectName='RatesButton')
        paramLayout.addWidget(self.ratesButton, 6, 1, 1, 1)

        # ???: Initialize holdLabel properly
#        self.holdLabel = QLabel(paramWidget, text='Ramp hold times UNIT',
#                                objectName='HoldLabel')
        # ???: Determine if hold times label text needs to update
#        paramLayout.addWidget(self.holdLabel, 7, 0, 1, 1)

#        self.holdButton = QPushButton(paramWidget, text='List',
#                                      objectName='HoldButton')
#        paramLayout.addWidget(self.holdButton, 7, 1, 1, 1)

        self.quenchDetCheckbox = QCheckBox(paramWidget, text='Quench Detect',
                                           objectName='QuenchDetCheckBox')
        paramLayout.addWidget(self.quenchDetCheckbox, 7, 0, 1, 1)
        self.quenchDetCheckbox.setChecked(minfo.quench['def'])

        quenchTempLayout = QHBoxLayout(objectName='QuenchTempLayout')
        paramLayout.addLayout(quenchTempLayout, 7, 1, 1, 1)

#        quenchTempLabel = QLabel(paramWidget, text='Quench Temperature (K)',
#                                 objectName='QuenchTempLabel')
#        quenchTempLayout.addWidget(quenchTempLabel)

#        self.quenchTempSpinbox = QDoubleSpinBox(paramWidget,
#                                                objectName='QuenchTempSpinBox')
#        self.quenchTempSpinbox.setRange(0.0, 8.0)
#        self.quenchTempSpinbox.setSingleStep(0.1)
#        self.quenchTempSpinbox.setValue(6.5)
#        self.quenchTempSpinbox.setToolTip(
#            'Temperature at which software will assert a quench.  '
#           'Set to 0.0 to disable this functionality, otherwise, keep '
#           'between 4.0 and 8.0.  Having this enabled will cause software '
#           'to measure inner rad shield temperatures during the ramp.  '
#           'These temperatures will not be recorded.')
#        quenchTempLayout.addWidget(self.quenchTempSpinbox)

        voltLimitLabel = QLabel(paramWidget, text='Voltage Limit (V)',
                                objectName='VoltLimitLabel')
        paramLayout.addWidget(voltLimitLabel, 8, 0, 1, 1)

        self.voltLimitSpinbox = QDoubleSpinBox(paramWidget,
                                               objectName='VoltLimitSpinBox')
        # TODO: determine if can change argument to mlims.volt
        self.voltLimitSpinbox.setRange(minfo.volt['lim'][0],
                                       minfo.volt['lim'][1])
        self.voltLimitSpinbox.setValue(minfo.volt['def'])
        paramLayout.addWidget(self.voltLimitSpinbox, 8, 1, 1, 1)

        currLimitLabel = QLabel(paramWidget, text='Current limit (A)',
                                objectName='CurrLimitLabel')
        paramLayout.addWidget(currLimitLabel, 9, 0, 1, 1)

        self.currLimitSpinbox = QDoubleSpinBox(paramWidget,
                                               objectName='CurrLimitSpinBox')
        # TODO: Figure out if can set argument to mlims.curr
        self.currLimitSpinbox.setRange(minfo.curr['lim'][0],
                                       minfo.curr['lim'][1])
        self.currLimitSpinbox.setValue(minfo.curr['def'])
        paramLayout.addWidget(self.currLimitSpinbox, 9, 1, 1, 1)

        self.zeroButton = QPushButton(paramWidget, text='Zero Magnet',
                                      objectName='ZeroButton')
        paramLayout.addWidget(self.zeroButton, 10, 0, 1, 1)

        # TODO: Determine if using rampdown at all
        # rampdownLayout = QHBoxLayout(objectName='RampdownLayout')
        # paramLayout.addLayout(rampdownLayout, 10, 1, 1, 1)

        # TODO: Determine if using rampdown at all (probably no?)
        # self.rampdownLabel = QLabel(paramWidget, text='Rampdown rate (A/s)',
        #                             objectName='RampdownLabel')
        # TODO: Figure out if units need to update
        # rampdownLayout.addWidget(self.rampdownLabel)

        # self.rampdownSpinbox = QDoubleSpinBox(paramWidget,
        #                                       objectName='RampdownSpinBox')
        # TODO: Figure out max and min values
#        self.rampdownSpinbox.setRange
        # self.rampdownSpinbox.setValue()
        # rampdownLayout.addWidget(self.rampdownSpinbox)

        mCalibrationFileLabel = QLabel(paramWidget,
                                       text='Magnet Calibration file:',
                                       objectName='MCalibrationFileLabel')
        paramLayout.addWidget(mCalibrationFileLabel, 11, 0, 1, 1)

        mCalibrationLayout = QHBoxLayout(objectName='MCalibrationLayout')
        paramLayout.addLayout(mCalibrationLayout, 11, 1, 1, 1)

        self.mCalibrationFile = QLineEdit(paramWidget,
                                          objectName='MCalibrationFile')
        mCalibrationLayout.addWidget(self.mCalibrationFile)

        self.mCalibrationLoadButton = QPushButton(
            paramWidget, text='Load', objectName='MCalibrationLoadButton')
        mCalibrationLayout.addWidget(self.mCalibrationLoadButton)

        centralLayout.addWidget(lowerFrame)

        self.setButton = QPushButton(lowerFrame, text='Set',
                                     objectName='SetButton')
        lowerLayout.addWidget(self.setButton)

        self.startButton = QPushButton(lowerFrame, text='Start',
                                       objectName='StartButton')
        self.startButton.setCheckable(True)
        self.startButton.setChecked(False)
        lowerLayout.addWidget(self.startButton)


class Ui_TempWindow(Ui_MainWindow):
    """UI for setting temperature parameters and ramping temperature.

    attributes_
        configFile: QLineEdit for YAML config file path.
        configLoadButton: QPushButton for loading YAML configuration files.
        configSaveButton: QPushButton for saving instrument configuration.
        tMeasureCheckbox: QCheckBox for enabling/disabling data recording.
        GPIBSpinbox: QSpinBox for GPIB address.
        measuredTempCombobox: QComboBox for selecting which temperatures to
            measure.
        radControlCheckbox: QCheckBox for enabling magnet/rad shield control.
        radSetpointSpinbox: QDoubleSpinBox for magnet/rad shield temperature.
        radRampSpinbox: QDoubleSpinBox for magnet/rad shield ramp rate.
        radPowerSpinbox: QSpinBox for magnet/rad shield heater power setting.
        stageControlCheckbox: QCheckBox for enabling stage temperature control.
        stageSetpointSpinbox: QDoubleSpinBox for setting stage temperature.
        stageRampSpinbox: QDoubleSpinBox for setting stage ramp rate.
        stagePowerSpinbox: QSpinBox for setting stage heater power.
        setButton: QPushButton for setting temperature parameters.
        runButton: QPushButton for starting a temperature ramp.

    methods_
        setupUi(QMainWindow)
    """

    def __init__(self):
        super().__init__()

    def setupUi(self, TempWindow) -> None:
        """Generate the UI for the temperature window."""
        (centralWidget, centralLayout) = super().setupUi(TempWindow)
        TempWindow.setWindowTitle("LakeShore 336 Temperature Controller")
        TempWindow.resize(300, 300)

        (topFrame, topLayout) = self.add_top(centralWidget)
        centralLayout.addWidget(topFrame)

        configFrame = QFrame(topFrame, objectName='ConfigFrame')
        topLayout.addWidget(configFrame, 0, 0, 1, 1)
        (configLayout, self.configFile, self.configLoadButton,
         self.configSaveButton) = self.add_config(configFrame)

        (paramWidget, paramLayout) = self.add_param(centralWidget)
        centralLayout.addWidget(paramWidget)

        (lowerFrame, lowerLayout) = self.add_lower(centralWidget)
        centralLayout.addWidget(lowerFrame)

        self.tMeasureCheckbox = QCheckBox(topFrame, text='Record Temperature',
                                          objectName='tMeasureCheckBox')
        topLayout.addWidget(self.tMeasureCheckbox, 1, 0, 1, 1)

        GPIBLabel = QLabel(paramWidget, text='GPIB address',
                           objectName='GPIBLabel')
        paramLayout.addWidget(GPIBLabel, 0, 0, 1, 1)

        self.GPIBSpinbox = QSpinBox(paramWidget, objectName='GPIBSpinBox')
        self.GPIBSpinbox.setToolTip('GPIB address of LakeShore 336')
        self.GPIBSpinbox.setRange(tlims.addr[0], tlims.addr[-1])
        self.GPIBSpinbox.setValue(tlims.addr_default)
        paramLayout.addWidget(self.GPIBSpinbox, 0, 1, 1, 1)

        measuredTempLabel = QLabel(paramWidget, text='Temperatures to measure',
                                   objectName='MeasuredTempLabel')
        paramLayout.addWidget(measuredTempLabel, 1, 0, 1, 1)

        self.measuredTempCombobox = QComboBox(paramWidget,
                                              objectName='MeasuredTempComboBox'
                                              )
        self.measuredTempCombobox.addItem('Controlled')
        self.measuredTempCombobox.addItem('All')
        paramLayout.addWidget(self.measuredTempCombobox, 1, 1, 1, 1)

        self.radControlCheckbox = QCheckBox(
            paramWidget, text='Control rad shield/magnet temperature',
            objectName='RadControlCheckBox')
        paramLayout.addWidget(self.radControlCheckbox, 2, 0, 1, 1)

        radSetpointLabel = QLabel(paramWidget,
                                  text='Rad shield/magnet setpoint (K)',
                                  objectName='RadSetpointLabel')
        paramLayout.addWidget(radSetpointLabel, 3, 1, 1, 1)

        self.radSetpointSpinbox = QDoubleSpinBox(
            paramWidget, objectName='RadSetpointSpinBox')
        self.radSetpointSpinbox.setRange(tlims.setpt[0], tlims.setpt[1])
        self.radSetpointSpinbox.setValue(tlims.setpt_default)
        paramLayout.addWidget(self.radSetpointSpinbox, 3, 2, 1, 1)

        radRampLabel = QLabel(paramWidget,
                              text='Rad shield/magnet ramp rate (K/min)',
                              objectName='RadRampLabel')
        paramLayout.addWidget(radRampLabel, 4, 1, 1, 1)

        self.radRampSpinbox = QDoubleSpinBox(paramWidget,
                                             objectName='RadRampSpinBox')
        self.radRampSpinbox.setRange(tlims.rate[2], tlims.rate[1])
        self.radRampSpinbox.setSingleStep(tlims.rate[0])
        self.radRampSpinbox.setValue(tlims.rate_default)
        self.radRampSpinbox.setToolTip(
            'Rad shield/magnet temperature ramp rate in K/min')
        paramLayout.addWidget(self.radRampSpinbox, 4, 2, 1, 1)

        radPowerLabel = QLabel(paramWidget,
                               text='Rad shield/heater power setting',
                               objectName='RadPowerLabel')
        paramLayout.addWidget(radPowerLabel, 5, 1, 1, 1)

        self.radPowerCombobox = QComboBox(paramWidget,
                                          objectName='RadPowerComboBox')
        self.radPowerCombobox.addItem('Off')
        self.radPowerCombobox.addItem('Low')
        self.radPowerCombobox.addItem('Medium')
        self.radPowerCombobox.addItem('High')
        paramLayout.addWidget(self.radPowerCombobox, 5, 2, 1, 1)

        # self.radPowerSpinbox = QSpinBox(paramWidget,
        #                                 objectName='RadPowerSpinBox')
        # self.radPowerSpinbox.setToolTip(
        #         '0 = off, 1 = low, 2 = medium, 3 = high')
        # self.radPowerSpinbox.setRange(tlims.heatmode[0], tlims.heatmode[-1])

        # paramLayout.addWidget(self.radPowerSpinbox, 5, 2, 1, 1)

        self.stageControlCheckbox = QCheckBox(paramWidget,
                                              text='Control stage temperature',
                                              objectName='StageControlCheckBox'
                                              )
        paramLayout.addWidget(self.stageControlCheckbox, 6, 0, 1, 1)

        stageSetpointLabel = QLabel(paramWidget, text='Stage setpoint (K)',
                                    objectName='StageSetpointLabel')
        paramLayout.addWidget(stageSetpointLabel, 7, 1, 1, 1)

        self.stageSetpointSpinbox = QDoubleSpinBox(
            paramWidget, objectName='StageSetpointSpinBox')
        self.stageSetpointSpinbox.setRange(tlims.setpt[0], tlims.setpt[1])
        self.stageSetpointSpinbox.setValue(tlims.setpt_default)
        paramLayout.addWidget(self.stageSetpointSpinbox, 7, 2, 1, 1)

        stageRampLabel = QLabel(paramWidget, text='Stage ramp rate (K/min',
                                objectName='StageRampLabel')
        paramLayout.addWidget(stageRampLabel, 8, 1, 1, 1)

        self.stageRampSpinbox = QDoubleSpinBox(paramWidget,
                                               objectName='stageRampSpinBox')
        self.stageRampSpinbox.setToolTip(
                'Ramp rate for the sample stage temperature in K/min')
        self.stageRampSpinbox.setRange(tlims.rate[2], tlims.rate[1])
        self.stageRampSpinbox.setSingleStep(tlims.rate[0])
        self.stageRampSpinbox.setValue(tlims.rate_default)
        paramLayout.addWidget(self.stageRampSpinbox, 8, 2, 1, 1)

        stagePowerLabel = QLabel(paramWidget, text='Heater power setting',
                                 objectName='StagePowerLabel')
        paramLayout.addWidget(stagePowerLabel, 9, 1, 1, 1)

        self.stagePowerCombobox = QComboBox(paramWidget,
                                            objectName='StagePowerComboBox')
        self.stagePowerCombobox.addItem('Off')
        self.stagePowerCombobox.addItem('Low')
        self.stagePowerCombobox.addItem('Medium')
        self.stagePowerCombobox.addItem('High')
        paramLayout.addWidget(self.stagePowerCombobox, 9, 2, 1, 1)

        # self.stagePowerSpinbox = QSpinBox(paramWidget,
        #                                   objectName='StagePowerSpinBox')
        # self.stagePowerSpinbox.setRange(0, 3)
        # self.stagePowerSpinbox.setToolTip(
        #         '0 = off, 1 = low, 2 = medium, 3 = high')
        # paramLayout.addWidget(self.stagePowerSpinbox, 9, 2, 1, 1)

        self.setButton = QPushButton(lowerFrame, text='Set',
                                     objectName='SetButton')
        lowerLayout.addWidget(self.setButton, 0, 0, 1, 1)

        self.runButton = QPushButton(lowerFrame, text='Ramp',
                                     objectName='RunButton')
        self.runButton.setCheckable(True)
        self.runButton.setChecked(False)
        lowerLayout.addWidget(self.runButton, 0, 1, 1, 1)

        self.stopButton = QPushButton(lowerFrame, text='Stop',
                                      objectName='StopButton')
        lowerLayout.addWidget(self.stopButton, 0, 2, 1, 1)


class Ui_SelectWindow(Ui_MainWindow):
    """Contains UI for selecting which measurement windows to open.

    attributes_
        keithleyButton: QPushButton for toggling Keithley control.
        magnetButton: QPushButton for toggling magnet control.
        tempButton: QPushButton for toggling temperature control.

    methods_
        setupUi(QMainWindow)
    """

    def setupUi(self, SelectWindow) -> None:
        """Generate the UI for the measurement select window."""
        (centralWidget, centralLayout) = super().setupUi(SelectWindow)
        SelectWindow.setWindowTitle("Instruments Controlled")
        SelectWindow.resize(300, 100)

        self.keithleyButton = QPushButton(centralWidget,
                                          text='Keithley 6221/2182a',
                                          objectName='KeithleyButton')
        self.keithleyButton.setCheckable(True)
        self.keithleyButton.setChecked(False)
        centralLayout.addWidget(self.keithleyButton)

        self.magnetButton = QPushButton(centralWidget,
                                        text='AMI 430 Magnet Power Supply',
                                        objectName='MagnetButton')
        self.magnetButton.setCheckable(True)
        self.magnetButton.setChecked(False)
        centralLayout.addWidget(self.magnetButton)

        self.tempButton = QPushButton(
            centralWidget, text='LakeShore 336 Temperature Controller',
            objectName='TemperatureButton')
        self.tempButton.setCheckable(True)
        self.tempButton.setChecked(False)
        centralLayout.addWidget(self.tempButton)


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     PlotWindow = QtWidgets.QMainWindow()
#     Ui_PlotWindow().setupUi(PlotWindow)
#     PlotWindow.show()

    # KeithWindow = QtWidgets.QMainWindow()
    # Ui_KeithWindow().setupUi(KeithWindow)
    # KeithWindow.show()
#
    # MagWindow = QtWidgets.QMainWindow()
    # Ui_MagnetWindow().setupUi(MagWindow)
    # MagWindow.show()

# TempWindow looks perfect
    # TempWindow = QtWidgets.QMainWindow()
    # Ui_TempWindow().setupUi(TempWindow)
    # TempWindow.show()

# SelectWindow looks perfect
    # SelectWindow = QtWidgets.QMainWindow()
    # Ui_SelectWindow().setupUi(SelectWindow)
    # SelectWindow.show()

    # sys.exit(app.exec_())
