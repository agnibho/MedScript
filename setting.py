# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QFormLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QStatusBar, QMessageBox
import json
from config import config

class EditPrescriber(QMainWindow):

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

    def save(self):
        try:
            self.prescriber["name"]=self.input_name.text()
            self.prescriber["qualification"]=self.input_qualification.text()
            self.prescriber["registration"]=self.input_registration.text()
            self.prescriber["address"]=self.input_address.toPlainText()
            self.prescriber["contact"]=self.input_contact.text()
            self.prescriber["extra"]=self.input_extra.toPlainText()
            with open(self.file, "w") as f:
                f.write(json.dumps(self.prescriber, indent=4))
            QMessageBox.information(self,"Saved", "Information saved.")
            self.hide()
        except Exception as e:
            QMessageBox.critical(self,"Failed to save", "Failed to save the data to the file.")
            raise(e)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("EditBox")
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
        button=QPushButton("Save")
        button.clicked.connect(self.save)
        layout.addWidget(button)

        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)

        self.setCentralWidget(widget)

        self.load()
