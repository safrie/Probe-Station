#!/usr/bin/env python
# coding=utf-8

"""
main.py contains the overarching logic for the probe station program.

Contained in this module is logic for interfacing between the software, the
instruments, and the UI.  It sets up the UI and then allows the user to control
measurement settings through the UI, by loading a configuration file, or by
putting commands into a terminal.  The program directs the running of the
measurement, collects data from the instruments, and plots and saves them.

classes_
    Window: Structure for grouping QMainWindow, UI, and signals and slots for
        the various windows ProbeGUI opens.
    ProbeGui: Contains the logic for running pretty much everything

methods_
    main()

Part of the V3 probe station collection.
@author: Sarah Friedensen
"""
import sys
# import os
# import time
# import re
# import pyqtgraph as pg

# from pathlib import Path
# import inspect
from ruamel_yaml import YAML
from qtpy import QtGui, QtWidgets, QtCore
from qtpy.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QMainWindow
# from qtpy.QtGui import QFileDialog, QMessageBox, QInputDialog, QMainWindow
from typing import Union, Optional, List, Dict
from pathlib import Path

from design import (Ui_PlotWindow, Ui_KeithWindow, Ui_TempWindow,
                    Ui_MagnetWindow, Ui_SelectWindow)
from file_io import Save, Config
from LakeShore_336.temperature import Temp
from Keithley2182a_6221.keith import Keith
from AMI_430.magnet import Mag
from limits import (KeithInfo as kinfo, TempInfo as tinfo, MagInfo as minfo,
                    key, ivinfo)


def no():
    """Do nothing as a placeholder."""
    pass


class Window():
    """Logically groups UI elements for easy access.

    attributes_
        window: A QMainWindow that the user will actually see
        ui: The collection of design elements that go in that window
        signals_slots: The dictionary that connects UI actions to results

    methods_
        __init__(QMainWindow, class instance)
    """

    def __init__(self, window, ui) -> None:
        """Initialize the window and call setupUi if it exists."""
        self.window = window
        self.ui = ui
        if hasattr(self.ui, 'setupUi'):
            self.ui.setupUi(self.window)
        self.signals_slots = {}

    # def eventFilter(self, source, event):
    #     """Print close events, hopefully tell us who called it."""
    #     if event.type() == QtCore.QEvent.Close:
    #         title = source.windowTitle()
    #         print(f'Title = {title}')
    #         print(super(Window, self).eventFilter(source, event))


class ProbeGui(QMainWindow):
    """Contains the logic for running the entire program.

    For connecting signals and slots, the following options are available:
        'combo': Comboboxes.  Disabled at start of measurement.  Signal is
            currentIndexChanged.
        'field': Fields/spinboxes in which to type/enter settings.  Set to
            'Read Only' at start of measurement.  Signal is editingFinished.
        'button1': Buttons set to do nothing during measurement (e.g., arm or
            start buttons).  Signal is clicked.
        'button2': Buttons set to remain active during measurement (e.g., stop
            button).  Signal is clicked.
        'checkbox': Checkboxes set to 'setCheckable(False)' during measurement.
            Signal is clicked.

    # TODO: MORE DESCRIPTION

    attributes_
        yaml: YAML object for processing configuration files
        save: Save object for handling/saving data
        config: Config object for handling configuration files
        keith: Keith object for controlling the Keithley stack
        temp: Temp object for controlling the LakeShore336 controller
        mag: Mag object for controlling the magnet
        list_box: QInputDialog for accepting lists of parameters


        plwind: Window object for the plotting window interface
        swind: Window object for the select window interface

        kwind: Window object for the Keithley control interface
        keith_ui_internal: Dict connecting main.py methods (which connect to
            the UI) to Keith methods (which connect to the instruments)
        keith_ui_modify: Dispatch dict for loading UI designs corresponding to
            the different IV measurement types

        twind: Window object for the temperature control interface
        temp_ui_internal: Dict connecting main.py methods (connect to UI) to
            Temp methods (which connect to the controller)

        mwind: Window object for the magnet control interface
        mag_ui_internal: Dict connecting main.py methods (connect to UI) to
            Mag methods (connect to controller)

    methods_
        __init__()
        init_ui(object)
        init_plwind()
        init_swind()

        init_kwind()
        toggle_kwind(opt bool)
        set_keith_address(opt int)
        set_keith_meas_type(opt int/str)
        set_keith_unit(opt int)
        set_keith_source_range_type(opt int/str)
        set_keith_source_range(opt int/float/str)
        set_keith_compliance(opt float)
        set_keith_compliance_abort(opt bool)
        TODO: Determine typing on set_keith_volt_range
        set_keith_volt_range(something?)
        set_keith_curr1(opt float, opt int)
        set_keith_curr2(opt float, opt int)
        set_keith_curr_step(opt float, opt int)
        set_keith_curr_delta(opt float, opt int)
        set_keith_meas_rate(opt int/float, opt int)
        set_keith_meas_delay(opt float, opt int)
        set_keith_pulse_width(opt float, opt int)
        set_keith_num_points(opt int, opt int)
        set_keith_num_sweeps(opt int, opt int)
        set_keith_low_meas(opt bool, opt int)
        set_keith_filter(opt bool, opt int)
        set_keith_filter_type(opt int/str, opt int)
        set_keith_filter_window(opt float, opt int)
        set_keith_filter_count(opt int, opt int)
        arm_keith()
        start_keith()
        stop_keith()
        update_keith_ui(opt bool)
        update_keith_values()
        update_keith_text()
        keith_ui_diffcon()
        keith_ui_delta()
        keith_ui_pdelta()
        keith_ui_pdelt_stair()
        update_keith_source_minmax(float)
        toggle_keith_for_run(bool)

        init_twind()
        toggle_twind(opt bool)
        set_temp_address(opt int)
        set_temp_measure(opt bool)
        set_temp_rad_control(opt bool)
        set_temp_rad_setpoint(opt float)
        set_temp_rad_ramp(opt float)
        set_temp_rad_power(opt int)
        set_temp_stage_control(opt bool)
        set_temp_stage_setpoint(opt float)
        set_temp_stage_ramp(opt float)
        set_temp_stage_power(opt int)
        set_temp_to_measure(opt int/str)
        set_temp_pars()
        start_temp()
        stop_temp()
        update_temp_ui(opt bool)
        toggle_temp_for_run(bool)

        init_mwind()
        toggle_mwind(opt bool)
        set_mag_address(opt int)
        set_mag_measure(opt bool)
        set_mag_target(opt float)
        set_mag_field_unit(opt int/str)
        set_mag_time_unit(opt int/str)
        set_mag_segments(opt int)
        set_mag_ramp_setpoints(opt list)
        set_mag_ramp_rates(opt list)
        set_mag_quench_detect(opt bool)
        # set_mag_quench_temp(opt float)
        set_mag_volt_limit(opt float)
        set_mag_curr_limit(opt float)
        set_mag_zero(opt bool)
        load_mag_calibration(opt str)
        update_mag_labels(opt int, opt int)
        update_mag_ui()

        update_from_config(opt str, opt str)
        load_keith_config(dict)
        get_keith_config()
        load_temp_config(dict)
        get_temp_config()
        load_mag_config(dict)
        get_mag_config()

    """

    # yaml = YAML()
    # save = Save()
    # config = Config()
    # keith = Keith()
    # temp = Temp()
    # mag = Mag()

    def __init__(self) -> None:
        """Initialize overarching program and allow for threading."""
        super().__init__()

        self.init_ui()

    def init_ui(self, parent=None) -> None:
        """Initialize the UI and set up inner classs etc."""
        # ???: What does this do??? Why here instead of __init__?
        # ???: Should it be setupUi instead?
        super(ProbeGui, self).__init__(parent)
        self.list_box = QInputDialog()
        self.list_box.setInputMode(0)
        self.save = Save()
        self.config = Config()
        self.keith = Keith()
        self.temp = Temp()
        self.mag = Mag()
        self.init_plwind()
        self.init_swind()
        self.init_kwind()
        self.init_twind()
        self.init_mwind()

    def init_plwind(self) -> None:
        # TODO: Test init_plwind
        """Initialize MainWindow, connect signals/slots, and show."""
        # self.plwind.setupUi(self.plwind_qmw)
        self.plwind = Window(QMainWindow(), Ui_PlotWindow())
        # TODO: Signals and slots
        self.plwind.signals_slots = {}
        self.plwind.window.show()

    def init_swind(self) -> None:
        # TODO: Test init_swind
        """Initialize Select Window, connect signals/slots, and show."""
        self.swind = Window(QMainWindow(), Ui_SelectWindow())
        ui = self.swind.ui
        # self.swind.setupUi(self.swind_qmw)
        self.swind.signals_slots = {
                    ui.keithleyButton: self.toggle_kwind,
                    ui.magnetButton: self.toggle_mwind,
                    ui.tempButton: self.toggle_twind}
        for k, v in self.swind.signals_slots.items():
            k.clicked.connect(v)
        print('Selectwindow initialized')
        self.swind.window.show()
