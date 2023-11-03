# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QFormLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox, QStatusBar, QMessageBox, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import os, json
from config import config, config_file

class EditConfiguration(QMainWindow):

    def select_directory(self):
        d=QFileDialog.getExistingDirectory(self, "Select Directory", config["data_directory"])
        if(d):
            self.input_directory.setText(d)
    def select_prescriber(self):
        f=QFileDialog.getOpenFileName(self, "Select Prescriber", config["prescriber_directory"], "JSON (*.json);; All Files (*)")[0]
        if(f):
            self.input_prescriber.setText(f)
    def select_key(self):
        f=QFileDialog.getOpenFileName(self, "Select Private Key", os.path.expanduser("~"), "PEM (*.pem);; All Files (*)")[0]
        if(f):
            self.input_key.setText(f)
    def select_certificate(self):
        f=QFileDialog.getOpenFileName(self, "Select Certificate", os.path.expanduser("~"), "PEM (*.pem);; All Files (*)")[0]
        if(f):
            self.input_certificate.setText(f)
    def select_root(self):
        f=QFileDialog.getOpenFileName(self, "Select Root Bundle", os.path.expanduser("~"), "PEM (*.pem);; All Files (*)")[0]
        if(f):
            self.input_root.setText(f)

    def load(self):
        try:
            self.statusbar.showMessage(config_file)
            self.input_directory.setText(self.config["data_directory"])
            self.input_prescriber.setText(self.config["prescriber"])
            self.input_newline.setChecked(bool(self.config["preset_newline"]))
            self.input_delimiter.setCurrentText(self.config["preset_delimiter"])
            self.input_markdown.setChecked(bool(self.config["markdown"]))
            self.input_update.setChecked(bool(self.config["check_update"]))
            self.input_plugin.setChecked(bool(self.config["enable_plugin"]))
            self.input_smime.setChecked(bool(self.config["smime"]))
            self.input_key.setText(self.config["private_key"])
            self.input_certificate.setText(self.config["certificate"])
            self.input_root.setText(self.config["root_bundle"])
        except Exception as e:
            QMessageBox.critical(self,"Failed to load", "Failed to load the data into the application.")
            raise(e)

    def save(self):
        if(QMessageBox.StandardButton.Yes==QMessageBox.question(self,"Confirm Save", "This action will overwrite the previous configuration. Continue?")):
            try:
                self.config["data_directory"]=self.input_directory.text()
                self.config["prescriber"]=self.input_prescriber.text()
                self.config["preset_newline"]=self.input_newline.isChecked()
                self.config["preset_delimiter"]=self.input_delimiter.currentText()
                self.config["markdown"]=self.input_markdown.isChecked()
                self.config["check_update"]=self.input_update.isChecked()
                self.config["enable_plugin"]=self.input_plugin.isChecked()
                self.config["smime"]=self.input_smime.isChecked()
                self.config["private_key"]=self.input_key.text()
                self.config["certificate"]=self.input_certificate.text()
                self.config["root_bundle"]=self.input_root.text()
                with open(config_file, "w") as f:
                    f.write(json.dumps(self.config, indent=4))
                QMessageBox.information(self,"Saved", "Configuration saved. Please restart MedScript.")
                self.hide()
            except Exception as e:
                QMessageBox.critical(self,"Failed to save", "Failed to save the data to the file.")
                print(e)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            with open(config_file) as f:
                self.config=json.loads(f.read()) | config
        except Exception as e:
            print(e)
            self.config=config

        self.setWindowTitle("MedScript")
        self.setGeometry(200, 200, 300, 200)

        widget=QWidget(self)
        layout=QFormLayout(widget)
        self.input_directory=QLineEdit(self)
        btn_directory=QPushButton("Select Directory", self)
        btn_directory.clicked.connect(self.select_directory)
        layout_directory=QHBoxLayout()
        layout_directory.addWidget(self.input_directory)
        layout_directory.addWidget(btn_directory)
        layout.addRow("Data Directory", layout_directory)
        self.input_prescriber=QLineEdit(self)
        btn_prescriber=QPushButton("Select File", self)
        btn_prescriber.clicked.connect(self.select_prescriber)
        layout_prescriber=QHBoxLayout()
        layout_prescriber.addWidget(self.input_prescriber)
        layout_prescriber.addWidget(btn_prescriber)
        layout.addRow("Prescriber", layout_prescriber)
        self.input_newline=QCheckBox("Add newline after preset", self)
        layout.addRow("Preset Newline", self.input_newline)
        self.input_delimiter=QComboBox(self)
        self.input_delimiter.addItems([",", ";"])
        layout.addRow("Preset Delimiter", self.input_delimiter)
        self.input_markdown=QCheckBox("Enable markdown formatting", self)
        layout.addRow("Markdown", self.input_markdown)
        self.input_update=QCheckBox("Check update on startup", self)
        layout.addRow("Check Update", self.input_update)
        self.input_plugin=QCheckBox("Enable plugin", self)
        layout.addRow("Plugin", self.input_plugin)
        self.input_smime=QCheckBox("Enable digital signature (experimental)", self)
        layout.addRow("S/MIME", self.input_smime)
        self.input_key=QLineEdit(self)
        btn_key=QPushButton("Select File", self)
        btn_key.clicked.connect(self.select_key)
        layout_key=QHBoxLayout()
        layout_key.addWidget(self.input_key)
        layout_key.addWidget(btn_key)
        layout.addRow("Private Key", layout_key)
        self.input_certificate=QLineEdit(self)
        btn_certificate=QPushButton("Select File", self)
        btn_certificate.clicked.connect(self.select_certificate)
        layout_certificate=QHBoxLayout()
        layout_certificate.addWidget(self.input_certificate)
        layout_certificate.addWidget(btn_certificate)
        layout.addRow("X509 Certificate", layout_certificate)
        self.input_root=QLineEdit(self)
        btn_root=QPushButton("Select File", self)
        btn_root.clicked.connect(self.select_root)
        layout_root=QHBoxLayout()
        layout_root.addWidget(self.input_root)
        layout_root.addWidget(btn_root)
        layout.addRow("Root Bundle", layout_root)
        button_save=QPushButton("Save")
        button_save.clicked.connect(self.save)
        button_reset=QPushButton("Reset")
        button_reset.clicked.connect(self.load)
        layout_btn=QHBoxLayout()
        layout_btn.addWidget(button_save)
        layout_btn.addWidget(button_reset)
        layout.addRow("", layout_btn)

        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)

        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.load()

