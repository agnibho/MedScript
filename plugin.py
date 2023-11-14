# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, os, importlib, copy, json
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QInputDialog, QFileDialog, QVBoxLayout
from PyQt6.QtCore import QObject, QThread, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from glob import glob
from config import config

class Plugin(QObject):

    update=pyqtSignal()

    plugins=[]
    names=[]
    workers=[]

    def __init__(self):
        super().__init__()
        if(config["enable_plugin"]):
            self.load()

    def load(self):
        plugin_list=glob(os.path.join(config["plugin_directory"], "*"))
        for i in plugin_list:
            try:
                if(os.path.isdir(i)):
                    spec=importlib.util.spec_from_file_location(os.path.basename(i), os.path.join(i, "main.py"))
                    mod=importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self.plugins.append(mod)
            except Exception as e:
                logging.warning(i+":"+str(e))

    def get_name(self, mod):
            try:
                return(mod.name)
            except Exception as e:
                return(mod.__name__)

    def commands(self):
        cmds=[]
        for i in self.plugins:
            if(hasattr(i, "run") and callable(i.run)):
                cmds.append([i, self.get_name(i)])
        return(cmds)

    def new(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "new") and callable(i.new)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    prescription_copy=copy.deepcopy(prescription)
                    message=i.new(prescription_copy)
                    prescription.set_data_from_copy(prescription_copy)
                    if(message):
                        self.showMessage(message)
            except Exception as e:
                logging.exception(e)

    def open(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "open") and callable(i.open)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    prescription_copy=copy.deepcopy(prescription)
                    message=i.open(prescription_copy)
                    prescription.set_data_from_copy(prescription_copy)
                    if(message):
                        self.showMessage(message)
            except Exception as e:
                logging.exception(e)

    def save(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "save") and callable(i.save)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    prescription_copy=copy.deepcopy(prescription)
                    message=i.save(prescription_copy)
                    prescription.set_data_from_copy(prescription_copy)
                    if(message):
                        self.showMessage(message)
            except Exception as e:
                logging.exception(e)

    def refresh(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "refresh") and callable(i.refresh)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    prescription_copy=copy.deepcopy(prescription)
                    message=i.refresh(prescription_copy)
                    prescription.set_data_from_copy(prescription_copy)
                    if(message):
                        self.showMessage(message)
            except Exception as e:
                logging.exception(e)

    def run(self, module, prescription):
        try:
            if(hasattr(module, "web") and callable(module.web)):
                    self.webapp=WebApp()
                    self.webapp.done.connect(lambda: self.update.emit())
                    prescription_copy=copy.deepcopy(prescription)
                    url, data=module.web(prescription_copy)
                    prescription.set_data_from_copy(prescription_copy)
                    self.webapp.load(module, QUrl(url), prescription, data)
                    self.webapp.show()
            elif(hasattr(module, "run") and callable(module.run)):
                if(hasattr(module, "confirm") and module.confirm):
                    if(QMessageBox.StandardButton.Yes!=QMessageBox.question(None,"Confirm", module.confirm)):
                        return
                if(hasattr(module, "input") and callable(module.input)):
                    module.input(self.input())
                if(hasattr(module, "fileopen") and callable(module.fileopen)):
                    module.fileopen(QFileDialog.getOpenFileName()[0])
                if(hasattr(module, "filesave") and callable(module.filesave)):
                    module.filesave(QFileDialog.getSaveFileName()[0])
                if(hasattr(module, "background") and module.background):
                    self.showMessage("Module "+module.__name__+" will run in background.")
                    self.workers.append(Worker(module.run, prescription))
                    index=len(self.workers)-1
                    self.workers[index].setIndex(index)
                    self.workers[index].pluginComplete.connect(self.showMessage)
                    self.workers[index].start()
                else:
                    prescription_copy=copy.deepcopy(prescription)
                    message=module.run(prescription_copy)
                    prescription.set_data_from_copy(prescription_copy)
                    if(message):
                        self.showMessage(message)
        except Exception as e:
            logging.exception(e)

    def input(self):
        try:
            text, ok=QInputDialog.getText(None, "User input", "Enter text:")
            if text and ok:
                return text
            else:
                return ""
        except Exception as e:
            logging.exception(e)

    def showMessage(self, message, index=None):
        QMessageBox.information(None, "Information", message)
        if index is not None:
            self.workers[index]=None

class WebApp(QMainWindow):

    done=pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("WebApp Plugin")
        self.setGeometry(100, 100, 400, 400)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))

        self.webview=QWebEngineView()
        self.setCentralWidget(self.webview)

    def load(self, module, url, prescription, data):
        self.module=module
        self.webview.load(url)
        self.channel=QWebChannel()
        self.js=JS(module, prescription, data)
        self.channel.registerObject("js", self.js)
        self.webview.page().setWebChannel(self.channel)
        self.js.done.connect(lambda: self.done.emit())
        self.js.hide.connect(lambda: self.close())

class JS(QObject):

    done=pyqtSignal()
    hide=pyqtSignal()

    def __init__(self, module, prescription, data):
        super().__init__()
        self.module=module
        self.prescription=prescription
        self.data=data

    @pyqtSlot(str)
    def run(self, result):
        try:
            prescription_copy=copy.deepcopy(self.prescription)
            message=self.module.run(prescription_copy, result)
            self.prescription.set_data_from_copy(prescription_copy)
            if(message):
                QMessageBox.information(None, "Information", message)
            self.done.emit()
        except Exception as e:
            logging.error(self.module)
            logging.exception(e)

    @pyqtSlot(result=str)
    def get(self):
        return self.data

    @pyqtSlot()
    def close(self):
        self.hide.emit()

class Worker(QThread):

    pluginComplete=pyqtSignal(str, int)
    function=None
    prescription=None
    index=None

    def __init__(self, function, prescription):
        super().__init__()
        self.function=function
        self.prescription=prescription

    def setIndex(self, index):
        self.index=index

    def run(self):
        try:
            prescription_copy=copy.deepcopy(self.prescription)
            message=self.function(prescription_copy)
            self.pluginComplete.emit(message, self.index)
        except Exception as e:
            logging.exception(e)
