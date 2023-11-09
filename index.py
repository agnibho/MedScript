# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableView, QAbstractItemView
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from glob import glob
from zipfile import ZipFile
from config import config
from renderbox import UnrenderBox
import logging, os, json

class Index(QMainWindow):

    signal_open=pyqtSignal(str)
    signal_copy=pyqtSignal(dict)
    index=[]
    proxymodel=QSortFilterProxyModel()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript")
        self.setGeometry(200, 200, 600, 400)

        widget=QWidget(self)
        layout=QVBoxLayout(widget)
        self.table=QTableView()
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.cmd_view)
        layout2=QFormLayout()
        self.input_pid=QLineEdit()
        self.input_pid.returnPressed.connect(self.cmd_filter_pid)
        self.input_id=QLineEdit()
        self.input_id.returnPressed.connect(self.cmd_filter_id)
        self.input_name=QLineEdit()
        self.input_name.returnPressed.connect(self.cmd_filter_name)
        layout2.addRow("Filter by PID:", self.input_pid)
        layout2.addRow("Filter by ID:", self.input_id)
        layout2.addRow("Filter by Name:", self.input_name)
        layout3=QHBoxLayout()
        button_view=QPushButton("View Prescription")
        button_view.clicked.connect(self.cmd_view)
        button_open=QPushButton("Open Original")
        button_open.clicked.connect(self.cmd_open)
        button_copy=QPushButton("Create Copy")
        button_copy.clicked.connect(self.cmd_copy)
        layout3.addWidget(button_view)
        layout3.addWidget(button_open)
        layout3.addWidget(button_copy)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addWidget(self.table)

        self.unrenderbox=UnrenderBox()

        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))

        self.refresh()

    def refresh(self):
        self.build()
        self.load()

    def cmd_filter_pid(self):
        self.input_id.setText("")
        self.input_name.setText("")
        self.proxymodel.setFilterKeyColumn(0)
        self.proxymodel.setFilterFixedString(self.input_pid.text())

    def cmd_filter_id(self):
        self.input_pid.setText("")
        self.input_name.setText("")
        self.proxymodel.setFilterKeyColumn(1)
        self.proxymodel.setFilterFixedString(self.input_id.text())

    def cmd_filter_name(self):
        self.input_pid.setText("")
        self.input_id.setText("")
        self.proxymodel.setFilterKeyColumn(2)
        self.proxymodel.setFilterFixedString(self.input_name.text())

    def cmd_view(self):
        try:
            file=self.getSelectedFile()
            if(file):
                with ZipFile(file) as zf:
                    with zf.open("prescription.json") as pf:
                        prescription=json.loads(pf.read())
                self.unrenderbox.show(prescription).exec()
        except Exception as e:
            logging.exception(e)

    def cmd_open(self):
        try:
            file=self.getSelectedFile()
            if(file):
                self.signal_open.emit()
                self.hide()
        except Exception as e:
            logging.exception(e)

    def cmd_copy(self):
        try:
            file=self.getSelectedFile()
            if(file):
                with ZipFile(file) as zf:
                    with zf.open("prescription.json") as pf:
                        pres=json.loads(pf.read())
                self.signal_copy.emit(pres)
                self.hide()
        except Exception as e:
            logging.exception(e)


    def getSelectedFile(self):
        try:
            selection=self.table.selectedIndexes()
            file=selection[-1].data()
            return file
        except IndexError as e:
            logging.warning(e)
        except Exception as e:
            logging.exception(e)

    def build(self):
        files=glob(os.path.join(config["document_directory"], "**", "*.mpaz"), recursive=True)
        self.index=[]
        for file in files:
            try:
                with ZipFile(file) as zf:
                    try:
                        with zf.open("prescription.json") as pf:
                            pres=json.loads(pf.read())
                            self.index.append([pres["pid"], pres["id"], pres["name"], pres["dob"], pres["age"], pres["sex"], pres["date"], pres["diagnosis"], file])
                    except KeyError as e:
                        logging.warning(e)
                    except Exception as e:
                        logging.exception(e)
            except Exception as e:
                logging.exception(e)

    def load(self):
        model=QStandardItemModel()
        model.setHorizontalHeaderLabels(["Patient ID", "Prescription ID", "Name", "Date of Birth", "Age", "Sex", "Date", "Diagnosis", "File"])
        for item in self.index:
            row=[]
            for i in item:
                row.append(QStandardItem(i))
            model.appendRow(row)
        self.proxymodel.setSourceModel(model)
        self.proxymodel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.table.setModel(self.proxymodel)
        self.table.resizeColumnsToContents()