class EditPrescriber(QMainWindow):

    signal_save=pyqtSignal(str)

    file=""
    prescriber=""

    def load(self):
        try:
            self.file=config["prescriber"]
            self.statusbar.showMessage(self.file)
            with open(self.file) as data:
                self.prescriber=json.loads(data.read())
            self.input_name.setText(self.prescriber["name"])
            self.input_qualification.setText(self.prescriber["qualification"])
            self.input_registration.setText(self.prescriber["registration"])
            self.input_address.setText(self.prescriber["address"])
            self.input_contact.setText(self.prescriber["contact"])
            self.input_extra.setText(self.prescriber["extra"])
        except Exception as e:
            QMessageBox.critical(self,"Failed to load", "Failed to load the data into the application.")
            raise(e)

    def save(self, file=False):
        if(file is not False or QMessageBox.StandardButton.Yes==QMessageBox.question(self,"Confirm Save", "This action will overwrite the previous information. Continue?")):
            if file is False:
                file=self.file
            try:
                self.prescriber["name"]=self.input_name.text()
                self.prescriber["qualification"]=self.input_qualification.text()
                self.prescriber["registration"]=self.input_registration.text()
                self.prescriber["address"]=self.input_address.toPlainText()
                self.prescriber["contact"]=self.input_contact.text()
                self.prescriber["extra"]=self.input_extra.toPlainText()
                with open(file, "w") as f:
                    f.write(json.dumps(self.prescriber, indent=4))
                QMessageBox.information(self,"Saved", "Information saved.")
                self.signal_save.emit(self.file)
                self.hide()
            except Exception as e:
                QMessageBox.critical(self,"Failed to save", "Failed to save the data to the file.")
                print(e)

    def save_as(self):
        try:
            self.save(QFileDialog.getSaveFileName(self, "Save prescriber", config["prescriber_directory"], "JSON (*.json);; All Files (*)")[0])
        except Exception as e:
            print(e)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript")
        self.setGeometry(200, 200, 300, 200)

        widget=QWidget(self)
        layout=QFormLayout(widget)
        self.input_name=QLineEdit(self)
        layout.addRow("Name", self.input_name)
        self.input_qualification=QLineEdit(self)
        layout.addRow("Qualification", self.input_qualification)
        self.input_registration=QLineEdit(self)
        layout.addRow("Registration", self.input_registration)
        self.input_address=QTextEdit(self)
        layout.addRow("Adress", self.input_address)
        self.input_contact=QLineEdit(self)
        layout.addRow("Contact", self.input_contact)
        self.input_extra=QTextEdit(self)
        layout.addRow("Extra", self.input_extra)
        button_save=QPushButton("Save")
        button_save.clicked.connect(self.save)
        button_save_as=QPushButton("Save As")
        button_save_as.clicked.connect(self.save_as)
        button_reset=QPushButton("Reset")
        button_reset.clicked.connect(self.load)
        layout_btn=QHBoxLayout()
        layout_btn.addWidget(button_save)
        layout_btn.addWidget(button_save_as)
        layout_btn.addWidget(button_reset)
        layout.addRow("", layout_btn)

        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)

        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.load()