# %% Keithley section

    def init_kwind(self) -> None:
        # TODO: Test init_kwind
        """Initialize Keithley window; connect signals and slots."""
        self.kwind = Window(QMainWindow(), Ui_KeithWindow())
        ui = self.kwind.ui
        (keith, meas) = (self.keith, self.keith.meas_type())
        # kwind.setupUi(self.kwind.window)
        self.kwind.signals_slots = {
            'combo': {
                ui.measureTypeCombobox: self.set_keith_meas_type,
                ui.unitsCombobox: self.set_keith_unit,
                ui.sourceRangeTypeCombobox: self.set_keith_source_range_type,
                ui.sourceRangeCombobox: self.set_keith_source_range,
                ui.meterRangeCombobox: self.set_keith_volt_range,
                ui.filterTypeCombobox: self.set_keith_filter_type
                      },
            'field': {
                ui.GPIBSpinbox: self.set_keith_address,
                ui.complianceSpinbox:  self.set_keith_compliance,
                ui.current1Spinbox: self.set_keith_curr1,
                ui.current2Spinbox: self.set_keith_curr2,
                ui.currStepSpinbox: self.set_keith_curr_step,
                ui.field4Spinbox: self.set_keith_field4,
                ui.rateSpinbox:  self.set_keith_meas_rate,
                ui.delaySpinbox: self.set_keith_meas_delay,
                ui.pulseWidthSpinbox: self.set_keith_pulse_width,
                ui.countSpinbox: self.set_keith_num_points,
                ui.filterWindowSpinbox: self.set_keith_filter_window,
                ui.filterCountSpinbox: self.set_keith_filter_count
                        },
            'button1': {
                ui.armButton: self.arm_keith,
                ui.startButton: self.start_keith
                },
            'button2': {},
            'checkbox': {
                # self.ui.kMeasureCheckbox: no,
                ui.CABCheckbox: self.set_keith_compliance_abort,
                ui.lowMeasCheckbox: self.set_keith_low_meas,
                ui.filterCheckbox: self.set_keith_filter}
                }
        for k, v in self.kwind.signals_slots['combo'].items():
            k.currentIndexChanged.connect(v)
        for k, v in self.kwind.signals_slots['field'].items():
            k.editingFinished.connect(v)
        for k, v in self.kwind.signals_slots['button1'].items():
            k.clicked.connect(v)
        for k, v in self.kwind.signals_slots['checkbox'].items():
            k.clicked.connect(v)

        self.keith_ui_internal = {
            self.set_keith_address: keith.address,
            self.set_keith_meas_type: keith.meas_type_idx,
            # self.set_keith_unit: meas.unit_idx,
            self.set_keith_unit: meas.unit,
            self.set_keith_source_range_type: keith.source_range_type_idx,
            self.set_keith_source_range: keith.source_range_idx,
            self.set_keith_compliance: keith.compl_volt,
            self.set_keith_compliance_abort: keith.compl_abort,
            self.set_keith_volt_range: keith.volt_range_idx,
            self.set_keith_curr1: meas.curr1,
            self.set_keith_curr2: meas.curr2,
            self.set_keith_curr_step: meas.curr_step,
            self.set_keith_curr_delta: meas.curr_delta,
            self.set_keith_meas_rate: meas.meas_rate,
            self.set_keith_meas_delay: meas.meas_delay,
            self.set_keith_pulse_width: meas.pulse_width,
            self.set_keith_num_points: meas.num_points,
            self.set_keith_num_sweeps: meas.num_sweeps,
            self.set_keith_low_meas: meas.low_meas,
            self.set_keith_filter: meas.filter_on,
            self.set_keith_filter_type: meas.filter_idx,
            self.set_keith_filter_window: meas.filter_window,
            self.set_keith_filter_count: meas.filter_count}

        self.keith_ui_modify = {0: self.keith_ui_diffcon,
                                1: self.keith_ui_delta,
                                2: self.keith_ui_pdelta,
                                3: self.keith_ui_pdelt_stair,
                                4: self.keith_ui_pdelt_log}

    def toggle_kwind(self, enable: Optional[bool] = None) -> None:
        # TODO: Test toggle_kwind, especially block=False
        # TODO: Test to see if need to alter close_event to make invisible to
        # make this work.
        """Toggle visibility of the Keithley window."""
        if enable is not None:
            self.kwind.window.setVisible(enable)
        else:
            self.kwind.window.setVisible(not self.kwind.window.isVisible())
        if self.kwind.window.isVisible():
            self.update_keith_ui(block=False)

    def set_keith_address(self, addr: Optional[int] = None) -> None:
        # TODO: Test set_keith_address
        """Set the Keithleys' GPIB address to addr or UI value."""
        spinbox = self.kwind.ui.GPIBSpinbox
        keith = self.keith
        if addr is not None:
            # addr = keith.set_address(addr)
            keith.address = addr
            spinbox.setValue(keith.address)
        else:
            # keith.set_address(spinbox.value())
            keith.address = spinbox.value()
        d1 = {self.set_keith_address: keith.address}
        self.keith_ui_internal.update(d1)

    def set_keith_meas_type(self,
                            idx: Optional[Union[int, str]] = None) -> None:
        # TODO: Test set_keith_meas_type
        """Set the Keithley IV measurement type."""
        ui = self.kwind.ui
        keith = self.keith
        if idx is None:
            idx = ui.measureTypeCombobox.currentIndex()
        idx, meas = keith.set_meas_type(idx)
        ui.measureTypeCombobox.setCurrentIndex(idx)
        # if idx is not None:
        #     if isinstance(idx, str):
        #         dic = kinfo.meas['txt']
        #         idx = key(dic=dic, val=idx)
        #     ui.measureTypeCombobox.setCurrentIndex(idx)
        # else:
        #     idx = ui.measureTypeCombobox.currentIndex()
        # meas = keith.set_meas_type(idx)
        # ui.unitsCombobox.setCurrentIndex(meas.unit_idx)
        ui.unitsCombobox.setCurrentIndex(meas.unit)
        rate = (meas.meas_rate if hasattr(meas, 'meas_rate') else
                meas.cycle_int if hasattr(meas, 'cycle_int') else
                meas.cycle_time if hasattr(meas, 'cycle_time') else None)

        d1 = {self.set_keith_meas_type: keith.meas_type_idx,
              # self.set_keith_unit: meas.unit_idx,
              self.set_keith_unit: meas.unit,
              self.set_keith_curr1: meas.curr1,
              self.set_keith_curr2: meas.curr2,
              self.set_keith_num_points: meas.num_points,
              self.set_keith_meas_rate: rate,
              self.set_keith_filter: meas.filter_on,
              self.set_keith_filter_type: meas.filter_idx,
              self.set_keith_filter_window: meas.filter_window,
              self.set_keith_filter_count: meas.filter_count}

        dlist = ([{self.set_keith_curr_step: meas.curr_step}] if
                 hasattr(meas, 'curr_step') else [])
        dlist.extend([{self.set_keith_curr_delta: meas.curr_delta}] if
                     hasattr(meas, 'curr_delta') else [])
        dlist.extend([{self.set_keith_meas_delay: meas.meas_delay}] if
                     hasattr(meas, 'meas_delay') else [])
        dlist.extend([{self.set_keith_pulse_width: meas.pulse_width}] if
                     hasattr(meas, 'pulse_width') else [])
        dlist.extend([{self.set_keith_num_sweeps: meas.num_sweeps}] if
                     hasattr(meas, 'num_sweeps') else [])
        dlist.extend([{self.set_keith_low_meas: meas.low_meas}] if
                     hasattr(meas, 'low_meas') else [])

        for d in dlist:
            d1.update(d)
        self.keith_ui_internal.update(d1)
        self.keith_ui_modify[idx]()

    def set_keith_unit(self, idx: Optional[int] = None,
                       meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_unit
        """Set the units for the current IV measurement type."""
        combobox = self.kwind.ui.unitsCombobox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if idx is not None:
            keith.set_unit(idx, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                combobox.setCurrentIndex(idx)
        else:
            keith.set_unit(combobox.currentIndex(), meas_idx)
        # d1 = {self.set_keith_unit: meas.unit_idx}
        d1 = {self.set_keith_unit: meas.unit}
        self.keith_ui_internal.update(d1)

    def set_keith_source_range_type(
            self, val: Optional[Union[int, str]] = None) -> None:
        # TODO: Test set_keith_source_range_type
        """Set the 6221 range type to "Best" (0) or "Fixed" (1)."""
        keith = self.keith
        combobox = self.kwind.ui.sourceRangeTypeCombobox
        if val is not None:
            idx = keith.set_source_range_type(val)
            combobox.setCurrentIndex(idx)
        else:
            idx = keith.set_source_range_type(combobox.currentIndex())
        self.update_keith_source_minmax(
            keith.source_range_minmax(keith.source_range_idx))
        d1 = {self.set_keith_source_range_type: idx}
        self.keith_ui_internal.update(d1)
        self.keith_ui_modify[keith.meas_type_idx]()

    def set_keith_source_range(
            self, val: Optional[Union[int, float, str]] = None) -> None:
        # TODO: Test set_keith_source_range
        """Set the Keithley 6221 current source range and update labels."""
        keith = self.keith
        combobox = self.kwind.ui.sourceRangeCombobox
        if val is not None:
            idx = keith.set_source_range(val)
            combobox.setCurrentIndex(idx)
        else:
            idx = keith.set_source_range(combobox.currentIndex())
        self.update_keith_source_minmax(keith.source_range_minmax(idx))
        self.update_keith_text()
        d1 = {self.set_keith_source_range: idx}
        self.keith_ui_internal.update(d1)
        self.keith_ui_modify[keith.meas_type_idx]()

    def set_keith_compliance(self, volt: Optional[float] = None) -> None:
        # TODO: Test set_keith_compliance
        """Set compliance voltage for Keithley 6221 current source."""
        spinbox = self.kwind.ui.complianceSpinbox
        keith = self.keith
        if volt is not None:
            keith.set_compl_volt(volt)
            spinbox.setValue(volt)
        else:
            keith.set_compl_volt(spinbox.value())
        d1 = {self.set_keith_compliance: keith.compl_volt}
        self.keith_ui_internal.update(d1)

    def set_keith_compliance_abort(self,
                                   enable: Optional[bool] = None) -> None:
        """Enable/disable compliance abort for Keithley IV measurement."""
        checkbox = self.kwind.ui.CABCheckbox
        keith = self.keith
        if enable is not None:
            keith.set_compl_abort(enable)
            checkbox.setChecked(enable)
        else:
            keith.set_compl_abort(checkbox.isChecked())
        d1 = {self.set_keith_compliance_abort: keith.compl_abort}
        self.keith_ui_internal.update(d1)

    def set_keith_volt_range(self, value=None) -> None:
        """Set the Keithley 2182a range."""
        combobox = self.kwind.ui.meterRangeCombobox
        keith = self.keith
        if value is not None:
            idx = keith.set_volt_range(value)
            combobox.blockSignals(True)
            combobox.setCurrentIndex(idx - 2)
            combobox.blockSignals(False)
        else:
            idx = keith.set_volt_range(combobox.currentIndex())
        d1 = {self.set_keith_volt_range: idx}
        self.keith_ui_internal.update(d1)

    def set_keith_curr1(self, curr: Optional[float] = None,
                        meas_idx: Optional[int] = None) -> None:
        """Set the 1st current for the Keithleys and update UI if needed."""
        spinbox = self.kwind.ui.current1Spinbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if curr is not None:
            keith.set_curr1(curr, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(keith.curr_conv_div(curr))
        else:
            keith.set_curr1(keith.curr_conv_mult(spinbox.value()), meas_idx)
            d1 = {self.set_keith_curr1, meas.curr1}
            self.keith_ui_internal.update(d1)

    def set_keith_curr2(self, curr: Optional[float] = None,
                        meas_idx: Optional[int] = None) -> None:
        """Set the 2nd current for the Keithleys and update UI if needed."""
        spinbox = self.kwind.ui.current2Spinbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if curr is not None:
            keith.set_curr2(curr, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx()):
                spinbox.setValue(keith.curr_conv_div(curr))
        else:
            keith.set_curr2(keith.curr_conv_mult(spinbox.value()), meas_idx)
        d1 = {self.set_keith_curr2: meas.curr2}
        self.keith_ui_internal.update(d1)

    def set_keith_curr_step(self, step: Optional[float] = None,
                            meas_idx: Optional[int] = None) -> None:
        """Set the Keithley current step size and update UI if needed."""
        spinbox = self.kwind.ui.currStepSpinbox
        label = self.kwind.ui.currStepLabel
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if step is not None:
            keith.set_curr_step(step, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(keith.curr_conv_div(step))
        elif label.isVisible():
            keith.set_curr_step(keith.curr_conv_mult(spinbox.value()),
                                meas_idx)
        d1 = {self.set_keith_curr_step: meas.curr_step}
        self.keith_ui_internal.update(d1)

    def set_keith_field4(self, val: Optional[Union[float, int]] = None,
                         meas_idx: Optional[int] = None) -> None:
        """Set field4 in the UI--dispatch to correct function for meas_idx."""
        ui = self.kwind.ui
        print(f"field4 val = {val}")
        if meas_idx is None:
            meas_idx = ui.measureTypeCombobox.currentIndex()

        if meas_idx == 0:
            self.set_keith_curr_delta(delta=val, meas_idx=meas_idx)
            return
        elif meas_idx > 2:
            self.set_keith_num_points(points=val, meas_idx=meas_idx)
            print(f"keith_num_points set to {val}")

    def set_keith_curr_delta(self, delta: Optional[float] = None,
                             meas_idx: Optional[int] = None) -> None:
        """Set differential conductance current delta, update UI if needed."""
        spinbox = self.kwind.ui.field4Spinbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if delta is not None:
            keith.set_curr_delta(delta, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(keith.curr_conv_div(delta))
        elif spinbox.isEnabled():
            keith.set_curr_delta(keith.curr_conv_mult(spinbox.value()),
                                 meas_idx)
        d1 = {self.set_keith_curr_delta: meas.curr_delta}
        self.keith_ui_internal.update(d1)

    def set_keith_meas_rate(self, rate: Optional[Union[int, float]] = None,
                            meas_idx: Optional[int] = None) -> None:
        """Set measurement rate/cycle interval and update UI if necessary."""
        # TODO: Test set_keith_meas_rate
        spinbox = self.kwind.ui.rateSpinbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if rate is not None:
            keith.set_meas_rate(rate, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(rate)
        else:
            keith.set_meas_rate(spinbox.value(), meas_idx)
        d1 = {self.set_keith_meas_rate: meas.meas_rate}
        self.keith_ui_internal.update(d1)

    def set_keith_meas_delay(self, delay: Optional[float] = None,
                             meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_meas_delay
        """Set the measurement delay and update UI if needed."""
        spinbox = self.kwind.ui.delaySpinbox
        label = self.kwind.ui.delayLabel
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if delay is not None:
            keith.set_meas_delay(delay, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(delay / 1e-3)
        elif label:
            keith.set_meas_delay(spinbox.value() * 1e-3, meas_idx)
        d1 = {self.set_keith_meas_delay: meas.meas_delay}
        self.keith_ui_internal.update(d1)

    def set_keith_pulse_width(self, width: Optional[float] = None,
                              meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_pulse_width
        """Set the pulse width of the measurement and update UI if needed."""
        (spinbox, label) = (self.kwind.ui.pulseWidthSpinbox,
                            self.kwind.ui.pulseWidthLabel)
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if width is not None:
            keith.set_pulse_width(width, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(width)
        elif label:
            keith.set_pulse_width(spinbox.value(), meas_idx)
        d1 = {self.set_keith_pulse_width: meas.pulse_width}
        self.keith_ui_internal.update(d1)

    def set_keith_num_points(self, points: Optional[int] = None,
                             meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_num_points
        """Set number of points in the measurement and update UI if needed."""
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        index = keith.meas_type_idx if meas_idx is None else meas_idx
        spinbox = (self.kwind.ui.countSpinbox if index < 3
                   else self.kwind.ui.field4SpinBox)
        if points is not None:
            # TODO: Why is points = int(points) here? form loading?
            points = int(points)
            keith.set_num_points(points, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(points)
        else:
            keith.set_num_points(spinbox.value(), meas_idx)
        d1 = {self.set_keith_num_points: meas.num_points}
        self.keith_ui_internal.update(d1)

    def set_keith_num_sweeps(self, sweeps: Optional[int] = None,
                             meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_num_sweeps
        """Set the number of sweeps and update UI if needed."""
        spinbox = self.kwind.ui.countSpinbox
        label = self.kwind.ui.countLabel
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        index = keith.meas_type_idx if meas_idx is None else meas_idx
        if sweeps is not None:
            keith.set_num_sweeps(sweeps, meas_idx)
            if ((meas_idx is None or meas_idx == keith.meas_type_idx)
                    and index > 2):
                spinbox.setValue(sweeps)
        elif label.text() == 'Number Sweeps':
            keith.set_num_sweeps(spinbox.value(), meas_idx)
        d1 = {self.set_keith_num_sweeps: meas.num_sweeps}
        self.keith_ui_internal.update(d1)

    def set_keith_low_meas(self, enable: Optional[bool] = None,
                           meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_low_meas
        """Toggle 2nd low measurement an update UI if needed."""
        checkbox = self.kwind.ui.lowMeasCheckbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if enable is not None:
            keith.set_low_meas(enable, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                checkbox.setChecked(enable)
        elif checkbox.isEnabled():
            keith.set_low_meas(checkbox.isChecked(), meas_idx)
        d1 = {self.set_keith_low_meas: meas.low_meas}
        self.keith_ui_internal.update(d1)

    def set_keith_filter(self, enable: Optional[bool] = None,
                         meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_filter
        """Toggle IV filtering and update UI if needed."""
        checkbox = self.kwind.ui.filterCheckbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if enable is not None:
            keith.set_filter(enable, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                checkbox.setChecked(enable)
        else:
            keith.set_filter(checkbox.isChecked(), meas_idx)
        d1 = {self.set_keith_filter: meas.filter_on}
        self.keith_ui_internal.update(d1)

    def set_keith_filter_type(self, ftype: Optional[Union[int, str]] = None,
                              meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_filter_type
        """Set IV mathematical filter type and update UI if needed."""
        combobox = self.kwind.ui.filterTypeCombobox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if ftype is not None:
            keith.set_filter_idx(ftype, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                combobox.setCurrentIndex(keith.filter_index(ftype))
        else:
            keith.set_filter_idx(combobox.currentIndex(), meas_idx)
        d1 = {self.set_keith_filter_type: meas.filter_idx}
        self.keith_ui_internal.update(d1)

    def set_keith_filter_window(self, window: Optional[float] = None,
                                meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_filter_window and expand docstring
        """Set the IV mathematical filter window and update UI if needed."""
        spinbox = self.kwind.ui.filterWindowSpinbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if window is not None:
            keith.set_filter_window(window, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(window)
        else:
            keith.set_filter_window(spinbox.value(), meas_idx)
        d1 = {self.set_keith_filter_window: meas.filter_window}
        self.keith_ui_internal.update(d1)

    def set_keith_filter_count(self, count: Optional[int] = None,
                               meas_idx: Optional[int] = None) -> None:
        # TODO: Test set_keith_filter_count and expand docstring.
        """Set the filter count and update the UI if needed."""
        spinbox = self.kwind.ui.filterCountSpinbox
        (keith, meas) = (self.keith, self.keith.meas_type(meas_idx))
        if count is not None:
            keith.set_filter_count(count, meas_idx)
            if (meas_idx is None or meas_idx == keith.meas_type_idx):
                spinbox.setValue(count)
        else:
            keith.set_filter_count(spinbox.value(), meas_idx)
        d1 = {self.set_keith_filter_count: meas.filter_count}
        self.keith_ui_internal.update(d1)

    def arm_keith(self) -> None:
        # TODO: Test arm_keith
        """Send VISA commands to Keithleys to arm then disarm a measurement.

        Good for testing your measurement setup.
        """
        armed = self.keith.arm()
        if armed:
            # TODO: Abort just for testing. Delete this after all's good.
            self.keith.visa.write(self.keith.visa.abort_cmd)
            print('Arming worked!')
        else:
            print("Arming didn't work.  Check the error queue.")

    def start_keith(self) -> None:
        # TODO: Test start_keith
        """Send VISA commands to arm and start Keithley measurement."""
        ui = self.kwind.ui
        self.toggle_keith_for_run(True)
        (self.kdata_str, self.ksdata_rows, self.kdata_cols) = self.keith.run()
        self.toggle_keith_for_run(False)
        ui.startButton.setChecked(False)
        print(f'Keithley data length: {len(self.ksdata_rows)}')
        self.save.data(self.kdata_str)

    def stop_keith(self) -> None:
        # TODO: Test stop_keith
        """Halt Keithley measurement.  Will save what data you have."""
        ui = self.kwind.ui
        self.toggle_keith_for_run(False)
        self.keith.stop()
        (self.kdata_str, self.ksdata_rows, self.kdata_cols) = (
                self.keith.get_data())
        print(f'Keithley data length: {len(self.ksdata_rows)}')
        self.krunning = False
        ui.startButton.setChecked(False)
        self.save.data(self.kdata_str)

    def update_keith_ui(self, block: bool = False) -> None:
        # TODO: Test update_keith_ui
        """Update the UI so Keithley values correspond to internal vars."""
        for k, v in self.keith_ui_internal.items():
            if not (block and k.__name__ == 'set_keith_volt_range'):
                k(v)

    def update_keith_values(self) -> None:
        # TODO: Test update_keith_values
        """Update Keithley UI elements to reflect internal values."""
        (ui, keith, meas) = (self.kwind.ui, self.keith, self.keith.meas_type())
        ui.current1Spinbox.setValue(keith.curr_conv_div(meas.curr1))
        ui.current2Spinbox.setValue(keith.curr_conv_div(meas.curr2))
        if ui.currStepSpinbox.isVisible():
            ui.currStepSpinbox.setValue(keith.curr_conv_div(meas.curr_step))
        if ui.field4Spinbox.isVisible():
            if 'Delta Current' in ui.field4Label.text():
                ui.field4Spinbox.setValue(keith.curr_conv_div(meas.curr_delta))
            elif 'Number Points' in ui.field4Label.text():
                ui.field4Spinbox.setValue(meas.num_points)
        if 'Rate' in ui.rateLabel.text():
            ui.rateSpinbox.setValue(meas.meas_rate)
        elif 'Interval' in ui.rateLabel.text():
            ui.rateSpinbox.setValue(meas.cycle_int)
        elif 'Time' in ui.rateLabel.text():
            ui.rateSpinbox.setValue(meas.cycle_time)
        if ui.delaySpinbox.isVisible():
            ui.delaySpinbox.setValue(meas.meas_delay)
        if ui.pulseWidthSpinbox.isVisible():
            ui.pulseWidthSpinbox.setValue(meas.pulse_width)
        if ui.countSpinbox.isVisible():
            if 'Pulse Count' in ui.countLabel.text():
                ui.countSpinbox.setValue(meas.num_points)
            elif 'Number Sweeps' in ui.countLabel.text():
                ui.countSpinbox.setValue(meas.num_sweeps)
        ui.filterCheckbox.setChecked(meas.filter_on)
        # TODO: Set filter type maybe?
        ui.filterCountSpinbox.setValue(meas.filter_count)
        ui.filterWindowSpinbox.setValue(meas.filter_window)
        if ui.lowMeasCheckbox.isVisible():
            ui.lowMeasCheckbox.setChecked(meas.low_meas)

    def update_keith_text(self) -> None:
        """Update UI labels for a different measurement type or range."""
        ui = self.kwind.ui
        keith = self.keith
        idx = keith.meas_type_idx
        info = ivinfo['dic'][idx]()
        ui.current1Label.setText(keith.curr1_text(idx))
        ui.current2Label.setText(keith.curr2_text(idx))
        ui.currStepLabel.setText(keith.curr_step_text(idx))
        ui.field4Label.setText(keith.field4_text(idx))
        ui.rateLabel.setText(info.rate['txt'][idx])
        ui.delayLabel.setText(info.delay['txt'][idx])
        ui.pulseWidthLabel.setText(info.width['txt'][idx])
        ui.countLabel.setText(info.count['txt'][idx])

    def keith_ui_diffcon(self) -> None:
        # TODO: Test keith_ui_diffcon
        """Update UI for requisite inputs for differential conductance."""
        ui = self.kwind.ui
        idx = key(kinfo.meas['txt'], "diffCond")
        info = ivinfo['dic'][idx]()
        self.update_keith_text()
        ui.currStepSpinbox.show()
        ui.field4Spinbox.show()
        ui.field4Spinbox.setReadOnly(False)
        # TODO: Verify that set_keith_field4 works so we can get rid of below.
        # ui.field4Spinbox.editingFinished.disconnect()
        # ui.field4Spinbox.editingFinished.connect(self.set_keith_curr_delta)
        ui.rateSpinbox.setDecimals(info.rate['decim'][idx])
        ui.rateSpinbox.setRange(info.rate['lim'][0], info.rate['lim'][-1])
        ui.delaySpinbox.show()
        ui.delaySpinbox.setRange(info.delay['lim'][0]*1e3,
                                 info.delay['lim'][-1]*1e3)
        ui.pulseWidthSpinbox.hide()
        ui.countSpinbox.hide()
        ui.filterTypeCombobox.setEnabled(True)
        self.set_keith_filter_type(ftype=info.filt['def'])
        ui.filterTypeCombobox.setEnabled(False)
        ui.lowMeasCheckbox.hide()
        self.update_keith_values()

    def keith_ui_delta(self) -> None:
        # TODO: Test keith_ui_delta
        """Update UI for requisite inputs for delta measurement."""
        ui = self.kwind.ui
        idx = key(kinfo.meas['txt'], "delta")
        info = ivinfo['dic'][idx]()
        self.update_keith_text()
        ui.currStepSpinbox.hide()
        ui.field4Spinbox.hide()
        ui.rateSpinbox.setDecimals(info.rate['decim'][idx])
        ui.rateSpinbox.setRange(info.rate['lim'][0], info.rate['lim'][-1])
        ui.delaySpinbox.show()
        ui.delaySpinbox.setRange(info.delay['lim'][0]*1e3,
                                 info.delay['lim'][-1]*1e3)
        ui.pulseWidthSpinbox.hide()
        ui.countSpinbox.show()
        ui.countSpinbox.editingFinished.disconnect()
        ui.countSpinbox.editingFinished.connect(self.set_keith_num_points)
        ui.filterTypeCombobox.setEnabled(True)
        self.set_keith_filter_type(meas_idx=idx)
        ui.lowMeasCheckbox.hide()
        self.update_keith_values()

    def keith_ui_pdelta(self) -> None:
        # TODO: Test keith_ui_pdelta
        """Update UI for requisite inputs for pulse delta measurement."""
        ui = self.kwind.ui
        idx = key(kinfo.meas['txt'], "delta")
        info = ivinfo['dic'][idx]()
        self.update_keith_text()
        ui.currStepSpinbox.hide()
        ui.field4Spinbox.hide()
        ui.delaySpinbox.show()
        ui.delaySpinbox.setRange(info.delay['lim'][0]*1e6,
                                 info.delay['lim'][1]*1e6)
        ui.rateSpinbox.setDecimals(info.rate['decim'][idx])
        ui.rateSpinbox.setRange(info.rate['lim'][0], info.rate['lim'][-1])
        ui.pulseWidthSpinbox.show()
        ui.countSpinbox.show()
        ui.countSpinbox.editingFinished.disconnect()
        ui.countSpinbox.editingFinished.connect(self.set_keith_num_points)
        ui.filterTypeCombobox.setEnabled(True)
        self.set_keith_filter_type(meas_idx=idx)
        ui.lowMeasCheckbox.show()
        self.update_keith_values()

    def keith_ui_pdelt_stair(self) -> None:
        # TODO: Test keith_ui_pdelt_stair.
        """Update UI for requisite inputs for pulse delta stair sweep."""
        ui = self.kwind.ui
        self.update_keith_text()
        idx = key(kinfo.meas['txt'], "sweepPulseDeltaStair")
        info = ivinfo['dic'][idx]()
        ui.currStepSpinbox.show()
        ui.field4Spinbox.show()
        ui.field4Spinbox.setReadOnly(True)
        # ui.field4Spinbox.editingFinished.disconnect()
        # ui.field4Spinbox.editingFinished.connect(self.set_keith_num_points)
        ui.rateSpinbox.setDecimals(info.rate['decim'][idx])
        ui.rateSpinbox.setRange(info.rate['lim'][0]*1e3,
                                info.rate['lim'][-1]*1e3)
        ui.delaySpinbox.show()
        ui.delaySpinbox.setRange(info.delay['lim'][0]*1e6,
                                 info.delay['lim'][-1]*1e-6)
        ui.pulseWidthSpinbox.show()
        ui.countSpinbox.show()
        ui.countSpinbox.editingFinished.disconnect()
        ui.countSpinbox.editingFinished.connect(self.set_keith_num_sweeps)
        ui.filterTypeCombobox.setEnabled(True)
        self.set_keith_filter_type(ftype=info.filt['def'])
        ui.filterTypeCombobox.setEnabled(False)
        ui.lowMeasCheckbox.show()
        self.update_keith_values()

    def keith_ui_pdelt_log(self) -> None:
        # TODO: Test keith_ui_pdelt_log
        """Update UI for requisite inputs for pulse delta log sweep."""
        ui = self.kwind.ui
        self.update_keith_text()
        idx = key(kinfo.meas['txt'], "sweepPulseDeltaLog")
        info = ivinfo['dic'][idx]()
        ui.currStepSpinbox.hide()
        ui.field4Spinbox.show()
        ui.field4Spinbox.setReadOnly(False)
        # TODO: Verify main.set_keith_field4 works so not changing signal ok
        # ui.field4Spinbox.editingFinished.disconnect()
        # ui.field4Spinbox.editingFinished.connect(self.set_keith_num_points)
        ui.rateSpinbox.setDecimals(info.rate['decim'][idx])
        ui.rateSpinbox.setRange(info.rate['lim'][0]*1e3,
                                info.rate['lim'][-1]*1e3)
        ui.delaySpinbox.show()
        ui.delaySpinbox.setRange(info.delay['lim'][0]*1e6,
                                 info.delay['lim'][-1]*1e6)
        ui.pulseWidthSpinbox.show()
        ui.countSpinbox.show()
        ui.countSpinbox.editingFinished.disconnect()
        ui.countSpinbox.editingFinished.connect(self.set_keith_num_sweeps)
        ui.filterTypeCombobox.setEnabled(True)
        self.set_keith_filter_type(ftype=info.filt['def'])
        ui.filterTypeCombobox.setEnabled(False)
        ui.lowMeasCheckbox.show()
        self.update_keith_values()

    def update_keith_source_minmax(self, bound: float) -> None:
        # TODO: Test update_keith_source_minmax
        """Update min and max allowed current values based on source range.

        If "Best" ranging is selected, maximum is 100 mA.
        """
        ui = self.kwind.ui
        idx = self.keith.meas_type_idx
        (keith, meas) = (self.keith, self.keith.meas_type())
        max_A = (keith.curr_conv_mult(bound) if keith.source_range_type_idx
                 else list(kinfo.sour_range['dic'])[-1])
        max_sb_curr = keith.curr_conv_div(max_A)  # Max current for spinbox
        max_points = kinfo().points['lim'][-1]
        (curr1, curr2) = (meas.curr1, meas.curr2)
        step = meas.curr_step if hasattr(meas, 'curr_step') else None
        delta = meas.curr_delta if hasattr(meas, 'curr_delta') else None
        points = meas.num_points

        if curr1 > max_A:
            self.set_keith_curr1(max_A)
        elif curr1 < -max_A:
            self.set_keith_curr1(-max_A)

        if curr2 > max_A:
            self.set_keith_curr2(max_A)
        elif curr2 < -max_A:
            self.set_keith_curr2(-max_A)

        if step is not None:
            if step > max_A:
                self.set_keith_curr_step(max_A)
            elif step < 0:
                self.set_keith_curr_step(0)

        if idx:  # Measurement type is not differential conductance
            if points > max_points:
                self.set_keith_points(max_points)
            elif points < 1:
                self.set_keith_points(1)
        else:
            if delta > max_A:
                self.set_keith_curr_delta(max_A)
            elif delta < 0:
                self.set_keith_curr_delta(0)

        if keith.source_range_type_idx:  # Fixed range
            ui.current1Spinbox.setRange(-bound, bound)
            ui.current2Spinbox.setRange(-bound, bound)
            ui.currStepSpinbox.setRange(0, bound)
            f4range = (1, max_points) if idx else (0, bound)
            ui.field4Spinbox.setRange(f4range[0], f4range[1])
        else:
            ui.current1Spinbox.setRange(-max_sb_curr, max_sb_curr)
            ui.current2Spinbox.setRange(-max_sb_curr, max_sb_curr)
            ui.currStepSpinbox.setRange(-max_sb_curr, max_sb_curr)
            f4range = (1, max_points) if idx else (0, bound)
            ui.field4Spinbox.setRange(f4range[0], f4range[1])

    def toggle_keith_for_run(self, running: bool) -> None:
        # TODO: Test toggle_keith_for_run
        """Enable/disable Keithley UI based on if measurement running."""
        for k, v in self.kwind.signals_slots['combo'].items():
            k.setEnabled(not running)
        for k, v in self.kwind.signals_slots['field'].items():
            k.setReadOnly(running)
        for k, v in self.kwind.signals_slots['button1'].items():
            k.blockSignals(running)
        for k, v in self.kwind.signals_slots['checkbox'].items():
            k.setCheckable(not running)
        self.krunning = running

# %% Temperature section

    def init_twind(self) -> None:
        """Initialize Temperature Control window; connect signals/slots.

        Please note that most temperature methods will not direclty command the
        LakeShore 336 over GPIB.  This is because writing the commands will
        cause them to execute immediately.  The dev thinks it would be better
        to set up the ramp you want and then hit 'start' to begin execution.
        """
        # TODO: Test init_twind
        self.twind = Window(QMainWindow(), Ui_TempWindow())
        (temp, ui) = (self.temp, self.twind.ui)
        # Note that the fields for temperature will remain editable during
        # a ramp because of time reasons.
        self.twind.signals_slots = {
            'combo': {ui.measuredTempCombobox: self.set_temp_to_measure,
                      ui.radPowerCombobox: self.set_temp_rad_power,
                      ui.stagePowerCombobox: self.set_temp_stage_power},
            'field': {ui.GPIBSpinbox: self.set_temp_address,
                      ui.radSetpointSpinbox: self.set_temp_rad_setpoint,
                      ui.radRampSpinbox: self.set_temp_rad_ramp,
                      # ui.radPowerCombobox: self.set_temp_rad_power,
                      ui.stageSetpointSpinbox: self.set_temp_stage_setpoint,
                      ui.stageRampSpinbox: self.set_temp_stage_ramp,
                      # ui.stagePowerSpinbox: self.set_temp_stage_power
                      },
            'button1': {},
            # TODO: Connect runButton.
            'button2': {ui.setButton: self.set_temp_pars,
                        ui.runButton: self.start_temp},
            'checkbox': {ui.tMeasureCheckbox: self.set_temp_measure,
                         ui.radControlCheckbox: self.set_temp_rad_control,
                         ui.stageControlCheckbox: self.set_temp_stage_control}
            }

        for k, v in self.twind.signals_slots['combo'].items():
            k.currentIndexChanged.connect(v)
        for k, v in self.twind.signals_slots['field'].items():
            k.editingFinished.connect(v)
        for k, v in self.twind.signals_slots['button2'].items():
            k.clicked.connect(v)
        for k, v in self.twind.signals_slots['checkbox'].items():
            k.clicked.connect(v)

        self.temp_ui_internal = {
            self.set_temp_address: temp.address,
            self.set_temp_measure: temp.measure,
            self.set_temp_rad_control: temp.rad_control,
            self.set_temp_rad_setpoint: temp.rad_setpoint,
            self.set_temp_rad_ramp: temp.rad_ramp,
            self.set_temp_rad_power: temp.rad_power,
            self.set_temp_stage_control: temp.stage_control,
            self.set_temp_stage_setpoint: temp.stage_setpoint,
            self.set_temp_stage_ramp: temp.stage_ramp,
            self.set_temp_stage_power: temp.stage_power,
            self.set_temp_to_measure: temp.to_measure_idx}

    def toggle_twind(self, enable: Optional[bool] = None) -> None:
        """Toggle visibility of the temperature control window."""
        # TODO: Test toggle_twind
        # TODO: Test to see if need to alter close_event to make invisible to
        # make this work.
        window = self.twind.window
        if enable is not None:
            window.setVisible(enable)
        else:
            window.setVisible(not window.isVisible())
        if window.isVisible():
            self.update_temp_ui()

    def set_temp_address(self, addr: Optional[int] = None) -> None:
        """Set GPIB address of temperature controller to addr or UI value."""
        # TODO: Test set_temp_address
        (temp, spinbox) = (self.temp, self.twind.ui.GPIBSpinbox)
        if addr is not None:
            # addr = temp.set_address(addr)
            # spinbox.setValue(addr)
            temp.address(addr)
            spinbox.setValue(temp.address)
        else:
            # addr = temp.set_address(spinbox.value())
            temp.address(spinbox.value())
        d1 = {self.set_temp_address: temp.address}
        self.temp_ui_internal.update(d1)

    def set_temp_measure(self, enable: Optional[bool] = None) -> None:
        # TODO: Test set_temp_measure
        """Enables/disables temperature measurement recording during a ramp.

        Note that measurement is independent of control; you can run a ramp
        without saving any data.
        """
        temp, checkbox = self.temp, self.twind.ui.tMeasureCheckbox
        if enable is not None:
            temp.set_measure(enable)
            checkbox.setChecked(enable)
        else:
            temp.set_measure(checkbox.isChecked())
        d1 = {self.set_temp_measure: temp.measure}
        self.temp_ui_internal.update(d1)

    def set_temp_rad_control(self, enable: Optional[bool] = None) -> None:
        """Enable/disable rad shield temperature control."""
        # TODO: test set_temp_rad_control
        (temp, checkbox) = (self.temp, self.twind.ui.radControlCheckbox)
        if enable is not None:
            temp.set_rad_control(enable)
            checkbox.setChecked(enable)
        else:
            temp.set_rad_control(checkbox.isChecked())
        d1 = {self.set_temp_rad_control: temp.rad_control}
        self.temp_ui_internal.update(d1)

    def set_temp_rad_setpoint(self, setpt: Optional[float] = None) -> None:
        """Set the rad shield temperature setpoint to setpt or UI value."""
        # TODO: Test set_temp_rad_setpoint
        (temp, spinbox) = (self.temp, self.twind.ui.radSetpointSpinbox)
        if setpt is not None:
            setpt = temp.set_setpoint(setpt, 'rad')
            spinbox.setValue(setpt)
        else:
            setpt = temp.set_setpoint(spinbox.value(), 'rad')
        d1 = {self.set_temp_rad_setpoint: setpt}
        self.temp_ui_internal.update(d1)

    def set_temp_rad_ramp(self, rate: Optional[float] = None) -> None:
        """Set the ramp rate for the temperature of the rad shield."""
        # TODO: Test set_rad_rap
        temp, spinbox = self.temp, self.twind.ui.radRampSpinbox
        if rate is not None:
            rate = temp.set_ramp(rate, 'rad')
            spinbox.setValue(rate)
        else:
            rate = temp.set_ramp(spinbox.value(), 'rad')
        d1 = {self.set_temp_rad_ramp: rate}
        self.temp_ui_internal.update(d1)

    def set_temp_rad_power(self, power: Optional[int] = None) -> None:
        """Set the rad shield heater power to power or UI value."""
        # TODO: Test set_temp_rad_power
        temp, combobox = self.temp, self.twind.ui.radPowerCombobox
        if power is not None:
            power = temp.set_power(power, 'rad')
            combobox.setCurrentIndex(power)
        else:
            power = temp.set_power(combobox.currentIndex(), 'rad')
        d1 = {self.set_temp_rad_power: power}
        self.temp_ui_internal.update(d1)

    def set_temp_stage_control(self, enable: Optional[bool] = None) -> None:
        """Enable/disable temperature control of the stage."""
        # TODO: Test set_temp_stage_control
        temp, checkbox = self.temp, self.twind.ui.stageControlCheckbox
        if enable is not None:
            temp.set_stage_control(enable)
            checkbox.setChecked(enable)
        else:
            temp.set_stage_control(checkbox.isChecked())
        d1 = {self.set_temp_stage_control: temp.stage_control}
        self.temp_ui_internal.update(d1)

    def set_temp_stage_setpoint(self, setpt: Optional[float] = None) -> None:
        """Set the stage temperature setpoint to setpt or UI value."""
        # TODO: Test set_temp_stage_setpoint
        temp, spinbox = self.temp, self.twind.ui.stageSetpointSpinbox
        if setpt is not None:
            setpt = temp.set_setpoint(setpt, 'stage')
            spinbox.setValue(setpt)
        else:
            setpt = temp.set_setpoint(spinbox.value(), 'stage')
        d1 = {self.set_temp_stage_setpoint: setpt}
        self.temp_ui_internal.update(d1)

    def set_temp_stage_ramp(self, rate: Optional[float] = None) -> None:
        """Set the ramp rate for the temperature of the stage."""
        # TODO: Test set_temp_stage_ramp
        temp, spinbox = self.temp, self.twind.ui.stageRampSpinbox
        if rate is not None:
            rate = temp.set_ramp(rate, 'stage')
            spinbox.setValue(rate)
        else:
            rate = temp.set_ramp(spinbox.value(), 'stage')
        d1 = {self.set_temp_stage_ramp: rate}
        self.temp_ui_internal.update(d1)

    def set_temp_stage_power(self, power: Optional[int] = None) -> None:
        """Set the stage heater to power level power."""
        # TODO: Test set_temp_stage_power
        temp, combobox = self.temp, self.twind.ui.stagePowerCombobox
        if power is not None:
            power = temp.set_power(power, 'stage')
            combobox.setCurrentIndex(power)
        else:
            power = temp.set_power(combobox.value(), 'stage')
        d1 = {self.set_temp_stage_power: power}
        self.temp_ui_internal.update(d1)

    def set_temp_to_measure(self,
                            measured: Optional[Union[int, str]] = None
                            ) -> None:
        """Set which temperatures to measure to measured or to UI value."""
        # TODO: Test set_temp_to_measure
        temp, combobox = self.temp, self.twind.ui.measuredTempCombobox
        set = measured if measured is not None else combobox.currentIndex()
        idx = temp.set_to_measure(set)

        if idx is not None:
            if measured is not None:
                combobox.setCurrentIndex(idx)
            d1 = {self.set_temp_to_measure: idx}
            self.temp_ui_internal.update(d1)

    def set_temp_pars(self) -> None:
        """Send temperature parameters to the 336 Controller.

        This method will not enable output while there is not a ramp, but it
        will affect the ramps and setpoints if a ramp is running.
        """
        # TODO: Test set_temp_pars
        self.temp.set_pars()

    def start_temp(self) -> None:
        """Send VISA commands to arm and start temperature ramp/measurement."""
        # TODO: Test start_temp
        # TODO: Make wait longer after testing.
        ui = self.twind.ui
        self.set_temp_pars()
        self.toggle_temp_for_run(True)
        (self.tdata_str, self.tsdata_rows,
         self.tdata_cols) = self.temp.run(wait=10)
        self.toggle_temp_for_run(False)
        ui.startButton.setChecked(False)
        print(f'Temperature data length: {len(self.tsdata_rows)}')
        self.save.data(self.tdata_str)

    def stop_temp(self) -> None:
        # TODO: Test stop_temp
        """Halt Temperature measurement.  Will save what data you have."""
        ui = self.twind.ui
        self.toggle_temp_for_run(False)
        ui.startButton.setChecked(False)
        self.save.data(self.tdata_str)

    def update_temp_ui(self) -> None:
        """Update the UI so temperature values correspond to internal vars."""
        # TODO: Write update_temp_ui
        for k, v in self.temp_ui_internal.items():
            k(v)

    def toggle_temp_for_run(self, running=bool) -> None:
        # TODO: Test toggle_temp_for_run
        """Enable/disable LakeShore336 UI based on if measurement running."""
        for k, v in self.twind.signals_slots['combo'].items():
            k.setEnabled(not running)
        for k, v in self.twind.signals_slots['checkbox'].items():
            k.setCheckable(not running)
        self.twind.ui.GPIBSpinbox.setReadOnly(running)
        self.trunning = running

# %% Magnet section
    def init_mwind(self) -> None:
        """Initialize Magnet Control window; connect signals/slots."""
        self.mwind = Window(QMainWindow(), Ui_MagnetWindow())
        mag, ui = self.mag, self.mwind.ui
        self.update_mag_labels()
        self.mwind.signals_slots = {
            'combo': {
                # Comboboxes.  Disable at start of measurement.
                # Signal is currentIndexChanged.
                # TODO: Determine if using mMeasureCombobox and implement.
                # ui.mMeasureCombobox: self.set_mag_measure,
                ui.fieldUnitCombobox: self.set_mag_field_unit,
                ui.timeUnitCombobox: self.set_mag_time_unit
                },
            'field': {
                # Fields/spinboxes in which to type/enter settings.
                # Set to 'Read Only' at start of measurement.
                # Signal is editingFinished.
                ui.COMSpinbox: self.set_mag_address,
                ui.targetSpinbox: self.set_mag_target,
                ui.segmentsSpinbox: self.set_mag_ramp_segments,
                # ui.quenchTempSpinbox: self.set_mag_quench_temp,
                ui.voltLimitSpinbox: self.set_mag_volt_limit,
                ui.currLimitSpinbox: self.set_mag_curr_limit,
                ui.mCalibrationFile: self.load_mag_calibration
                },
            'button1': {
                # Buttons set to do nothing during measurement.
                # Signal is clicked.
                ui.setpointsButton: self.set_mag_ramp_setpoints,
                ui.ratesButton: self.set_mag_ramp_rates,
                ui.mCalibrationLoadButton: self.load_mag_calibration,
                ui.setButton: self.set_mag_pars,
                ui.startButton: self.start_mag,
                ui.configLoadButton: self.load_mag_config,
                ui.configSaveButton: self.get_mag_config
                },
            'button2': {
                # Buttons set to remain active during measurement.
                # Signal is clicked.
                ui.zeroButton: self.set_mag_zero
                },
            'checkbox': {
                # Checkboxes set to 'setCheckable(False)' during measurement.
                # Signal is clicked.
                ui.mMeasureCheckbox: self.set_mag_measure,
                ui.quenchDetCheckbox: self.set_mag_quench_detect
                }
            }
        for k, v in self.mwind.signals_slots['combo'].items():
            k.currentIndexChanged.connect(v)
        for k, v in self.mwind.signals_slots['field'].items():
            k.editingFinished.connect(v)
        for k, v in self.mwind.signals_slots['button1'].items():
            k.clicked.connect(v)
        for k, v in self.mwind.signals_slots['checkbox'].items():
            k.clicked.connect(v)

        self.mag_ui_internal = {
            self.set_mag_address: mag.address,
            self.set_mag_measure: mag.measure,
            self.set_mag_field_unit: mag.field_unit_idx,
            self.set_mag_time_unit: mag.time_unit_idx,
            self.set_mag_target: mag.target,
            self.set_mag_ramp_segments: mag.ramp_segments,
            self.set_mag_ramp_setpoints: mag.setpoints_list,
            self.set_mag_ramp_rates: mag.ramps_list,
            self.set_mag_quench_detect: mag.quench_detect,
            # self.set_mag_quench_temp: mag.quench_temp,
            self.set_mag_volt_limit: mag.volt_limit,
            self.set_mag_curr_limit: mag.curr_limit,
            # self.set_mag_zero: mag.zero,
            self.load_mag_calibration: mag.calibration_file
            }

    def toggle_mwind(self, enable: Optional[bool] = None) -> None:
        """Toggle visibility of the magnet control window."""
        # TODO: Test toggle_mwind
        window = self.mwind.window
        if enable is not None:
            window.setVisible(enable)
        else:
            window.setVisible(not window.isVisible())
        if window.isVisible():
            self.update_mag_ui()

    def set_mag_address(self, addr: Optional[int] = None) -> None:
        """Set COM address of magnet power supply to addr or UI value."""
        # TODO: Test set_mag_address
        mag, spinbox = self.mag, self.mwind.ui.COMSpinbox
        if addr is not None:
            # addr = mag.set_address(addr)
            # spinbox.setValue(addr)
            mag.address(addr)
            spinbox.setValue(mag.address)
        else:
            # addr = mag.set_address(spinbox.value())
            mag.address(spinbox.value())
        d1 = {self.set_mag_address: mag.address}
        self.mag_ui_internal.update(d1)

    def set_mag_measure(self, enable: Optional[bool] = None) -> None:
        # TODO: Test set_mag_measure
        """Enables/Disables recording magnetic field during a ramp.

        Note this is separate from the question of whether a ramp is occurring.
        """
        mag, checkbox = self.mag, self.mwind.ui.mMeasureCheckbox
        if enable is not None:
            mag.set_measure(enable)
            checkbox.setChecked(enable)
        else:
            mag.set_measure(checkbox.isChecked())
        d1 = {self.set_mag_measure: mag.measure}
        self.mag_ui_internal.update(d1)

    def set_mag_target(self, targ: Optional[float] = None) -> None:
        # TODO: Test set_mag_target
        """Set the target magnetic field or current to targ or UI value."""
        mag, spinbox = self.mag, self.mwind.ui.targetSpinbox
        if targ is not None:
            print(f"targ not none, type = {type(targ)}")
            targ = mag.set_target(targ)
            spinbox.setValue(targ)
        else:
            print(f"targ was None, spin value = {spinbox.value()}")
            targ = mag.set_target(spinbox.value())
        d1 = {self.set_mag_target: targ}
        self.mag_ui_internal.update(d1)

    def set_mag_field_unit(self,
                           idx: Optional[Union[int, str]] = None) -> None:
        # TODO: Test set_mag_field_unit
        """Set field/current unit of magnet power supply to idx or UI value."""
        mag, combobox = self.mag, self.mwind.ui.fieldUnitCombobox
        if idx is not None:
            idx = mag.set_field_unit(idx)
            combobox.setCurrentIndex(idx)
        else:
            idx = mag.set_field_unit(combobox.currentIndex())
        d1 = {self.set_mag_field_unit: idx}
        self.mag_ui_internal.update(d1)
        self.update_mag_labels()

    def set_mag_time_unit(self, idx: Optional[Union[int, str]] = None) -> None:
        # TODO: Test set_mag_time_unit
        """Set the time unit of the magnet power supply to idx or UI value."""
        mag, combobox = self.mag, self.mwind.ui.timeUnitCombobox
        if idx is not None:
            idx = mag.set_time_unit(idx)
            combobox.setCurrentIndex(idx)
        else:
            idx = mag.set_time_unit(combobox.currentIndex())
        d1 = {self.set_mag_time_unit: idx}
        self.mag_ui_internal.update(d1)
        self.update_mag_labels()

    def set_mag_ramp_segments(self, segs: Optional[int] = None) -> None:
        # TODO: Test set_mag_ramp_segments
        """Set the number of ramp segments for magnet to segs or UI value.

        Ramp segments define ranges at which the magnet will have a specified
        ramp rate.  In a two-segment setup, for instance, between 0 and 1 T
        the magnet could have a ramp rate of 0.25 T/min, and between 1 and 3 T
        the magnet could have a ramp rate of 0.1 T/min.  You could then
        institute a ramp from 0.75 T to 3.0 T, and the ramp rates will hold to
        the pattern established by the segments.
        """
        mag, spinbox = self.mag, self.mwind.ui.segmentsSpinbox
        if segs is not None:
            segs = mag.set_ramp_segments(segs)
            spinbox.setValue(segs)
        else:
            segs = mag.set_ramp_segments(spinbox.value())
        d1 = {self.set_mag_ramp_segments: segs}
        self.mag_ui_internal.update(d1)

    def set_mag_ramp_setpoints(self, setpts: Optional[Union[List, str]]
                               = None) -> None:
        # TODO: Test set_mag_ramp_setpoints
        # TODO: Input validation on fields
        """Open dialog box to set magnet ramp setpoints.

        For simplicity in the UI, the setpoints also serve as the ramp segment
        dividers.
        """
        mag = self.mag
        unit, abbv = mag.field_unit('Full'), mag.field_unit('Abbv')
        # unit_type = 'curr' if abbv == 'A' else 'field'
        unit_idx = mag.field_unit_idx
        bounds = (-minfo().field['lim'][unit_idx],
                  minfo().field['lim'][unit_idx])
        if setpts is None:
            title = f"{minfo().field['txt']['setp'][0]} ({abbv})"
            label = (f'Enter your list of magnet ramp setpoints in {unit}.\n'
                     + 'Setpoints should be numbers separated by commas '
                     + '(e.g., 1, 2, 3).\n'
                     + f'Range is {bounds[0]} {abbv} to {bounds[1]} {abbv}.')
            txt = self.list_box.getText(self, title, label)[0]
            (lst, txt) = mag.set_setpoints(txt)
        else:
            (lst, txt) = mag.set_setpoints(setpts)
        d1 = {self.set_mag_ramp_setpoints: lst}
        self.mag_ui_internal.update(d1)
        # if not len(lst) == mag.ramp_segments:
        #     self.set_mag_ramp_segments(len(lst))
        # if len(lst) == len(mag.ramps_list):
        #     print("Setting ramp segments")
        #     for i in range(0, mag.ramp_segments):
        #         mag.visa.set_rate(seg=i, rate=mag.ramps_list[i],
        #                           upbound=lst[i], unit=unit_type)

    def set_mag_ramp_rates(self, ramps: Optional[List] = None) -> None:
        # TODO: Test set_mag_ramp_rates
        """Open dialog box to set magnet ramp rates."""
        mag = self.mag
        fabbv, fidx = mag.field_unit('Abbv'), mag.field_unit_idx
        tabbv, tunit = mag.time_unit('Abbv'), mag.time_unit('Full').lower()
        # unit_type = 'curr' if fabbv == 'A' else 'field'
        bounds = minfo().rate['lim'][tunit][fidx]
        if ramps is None:
            title = f"{minfo().rate['txt'][0]} ({fabbv}/{tabbv})"
            label = (f'Enter list of magnet ramp rates in {fabbv}/{tabbv}.\n'
                     + 'Ramp rates should be numbers separated by commas '
                     + '(e.g., 1, 2, 3).\n'
                     + f'Range is {bounds[0]} {fabbv}/{tabbv} to '
                     + f'{bounds[2]} {fabbv}/{tabbv}.')
            txt = self.list_box.getText(self, title, label)[0]
            (lst, txt) = mag.set_ramps(txt)
        else:
            (lst, txt) = mag.set_ramps(ramps)
        d1 = {self.set_mag_ramp_rates: lst}
        self.mag_ui_internal.update(d1)
        # if len(lst) == len(mag.setpoints_list) == mag.ramp_segments:
        #     print("Setting ramp segments.")
        #     for i in range(0, mag.ramp_segments):
        #         mag.visa.set_rate(seg=i, rate=ramps_list[i],
        #                           upbound=mag.setpoints_list[i],
        #                           unit=unit_type)

    def set_mag_ramp(self, stpts: Optional[list], ramps: Optional[list],
                     segs: Optional[int], typ: Optional[str]):
        mag = self.mag
        stpts = self.mag.setpoints_list if stpts is None else stpts
        ramps = self.mag.ramps_list if ramps is None else ramps
        segs = self.mag.ramp_segments if segs is None else segs
        typ = self.mag.field_type()
        if not len(stpts) == len(ramps):
            print('Number of ramp setpoints and number of ramp rates not '
                  + 'equal.  Please correct.  No ramps set.')
            return
        if not len(stpts) == segs:
            self.set_mag_ramp_segments(len(stpts))
        print("Setting magnet ramp segments.")
        for i in range(0, mag.ramp_segments):
            mag.visa.set_rate(seg=i, rate=ramps[i], upbound=stpts[i],
                              unit=typ)

    def set_mag_quench_detect(self, enable: Optional[bool] = None) -> None:
        # TODO: Test set_mag_quench_det
        """Enable/disable magnet automatic quench detect.

        This quench detect is inherent to the instrument, not the software.
        """
        mag, checkbox = self.mag, self.mwind.ui.quenchDetCheckbox
        if enable is not None:
            mag.set_quench_detect(enable)
            checkbox.setChecked(enable)
        else:
            mag.set_quench_detect(checkbox.isChecked())
        d1 = {self.set_mag_quench_detect: mag.quench_detect}
        self.mag_ui_internal.update(d1)

    # def set_mag_quench_temp(self, temp: Optional[float] = None) -> None:
        # """Set temperature at which software will assert a magnet quench."""
        # mag, spinbox = self.mag, self.mwind.ui.quenchTempSpinbox
        # if temp is not None:
        #     mag.set_quench_temp(temp)
        #     spinbox.setValue(temp)
        # else:
        #     mag.set_quench_temp(spinbox.value())
        # d1 = {self.set_mag_quench_temp: mag.quench_temp}
        # self.mag_ui_internal.update(d1)

    def set_mag_volt_limit(self, limit: Optional[float] = None) -> None:
        # TODO: Test set_mag_volt_limit
        """Set the voltage output limit in V for the magnet."""
        mag, spinbox = self.mag, self.mwind.ui.voltLimitSpinbox
        if limit is not None:
            limit = mag.set_volt_limit(limit)
            spinbox.setValue(limit)
        else:
            limit = mag.set_volt_limit(spinbox.value())
        d1 = {self.set_mag_volt_limit: limit}
        self.mag_ui_internal.update(d1)

    def set_mag_curr_limit(self, limit: Optional[float] = None) -> None:
        # TODO: Test set_mag_curr_limit
        """Set the current output limit in A for the magnet."""
        mag, spinbox = self.mag, self.mwind.ui.currLimitSpinbox
        if limit is not None:
            limit = mag.set_curr_limit(limit)
            spinbox.setValue(limit)
        else:
            limit = mag.set_curr_limit(spinbox.value())
        d1 = {self.set_mag_curr_limit: limit}
        self.mag_ui_internal.update(d1)

    def set_mag_zero(self, enable: Optional[bool] = None) -> None:
        # TODO: Test set_mag_zad
        """Enable/disable Zero After Done (ramp to 0 field after ramp)."""
        mag, checkbox = self.mag, self.mwind.ui.zadCheckbox
        if enable is not None:
            mag.set_zero(enable)
            checkbox.setChecked(enable)
        else:
            mag.set_zero(checkbox.isChecked())
        d1 = {self.set_mag_zero: mag.zero}
        self.mag_ui_internal.update(d1)

    # TODO: Determine if using rampdown rate stuff, and if so, insert here.

    def load_mag_calibration(self, calib: Optional[str] = None) -> None:
        # TODO: Test and complete load_mag_calibration
        """Load a magnet calibration file.  Normally don't do this."""
        mag, calfile = self.mag, self.mwind.ui.mcalibrationFile
        # TODO: Implement input validation on calib
        if calib is None:
            # TODO: Determine proper filetype
            calib = QFileDialog.getOpenFileName(
                    None, 'Load magnet calibration file', '', 'Text (*.txt)')
        mag.set_calibration_file(calib)
        calfile.setText(calib)

    def set_mag_pars(self) -> None:
        # TODO: Test set_mag_pars
        """Send parameters to magnet power supply programmer.

        This method will not enable output while there is not a ramp, but it
        will affect the ramps and setpoints if a ramp is running.
        """
        self.mag.set_pars()

    def start_mag(self) -> None:
        # TODO: Implement and test start_mag
        """Begin magnet ramp and collect data."""
        # ui = self.mwind.ui
        self.set_mag_pars()
        self.toggle_mag_for_run(True)

    def togle_mag_for_run(self, enable: bool, safe: bool = True):
        """Update mag UI to enable/disable elements if ramp in progress.

        The safe variable indicates, when true, that this will not actually
        relay a start command to the magnet.  It is set to True during testing.
        """
        # TODO: Implement this method.

    def update_mag_labels(self, fidx: Optional[int] = None,
                          tidx: Optional[int] = None) -> None:
        # TODO: Test update_mag_labels
        """Update the ramp list labels to correspond to current units."""
        mag, ui = self.mag, self.mwind.ui
        print(fidx)
        if fidx is None:
            fidx = mag.field_unit_idx
        fabbv = (mag.field_unit('Abbv') if fidx is None
                 else minfo().field['unit']['Abbv'][fidx])
        tabbv = (mag.time_unit('Abbv') if tidx is None
                 else minfo.time['unit']['Abbv'][tidx])
        targ_text = (f"{minfo().field['txt']['targ']}"
                     + ("ic Field " if (fidx is not None and fidx < 2)
                        else "Current")
                     + f"({fabbv})")
        setp_label = minfo().field['txt']['setp'][0] + f" ({fabbv})"
        ramp_label = minfo().field['txt']['setp'][1] + f" ({fabbv}/{tabbv})"
        # bound = mag.lims.field[fidx] if (fidx is not None) else 0
        bound = minfo().field['lim'][fidx]
        ui.targetLabel.setText(targ_text)
        ui.targetSpinbox.setRange(-bound, bound)
        ui.setpointsLabel.setText(setp_label)
        ui.ratesLabel.setText(ramp_label)
        # ui.holdLabel.setText(mag.hold_times_label + f'({tabbv})')

    def update_mag_ui(self) -> None:
        # TODO: Test update_mag_ui
        """Update the UI so magnet values correspond to internal vars."""
        for k, v in self.mag_ui_internal.items():
            k(v)

# %% Configuration File Section

    def update_from_config(self, file: Optional[str] = None,
                           instr: Optional[str] = None):
        """Update internal variables of instr based on config file.

        instr can have values 'keith', 'temp', or 'mag'.  An empty value will
        update all internal variables.
        """
        # TODO: Test update_from_config
        self.config.name = None
        dispatch = {'keith': ('Keithley', self.kwind, self.load_keith_config),
                    'temp': ('Temperature', self.twind, self.load_temp_config),
                    'mag': ('Magnet', self.magwind, self.load_mag_config)}
        if instr is not None and instr not in dispatch.keys():
            raise ValueError('update_from_config: instr must be in'
                             f'{dispatch.keys()}.  All params loaded.')
            instr = None
        if file is None:
            filename = QFileDialog.getOpenFileName(
                    None,
                    (f'Load {dispatch[instr][0] if instr is not None else ""} '
                     'Configuration'), '', ('YAML (*.yaml)'))
            file = filename[0]
        if file is not None:
            self.config.load(file)
            window = dispatch[instr][1] if instr is not None else self.plwind
            window.configFile.setText(file)
            if instr is not None:
                params = self.config.params[dispatch[instr][0]]
                dispatch[instr][2](params)
            else:
                kparams = self.config.params['Keithley']
                tparams = self.config.params['Temperature']
                mparams = self.config.params['Magnet']
                self.load_keith_config(kparams)
                self.load_temp_config(tparams)
                self.load_mag_config(mparams)

    def load_keith_config(self, params: dict):
        """Load parameters from the 'Keithley' header of the config file."""
        print('IV config allegedly loaded.\n')
        self.set_keith_address(params['address'])
        self.set_keith_meas_type(params['measType'])
        self.set_keith_unit(params['unit'])
        self.set_keith_source_range_type(params['sourceRangeType'])
        self.set_keith_source_range(params['sourceRange'])
        self.set_keith_compliance(params['complianceVolt'])
        self.set_keith_compliance_abort(params['complianceAbort'])
        self.set_keith_volt_range(params['meterRange'])
        diff = params['diffCon']

        self.keith.set_curr1(diff['startCurrent'], meas_idx=0)
        self.keith.set_curr2(diff['stopCurrent'], meas_idx=0)
        self.keith.set_curr_step(diff['stepCurrent'], meas_idx=0)
        self.keith.set_curr_delta(diff['deltaCurrent'], meas_idx=0)
        self.keith.set_meas_rate(diff['measRate'], meas_idx=0)
        self.keith.set_meas_delay(diff['measDelay'], meas_idx=0)
        self.keith.set_filter(diff['filterOn'], meas_idx=0)
        self.keith.set_filter_window(diff['filterWindow'], meas_idx=0)
        self.keith.set_filter_count(diff['filterCount'], meas_idx=0)

        delta = params['delta']

        self.keith.set_curr1(delta['highCurrent'], meas_idx=1)
        self.keith.set_curr2(delta['lowCurrent'], meas_idx=1)
        self.keith.set_num_points(delta['pulseCount'], meas_idx=1)
        self.keith.set_meas_rate(delta['measRate'], meas_idx=1)
        self.keith.set_meas_delay(delta['measDelay'], meas_idx=1)
        self.keith.set_filter(delta['filterOn'], meas_idx=1)
        self.keith.set_filter_idx(delta['filterType'], meas_idx=1)
        self.keith.set_filter_window(delta['filterWindow'], meas_idx=1)
        self.keith.set_filter_count(delta['filterCount'], meas_idx=1)

        pdelta = params['pulseDelta']

        self.keith.set_curr1(pdelta['highCurrent'], meas_idx=2)
        self.keith.set_curr2(pdelta['lowCurrent'], meas_idx=2)
        self.keith.set_num_points(pdelta['pulseCount'], meas_idx=2)
        self.keith.set_meas_rate(pdelta['cycleInt'], meas_idx=2)
        self.keith.set_meas_delay(pdelta['measDelay'], meas_idx=2)
        self.keith.set_low_meas(pdelta['lowMeas'], meas_idx=2)
        self.keith.set_filter(pdelta['filterOn'], meas_idx=2)
        self.keith.set_filter_idx(pdelta['filterType'], meas_idx=2)
        self.keith.set_filter_window(pdelta['filterWindow'], meas_idx=2)
        self.keith.set_filter_count(pdelta['filterCount'], meas_idx=2)

        pdelt_stair = params['pDeltStair']

        self.keith.set_curr1(pdelt_stair['startCurrent'], meas_idx=3)
        self.keith.set_curr2(pdelt_stair['stopCurrent'], meas_idx=3)
        self.keith.set_curr_step(pdelt_stair['stepCurrent'], meas_idx=3)
        self.keith.set_num_sweeps(pdelt_stair['sweeps'], meas_idx=3)
        self.keith.set_pulse_width(pdelt_stair['pulseWidth'], meas_idx=3)
        self.keith.set_meas_rate(pdelt_stair['cycleTime'], meas_idx=3)
        self.keith.set_meas_delay(pdelt_stair['measDelay'], meas_idx=3)
        self.keith.set_low_meas(pdelt_stair['lowMeas'], meas_idx=3)
        self.keith.set_filter(pdelt_stair['filterOn'], meas_idx=3)
        self.keith.set_filter_window(pdelt_stair['filterWindow'], meas_idx=3)
        self.keith.set_filter_count(pdelt_stair['filterCount'], meas_idx=3)

        pdelt_log = params['pDeltLog']

        self.keith.set_curr1(pdelt_log['startCurrent'], meas_idx=4)
        self.keith.set_curr2(pdelt_log['stopCurrent'], meas_idx=4)
        self.keith.set_num_points(pdelt_log['points'], meas_idx=4)
        self.keith.set_num_sweeps(pdelt_log['sweeps'], meas_idx=4)
        self.keith.set_pulse_width(pdelt_log['pulseWidth'], meas_idx=4)
        self.keith.set_meas_rate(pdelt_log['cycleTime'], meas_idx=4)
        self.keith.set_meas_delay(pdelt_log['measDelay'], meas_idx=4)
        self.keith.set_low_meas(pdelt_log['lowMeas'], meas_idx=4)
        self.keith.set_filter(pdelt_log['filterOn'], meas_idx=4)
        self.keith.set_filter_window(pdelt_log['filterWindow'], meas_idx=4)
        self.keith.set_filter_count(pdelt_log['filterCount'], meas_idx=4)
        self.update_keith_ui(block=True)

    def get_keith_config(self):
        """Convert UI configuration from internal variables to YAML."""
        kconfig = self.config.params['Keithley']
        diffconfig = kconfig['diffcon']
        deltaconfig = kconfig['delta']
        pdconfig = kconfig['pulseDelta']
        stairconfig = kconfig['pDeltStair']
        logconfig = kconfig['pDeltLog']
        diff = self.keith.meas_type(0)
        delta = self.keith.meas_type(1)
        pdelta = self.keith.meas_type(2)
        stair = self.keith.meas_type(3)
        log = self.keith.meas_type(4)

        kconfig['address'] = self.keith.address
        kconfig['measType'] = self.keith.meas_type_txt()
        kconfig['unit'] = self.keith.unit()
        kconfig['sourceRangeType'] = self.keith.source_range_type()
        kconfig['sourceRange'] = self.keith.source_range('float')
        kconfig['complianceVolt'] = self.keith.compl_volt
        kconfig['combplianceAbort'] = self.keith.compl_abort
        kconfig['meterRange'] = self.keith.volt_range('float')

        diffconfig['startCurrent'] = diff.curr1
        diffconfig['stopCurrent'] = diff.curr2
        diffconfig['stepCurrent'] = diff.curr_step
        diffconfig['deltaCurrent'] = diff.curr_delta
        diffconfig['measRate'] = diff.meas_rate
        diffconfig['measDelay'] = diff.meas_delay
        diffconfig['filterOn'] = diff.filter_on
        diffconfig['filterWindow'] = diff.filter_window
        diffconfig['filterCount'] = diff.filter_count

        deltaconfig['highCurrent'] = delta.curr1
        deltaconfig['lowCurrent'] = delta.curr2
        deltaconfig['pulseCount'] = delta.num_points
        deltaconfig['measRate'] = delta.meas_rate
        deltaconfig['measDelay'] = delta.meas_delay
        deltaconfig['filterOn'] = delta.filter_on
        deltaconfig['filterType'] = delta.filter_type
        deltaconfig['filterWindow'] = delta.filter_window
        deltaconfig['filterCount'] = delta.filter_count

        pdconfig['highCurrent'] = pdelta.curr1
        pdconfig['lowCurrent'] = pdelta.curr2
        pdconfig['pulseCount'] = pdelta.num_points
        pdconfig['pulseWidth'] = pdelta.pulse_width
        pdconfig['cycleInt'] = pdelta.cycle_int
        pdconfig['measDelay'] = pdelta.meas_delay
        pdconfig['lowMeas'] = pdelta.low_meas
        pdconfig['filterOn'] = pdelta.filter_on
        pdconfig['filterType'] = pdelta.filter_type
        pdconfig['filterWindow'] = pdelta.filter_window
        pdconfig['filterCount'] = pdelta.filter_count

        stairconfig['startCurrent'] = stair.curr1
        stairconfig['stopCurrent'] = stair.curr2
        stairconfig['stepCurrent'] = stair.curr_step
        stairconfig['points'] = 0
        stairconfig['sweeps'] = stair.num_sweeps
        stairconfig['pulseWidth'] = stair.pulse_width
        stairconfig['cycleTime'] = stair.cycle_time
        stairconfig['measDelay'] = stair.meas_delay
        stairconfig['lowMeas'] = stair.low_meas
        stairconfig['filterOn'] = stair.filter_on
        stairconfig['filterWindow'] = stair.filter_window
        stairconfig['filterCount'] = stair.filter_count

        logconfig['startCurrent'] = log.curr1
        logconfig['stopCurrent'] = log.curr2
        logconfig['points'] = log.num_points
        logconfig['sweeps'] = log.num_sweeps
        logconfig['pulseWidth'] = log.pulse_width
        logconfig['cycleTime'] = log.cycle_time
        logconfig['measDelay'] = log.meas_delay
        logconfig['lowMeas'] = log.low_meas
        logconfig['filterOn'] = log.filter_on
        logconfig['filterWindow'] = log.filter_window
        logconfig['filterCount'] = log.filter_count

        self.config.new['Keithley'] = kconfig

    def load_temp_config(self, params: Dict):
        """Load parameters from the 'Temperature' header of the config file."""
        # TODO: Test load_temp_config
        print('temp config allegedly loaded.\n')
        self.set_temp_address(params['address'])
        self.set_temp_to_measure(params['tempsToMeasure'])
        self.set_temp_rad_control(params['controlRad'])
        self.set_temp_rad_setpoint(params['radSetpoint'])
        self.set_temp_rad_ramp(params['radRamp'])
        self.set_temp_rad_power(params['radPower'])
        self.set_temp_stage_control(params['controlStage'])
        self.set_temp_stage_setpoint(params['stageSetpoint'])
        self.set_temp_stage_ramp(params['stageRamp'])
        self.set_temp_stage_power(params['stagePower'])

        self.update_temp_ui(block=True)

    def get_temp_config(self):
        """Convert UI parameters to YAML."""
        # TODO: Test get_temp_config
        tconfig = self.config.params['Temperature']
        temp = self.temp

        tconfig['address'] = temp.address
        tconfig['tempsToMeasure'] = temp.to_measure_str
        tconfig['controlRad'] = temp.rad_control
        tconfig['radSetpoint'] = temp.rad_setpoint
        tconfig['radRamp'] = temp.rad_ramp
        tconfig['radPower'] = temp.rad_power
        tconfig['controlStage'] = temp.stage_control
        tconfig['stageSetpoint'] = temp.stage_setpoint
        tconfig['stageRamp'] = temp.stage_ramp
        tconfig['stagePower'] = temp.stage_power

    def load_mag_config(self, params: Dict):
        """Load parameters from the 'Magnet' header of the config file."""
        # TODO: Write load_mag_config
        self.set_mag_address(params['address'])
        self.set_mag_target(params['target'])
        self.set_mag_field_unit(params['fieldUnit'])
        self.set_mag_time_unit(params['time_unit'])
        self.set_mag_segments(params['segs'])
        self.set_mag_ramp_setpoints(params['rampSetpoints'])
        self.set_mag_ramp_rates(params['rampRates'])
        self.set_mag_quench_detect(params['quenchDetect'])
        self.set_mag_volt_limit(params['voltLimit'])
        self.set_mag_curr_limit(params['currLimit'])

    def get_mag_config(self):
        """Convert the UI to YAML data so it can be saved to a config file."""
        # TODO: Test get_mag_config
        mconfig = self.config.params['Magnet']
        mag = self.mag

        mconfig['address'] = mag.address
        mconfig['target'] = mag.target
        mconfig['fieldUnit'] = mag.fieldUnit('Full')
        mconfig['timeUnit'] = mag.timeUnit('Full')
        mconfig['segs'] = mag.ramp_segments
        mconfig['rampSetpoints'] = mag.setpoints_list
        mconfig['rampRates'] = mag.ramps_list
        mconfig['quenchDetect'] = mag.quench_detect
        mconfig['voltLimit'] = mag.volt_limit
        mconfig['currLimit'] = mag.curr_limit

# %% Save Data Section

    def save_data_as(self):
        """Open dialog box to set/create text file in which to save data."""
        name = QFileDialog.getSaveFileName(None, 'Title', '', 'TXT (*.txt)')
        self.save.new(name)
        if name[0]:
            # TODO: Implement UI update.
            pass

    def exit(self):
        """Stop all measurement safely and then close the program."""
        # TODO: Stop other running scripts?
        if self.krunning:
            self.stop_keith()
        sys.exit()

# %% Main


def main():
    """Execute the UI loop."""
    app = QtWidgets.QApplication(sys.argv)
    form = ProbeGui()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
