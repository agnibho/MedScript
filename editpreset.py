# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit, QTableView, QMessageBox
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSignal
from config import config
import logging, os, csv

class EditPreset(QMainWindow):

    presetEdited=pyqtSignal()
    editors=[]
    model=QStandardItemModel()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript Preset Editor")
        self.setGeometry(200, 200, 600, 400)

        widget=QWidget(self)
        layout=QVBoxLayout(widget)
        self.table=QTableView()
        layout2=QHBoxLayout()
        self.input_file=QComboBox()
        self.input_file.addItems(["note", "report", "advice", "investigation", "medication", "additional", "certificate"])
        self.input_file.currentIndexChanged.connect(self.cmd_load)
        button_save=QPushButton("Save")
        button_save.clicked.connect(self.cmd_save)
        button_row=QPushButton("Add Row")
        button_row.clicked.connect(self.cmd_row)
        layout2.addWidget(self.input_file)
        layout2.addWidget(button_save)
        layout.addLayout(layout2)
        layout.addWidget(self.table)
        layout.addWidget(button_row)

        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))

        self.load()

    def cmd_load(self):
        if self.confirm():
            self.load()

    def cmd_save(self):
        try:
            item=self.input_file.currentText()
            file=os.path.join(config["preset_directory"], item+".csv")
            with open(file, "w", newline="") as f:
                writer=csv.writer(f, delimiter=config["preset_delimiter"])
                writer.writerow(["KEY", "VALUE"])
                for i in self.editors:
                    row=[i[0].toPlainText(), i[1].toPlainText()]
                    if row[0].strip()!="" or row[1].strip()!="":
                        writer.writerow(row)
            self.load(file)
            self.presetEdited.emit()
            self.hide()
        except Exception as e:
            logging.exception(e)

    def cmd_row(self):
        tablerow=[]
        tablerow.append(QStandardItem(""))
        tablerow.append(QStandardItem(""))
        self.model.appendRow(tablerow)
        self.editors.append([QTextEdit(), QTextEdit()])
        self.table.setIndexWidget(self.model.index(self.model.rowCount()-1,0), self.editors[-1][0])
        self.table.setIndexWidget(self.model.index(self.model.rowCount()-1,1), self.editors[-1][1])
        self.table.resizeRowsToContents()

    def load(self, file=None):
        try:
            if file is None:
                item=self.input_file.currentText()
                file=os.path.join(config["preset_directory"], item+".csv")
            self.editors=[]
            self.model=QStandardItemModel()
            self.model.setHorizontalHeaderLabels(["KEY", "VALUE"])
            self.table.setModel(self.model)
            with open(file) as f:
                reader=csv.reader(f, delimiter=config["preset_delimiter"])
                next(reader)
                for idx,row in enumerate(reader):
                    tablerow=[]
                    try:
                        row[0]
                    except IndexError:
                        row.append("")
                    try:
                        row[1]
                    except IndexError:
                        row.append("")
                    tablerow.append(QStandardItem(row[0]))
                    tablerow.append(QStandardItem(row[1]))
                    self.model.appendRow(tablerow)
                    self.editors.append([QTextEdit(), QTextEdit()])
                    self.editors[idx][0].setPlainText(row[0])
                    self.editors[idx][1].setPlainText(row[1])
                    self.table.setIndexWidget(self.model.index(idx,0), self.editors[idx][0])
                    self.table.setIndexWidget(self.model.index(idx,1), self.editors[idx][1])
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.resizeRowsToContents()
            textedit=QTextEdit()
        except Exception as e:
            logging.exception(e)

    def confirm(self):
        return QMessageBox.StandardButton.Yes==QMessageBox.question(self,"Confirm action", "Unsaved changes may be lost. Continue?")

    def closeEvent(self, event):
        if self.confirm():
            event.accept()
        else:
            event.ignore()
