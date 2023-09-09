# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QToolBar, QFileDialog, QComboBox, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction, QIcon, QPageLayout, QPageSize
from PyQt6.QtCore import QUrl, QMarginsF
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import os
from config import config

class RenderBox(QMainWindow):

    file=""

    def cmd_pdf(self):
        file=QFileDialog.getSaveFileName(self, "Save PDF", os.path.abspath(os.path.join(config["document_directory"], ".pdf")), "PDF (*.pdf);; All Files (*)")
        page=QPageSize(QPageSize.PageSizeId[self.input_size.currentText()])
        self.webview.printToPdf(file[0], QPageLayout(page, QPageLayout.Orientation.Portrait, QMarginsF()))

    def cmd_print(self):
        dialog=QPrintDialog(self.printer)
        if(dialog.exec()):
            self.webview.print(self.printer)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript")
        self.setGeometry(100, 100, 600, 400)

        self.printer=QPrinter(QPrinter.PrinterMode.HighResolution)

        action_pdf=QAction("Create PDF", self)
        action_pdf.triggered.connect(self.cmd_pdf)
        action_print=QAction("Print Document", self)
        action_print.triggered.connect(self.cmd_print)

        page_size=[]
        for size in QPageSize.PageSizeId:
            page_size.append(size.name)
        self.input_size=QComboBox(self)
        self.input_size.addItems(page_size)

        toolbar=QToolBar("View Toolbar", floatable=False, movable=False)
        toolbar.addWidget(self.input_size)
        toolbar.addAction(action_pdf)
        spacer=QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        toolbar.addAction(action_print)
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
            print(e)
