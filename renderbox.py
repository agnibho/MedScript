# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QMainWindow, QToolBar, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl
import os, webbrowser

class RenderBox(QMainWindow):

    file=""

    def cmd_browse(self):
        webbrowser.open(self.file)

    def cmd_print(self):
        file=QFileDialog.getSaveFileName()
        self.webview.printToPdf(file[0])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("ViewBox")
        self.setGeometry(100, 100, 600, 400)

        action_browse=QAction("Open in Browser", self)
        action_browse.triggered.connect(self.cmd_browse)
        action_print=QAction("Print to PDF", self)
        action_print.triggered.connect(self.cmd_print)

        toolbar=QToolBar("View Toolbar", floatable=False, movable=False)
        toolbar.addAction(action_browse)
        toolbar.addAction(action_print)
        self.addToolBar(toolbar)

        self.webview=QWebEngineView()

        self.setCentralWidget(self.webview)

    def update(self, file):
        try:
            self.file=file
            self.webview.load(QUrl("file:///"+self.file.replace(os.sep, "/")))
        except Exception as e:
            QMessageBox.warning(self,"Display failed", "Failed to display file.")
            self.hide()
            print(e)
