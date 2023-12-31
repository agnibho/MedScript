# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QDialog, QToolBar, QFileDialog, QComboBox, QPushButton, QLabel, QVBoxLayout, QTextBrowser, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QPageLayout, QPageSize
from PyQt6.QtCore import QUrl, QMarginsF
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import logging, os, copy
from config import config

class RenderBox(QMainWindow):

    file=""

    def cmd_pdf(self):
        try:
            file=QFileDialog.getSaveFileName(self, "Save PDF", os.path.abspath(os.path.join(config["document_directory"], ".pdf")), "PDF (*.pdf);; All Files (*)")
            page=QPageSize(QPageSize.PageSizeId[self.input_size.currentText()])
            self.webview.printToPdf(file[0], QPageLayout(page, QPageLayout.Orientation.Portrait, QMarginsF()))
        except Exception as e:
            logging.exception(e)

    def cmd_print(self):
        try:
            dialog=QPrintDialog(self.printer)
            if(dialog.exec()):
                self.webview.print(self.printer)
        except Exception as e:
            logging.exception(e)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript Prescription")
        self.setGeometry(100, 100, 600, 400)

        self.printer=QPrinter(QPrinter.PrinterMode.HighResolution)

        button_pdf=QPushButton("Save PDF", self)
        button_pdf.setShortcut("Ctrl+S")
        button_pdf.clicked.connect(self.cmd_pdf)
        button_print=QPushButton("Print Document", self)
        button_print.setShortcut("Ctrl+P")
        button_print.clicked.connect(self.cmd_print)
        button_close=QPushButton("Close Window", self)
        button_close.setShortcut("Ctrl+Q")
        button_close.clicked.connect(self.hide)

        page_size=[]
        for size in QPageSize.PageSizeId:
            page_size.append(size.name)
        self.input_size=QComboBox(self)
        self.input_size.addItems(page_size)

        toolbar=QToolBar("View Toolbar", floatable=False, movable=False)
        toolbar.addWidget(self.input_size)
        toolbar.addWidget(button_pdf)
        spacer=QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        toolbar.addWidget(button_print)
        toolbar.addWidget(button_close)
        self.addToolBar(toolbar)

        self.webview=QWebEngineView()

        self.setCentralWidget(self.webview)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))

    def update(self, file):
        try:
            self.file=file
            self.webview.load(QUrl("file:///"+self.file.replace(os.sep, "/")))
        except Exception as e:
            QMessageBox.warning(self,"Display failed", "Failed to display file.")
            self.hide()
            logging.exception(e)


class UnrenderBox(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript Viewer")
        self.setMinimumSize(600, 400)
        self.setSizeGripEnabled(True)

        layout=QVBoxLayout(self)
        heading=QLabel("<strong>Prescription</strong>")
        self.display=QTextBrowser()
        layout.addWidget(heading)
        layout.addWidget(self.display)

        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))

    def show(self, prescription):
        if(type(prescription) is not dict):
            try:
                data=copy.deepcopy(prescription).__dict__
                if(type(data["prescriber"]) is not dict):
                   data["prescriber"]=data["prescriber"].__dict__
            except Exception as e:
                logging.critical(e)
        else:
            data=copy.deepcopy(prescription)
        self.load(data)
        return(self)

    def load(self, prescription):
        text=""
        for attr, value in prescription["prescriber"].items():
            if(attr not in ["properties"] and len(value)>0):
                text=text+"<strong>"+value.upper()+"</strong><br>"
        text=text.replace("\n", "<br>")+"<hr>"
        for attr, value in prescription.items():
            if(attr not in ["prescriber", "custom", "properties", "file"] and len(str(value))>0 and (attr not in ["daw"] or value)):
                text=text+"<strong>"+attr.upper()+"</strong><br>"
                text=text+str(value).strip()
                text=text.replace("\n", "<br>")+"<br>"
        self.display.setText(text)
