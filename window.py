# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import os, sys, datetime, dateutil.parser, webbrowser
from PyQt6.QtCore import QDateTime, QSize, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMainWindow, QMessageBox, QLabel, QPushButton, QLineEdit, QTextEdit, QDateTimeEdit, QListWidget, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout, QFormLayout, QToolBar, QTabWidget, QStatusBar, QFileDialog
from PyQt6.QtGui import QAction, QIcon
from pathlib import Path
from hashlib import md5
from prescription import Prescription
from renderer import Renderer
from filehandler import FileHandler
from renderbox import RenderBox
from setting import EditPrescriber
from viewbox import ViewBox

class MainWindow(QMainWindow):

    signal_view=pyqtSignal(str)

    current_file=FileHandler()
    prescription=Prescription()
    renderer=Renderer()
    save_state=md5("".encode()).hexdigest()

    def cmd_new(self):
        self.prescription.set_data()
        self.input_attachment.clear()
        self.load_interface()
        self.save_state=md5("".encode()).hexdigest()

    def cmd_open(self):
        try:
            self.current_file.set_file(QFileDialog.getOpenFileName()[0])
            self.current_file.open()
            self.prescription.read_from(os.path.join(self.current_file.directory.name,"prescription.json"))
            self.load_interface_from_instance()
            self.save_state=md5(self.prescription.get_json().encode()).hexdigest()
            self.load_attachment(self.current_file.list())
        except Exception as e:
            QMessageBox.warning(self,"Open failed", "Failed to open file.")
            print(e)

    def cmd_save(self):
        try:
            if not os.path.exists(self.current_file.file):
                self.current_file.set_file(QFileDialog.getSaveFileName()[0])
            for i in range(self.input_attachment.count()):
                self.current_file.copy(self.input_attachment.item(i).text())
            self.update_instance()
            self.prescription.write_to(os.path.join(self.current_file.directory.name, "prescription.json"))
            self.current_file.save()
            self.load_interface_from_instance()
            self.save_state=md5(self.prescription.get_json().encode()).hexdigest()
        except Exception as e:
            QMessageBox.warning(self,"Save failed", "Failed to save file.")
            print(e)

    def cmd_save_as(self):
        self.current_file.set_file(QFileDialog.getSaveFileName()[0])
        Path(self.current_file.file).touch()
        self.cmd_save()

    def cmd_refresh(self):
        self.update_instance()
        self.load_interface_from_instance()

    def cmd_quit(self):
        sys.exit()

    def cmd_render(self):
        self.update_instance()
        if(self.save_state==md5(self.prescription.get_json().encode()).hexdigest()):
            target=self.renderer.render(self.current_file.directory.name)
            self.signal_view.emit(target)
            self.renderbox.show()
        else:
           QMessageBox.information(self,"Save first", "Please save the file before rendering.")

    def cmd_prescriber(self):
        self.edit_prescriber.show()

    def cmd_about(self):
        self.viewbox.open(os.path.join("resource", "about.html"))
        self.viewbox.show()

    def cmd_help(self):
        self.viewbox.open(os.path.join("resource", "help.html"))
        self.viewbox.show()

    def load_interface(self, file="", date=None, id="", name="", age="", sex="", address="", contact="", extra="", mode="", daw="", note="", report="", investigation="", medication="", advice=""):
        try:
            self.statusbar.showMessage(self.current_file.file)
            if date is None:
                d=QDateTime.currentDateTime()
            else:
                try:
                    pdate=dateutil.parser.parse(date)
                    d=QDateTime.fromString(pdate.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
                except Exception as e:
                    QMessageBox.warning(self,"Failed to load", str(e))
                    raise(e)
            self.input_date.setDateTime(d)
            self.input_id.setText(id)
            self.input_name.setText(name)
            self.input_age.setText(age)
            self.input_sex.setCurrentText(sex)
            self.input_address.setText(address)
            self.input_contact.setText(contact)
            self.input_extra.setText(extra)
            self.input_mode.setCurrentText(mode)
            self.input_daw.setChecked(bool(daw))
            self.input_note.setText(note)
            self.input_report.setText(report)
            self.input_investigation.setText(investigation)
            self.input_medication.setText(medication)
            self.input_advice.setText(advice)
        except Exception as e:
            QMessageBox.warning(self,"Failed to load", "Failed to load the data into the application.")
            print(e)

    def load_interface_from_instance(self):
        self.load_interface(
                file=self.prescription.file,
                date=self.prescription.date,
                id=self.prescription.id,
                name=self.prescription.name,
                age=self.prescription.age,
                sex=self.prescription.sex,
                address=self.prescription.address,
                contact=self.prescription.contact,
                extra=self.prescription.extra,
                mode=self.prescription.mode,
                daw=self.prescription.daw,
                note=self.prescription.note,
                report=self.prescription.report,
                investigation=self.prescription.investigation,
                medication=self.prescription.medication,
                advice=self.prescription.advice
                )

    def update_instance(self):
        try:
            self.prescription.set_data(
                    date=self.input_date.dateTime().toString("yyyy-MM-dd hh:mm:ss"),
                    id=self.input_id.text(),
                    name=self.input_name.text(),
                    age=self.input_age.text(),
                    sex=self.input_sex.currentText(),
                    address=self.input_address.text(),
                    contact=self.input_contact.text(),
                    extra=self.input_extra.toPlainText(),
                    mode=self.input_mode.currentText(),
                    daw=self.input_daw.isChecked(),
                    note=self.input_note.toPlainText(),
                    report=self.input_report.toPlainText(),
                    investigation=self.input_investigation.toPlainText(),
                    medication=self.input_medication.toPlainText(),
                    advice=self.input_advice.toPlainText()
                    )
        except Exception as e:
            QMessageBox.critical(self,"Failed", "Critical failure happned. Please check console for more info.")
            print(e)

    def add_attachment(self):
        try:
            new=QFileDialog.getOpenFileName()[0]
            if new:
                self.input_attachment.addItem(new)
        except Exception as e:
            QMessageBox.warning(self,"Attach failed", "Failed to attach file.")
            print(e)

    def remove_attachment(self):
        self.input_attachment.takeItem(self.input_attachment.currentRow())

    def open_attachment(self):
        webbrowser.open(self.input_attachment.currentItem().text())

    def load_attachment(self, attachments):
        for attach in attachments:
            self.input_attachment.addItem(attach)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript")
        self.setGeometry(100, 100, 600, 400)

        icon_open=QIcon("resource/icon_open.svg")
        icon_save=QIcon("resource/icon_save.svg")
        icon_render=QIcon("resource/icon_render.svg")
        icon_refresh=QIcon("resource/icon_refresh.svg")

        action_new=QAction("New", self)
        action_new.triggered.connect(self.cmd_new)
        action_open=QAction("Open", self)
        action_open2=QAction(icon_open, "Open", self)
        action_open.triggered.connect(self.cmd_open)
        action_open2.triggered.connect(self.cmd_open)
        action_save=QAction("Save", self)
        action_save2=QAction(icon_save, "Save", self)
        action_save.triggered.connect(self.cmd_save)
        action_save2.triggered.connect(self.cmd_save)
        action_save_as=QAction("Save As", self)
        action_save_as.triggered.connect(self.cmd_save_as)
        action_refresh=QAction("Refresh", self)
        action_refresh2=QAction(icon_refresh, "Refresh", self)
        action_refresh.triggered.connect(self.cmd_refresh)
        action_refresh2.triggered.connect(self.cmd_refresh)
        action_quit=QAction("Quit", self)
        action_quit.triggered.connect(self.cmd_quit)
        action_render=QAction("Render", self)
        action_render2=QAction(icon_render, "Render", self)
        action_render.triggered.connect(self.cmd_render)
        action_render2.triggered.connect(self.cmd_render)
        action_prescriber=QAction("Prescriber", self)
        action_prescriber.triggered.connect(self.cmd_prescriber)
        action_about=QAction("About", self)
        action_about.triggered.connect(self.cmd_about)
        action_help=QAction("Help", self)
        action_help.triggered.connect(self.cmd_help)

        menubar=self.menuBar()
        menu_file=menubar.addMenu("File")
        menu_file.addAction(action_new)
        menu_file.addAction(action_open)
        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addAction(action_quit)
        menu_prepare=menubar.addMenu("Prepare")
        menu_prepare.addAction(action_render)
        menu_prepare.addAction(action_refresh)
        menu_prepare.addAction(action_prescriber)
        menu_help=menubar.addMenu("Help")
        menu_help.addAction(action_about)
        menu_help.addAction(action_help)

        toolbar=QToolBar("Main Toolbar", floatable=False, movable=False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.addAction(action_open2)
        toolbar.addAction(action_save2)
        toolbar.addAction(action_refresh2)
        toolbar.addAction(action_render2)
        self.addToolBar(toolbar)

        tab_info=QWidget(self)
        layout_info=QFormLayout(tab_info)
        self.input_date=QDateTimeEdit(self)
        self.input_date.setDisplayFormat("MMMM dd, yyyy hh:mm a")
        layout_info.addRow("Date", self.input_date)
        self.input_id=QLineEdit(self)
        layout_info.addRow("ID", self.input_id)
        self.input_name=QLineEdit(self)
        layout_info.addRow("Name", self.input_name)
        self.input_age=QLineEdit(self)
        layout_info.addRow("Age", self.input_age)
        self.input_sex=QComboBox(self)
        self.input_sex.addItems(["Male", "Female", "Other"])
        self.input_sex.setEditable(True)
        layout_info.addRow("Sex", self.input_sex)
        self.input_address=QLineEdit(self)
        layout_info.addRow("Address", self.input_address)
        self.input_contact=QLineEdit(self)
        layout_info.addRow("Contact", self.input_contact)
        self.input_extra=QTextEdit(self)
        layout_info.addRow("Extra", self.input_extra)
        self.input_mode=QComboBox(self)
        self.input_mode.addItems(["In-Person", "Tele-Consultation", "Other"])
        self.input_mode.setEditable(True)
        layout_info.addRow("Mode", self.input_mode)
        self.input_daw=QCheckBox("Dispense as written", self)
        layout_info.addRow("DAW", self.input_daw)

        tab_note=QWidget(self)
        layout_note=QVBoxLayout(tab_note)
        label_note=QLabel("Clinical Notes")
        self.input_note=QTextEdit(self)
        layout_note.addWidget(label_note)
        layout_note.addWidget(self.input_note)

        tab_report=QWidget(self)
        layout_report=QVBoxLayout(tab_report)
        label_report=QLabel("Available Reports")
        self.input_report=QTextEdit(self)
        layout_report.addWidget(label_report)
        layout_report.addWidget(self.input_report)

        tab_investigation=QWidget(self)
        layout_investigation=QVBoxLayout(tab_investigation)
        label_investigation=QLabel("Recommended Investigations")
        self.input_investigation=QTextEdit(self)
        layout_investigation.addWidget(label_investigation)
        layout_investigation.addWidget(self.input_investigation)

        tab_medication=QWidget(self)
        layout_medication=QVBoxLayout(tab_medication)
        label_medication=QLabel("Medication Advice")
        self.input_medication=QTextEdit(self)
        layout_medication.addWidget(label_medication)
        layout_medication.addWidget(self.input_medication)

        tab_advice=QWidget(self)
        layout_advice=QVBoxLayout(tab_advice)
        label_advice=QLabel("Additional Advice")
        self.input_advice=QTextEdit(self)
        layout_advice.addWidget(label_advice)
        layout_advice.addWidget(self.input_advice)

        tab_attachment=QWidget(self)
        layout_attachment=QVBoxLayout(tab_attachment)
        layout_attachment2=QHBoxLayout()
        label_attachment=QLabel("Attached files")
        self.input_attachment=QListWidget(self)
        button_add=QPushButton("Add")
        button_add.clicked.connect(self.add_attachment)
        button_remove=QPushButton("Remove")
        button_remove.clicked.connect(self.remove_attachment)
        button_open=QPushButton("Open")
        button_open.clicked.connect(self.open_attachment)
        layout_attachment.addWidget(label_attachment)
        layout_attachment.addLayout(layout_attachment2)
        layout_attachment.addWidget(self.input_attachment)
        layout_attachment2.addWidget(button_add)
        layout_attachment2.addWidget(button_remove)
        layout_attachment2.addWidget(button_open)


        tab=QTabWidget(self)
        tab.addTab(tab_info, "Patient")
        tab.addTab(tab_note, "Clinical")
        tab.addTab(tab_report, "Report")
        tab.addTab(tab_investigation, "Investigation")
        tab.addTab(tab_medication, "Medication")
        tab.addTab(tab_advice, "Advice")
        tab.addTab(tab_attachment, "Attachment")

        self.setCentralWidget(tab)

        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)

        self.renderbox=RenderBox()
        self.signal_view.connect(self.renderbox.update)
        self.edit_prescriber=EditPrescriber()
        self.viewbox=ViewBox()

        self.cmd_new()
        self.show()
