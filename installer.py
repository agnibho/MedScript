# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox, QFileDialog
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from glob import glob
from zipfile import ZipFile
from config import config
import logging, os, tempfile, shutil

class Installer(QMainWindow):

    preset={"name":[], "path":[]}
    template={"name":[], "path":[]}
    form={"name":[], "path":[]}
    plugin={"name":[], "path":[]}

    protected=["note", "report", "advice", "investigation", "medication", "additional", "certificate", "default", "medcert", "<unchanged>"]
    directory=None

    def cmd_install(self):
        try:
            file=QFileDialog.getOpenFileName(self, "Open Package", config["data_directory"], "Zip (*.zip);; All Files (*)")[0]
            self.directory=tempfile.TemporaryDirectory()
            with ZipFile(file, "r", strict_timestamps=False) as package:
                package.extractall(self.directory.name)
            for i in glob(os.path.join(self.directory.name, "preset", "*.csv")):
                name=os.path.splitext(os.path.basename(i))[0]
                if name not in self.protected:
                    if name not in self.preset["name"]:
                        if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm install", "Installing PRESET <strong>"+name+"</strong>. Continue?")):
                            self.copy(i, config["preset_directory"])
                    else:
                        QMessageBox.information(self, "File exists", "PRESET <strong>"+name+"</strong> is already installed.")
            for i in glob(os.path.join(self.directory.name, "template", "*")):
                if os.path.exists(os.path.join(i, "index.html")):
                    name=os.path.basename(i)
                    if name not in self.protected:
                        if name not in self.template["name"]:
                            if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm install", "Installing TEMPLATE <strong>"+name+"</strong>. Continue?")):
                                self.copy(i, os.path.join(config["template_directory"], name))
                        else:
                            QMessageBox.information(self, "File exists", "TEMPLATE <strong>"+name+"</strong> is already installed.")
            for i in glob(os.path.join(self.directory.name, "form", "*.json")):
                name=os.path.splitext(os.path.basename(i))[0]
                if name not in self.protected:
                    if name not in self.form["name"]:
                        if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm install", "Installing FORM <strong>"+name+"</strong>. Continue?")):
                            self.copy(i, config["form_directory"])
                    else:
                        QMessageBox.information(self, "File exists", "FORM <strong>"+name+"</strong> is already installed.")
            for i in glob(os.path.join(self.directory.name, "plugin", "*")):
                if os.path.exists(os.path.join(i, "main.py")):
                    name=os.path.basename(i)
                    if name not in self.protected:
                        if name not in self.plugin["name"]:
                            if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm install", "Installing PLUGIN <strong>"+name+"</strong>. Continue?")):
                                self.copy(i, os.path.join(config["plugin_directory"], name))
                        else:
                            QMessageBox.information(self, "File exists", "PLUGIN <strong>"+name+"</strong> is already installed.")
            QMessageBox.information(self, "Restart", "Please restart MedScript for the changes to take effect.")
        except Exception as e:
            logging.exception(e)

    def cmd_uninstall(self):
        txt=self.installed.currentItem().text().split("\t")
        name=txt[1]
        group=txt[0].replace("[", "").replace("]", "")
        if name not in self.protected:
            if(group=="preset"):
                if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm uninstall", "Uninstalling PRESET <strong>"+name+"</strong>. Continue?")):
                    idx=self.preset["name"].index(name)
                    path=self.preset["path"][idx]
                    self.delete(path)
            elif(group=="template"):
                if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm uninstall", "Uninstalling TEMPLATE <strong>"+name+"</strong>. Continue?")):
                    idx=self.template["name"].index(name)
                    path=self.template["path"][idx]
                    self.delete(path)
            elif(group=="form"):
                if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm uninstall", "Uninstalling FORM <strong>"+name+"</strong>. Continue?")):
                    idx=self.form["name"].index(name)
                    path=self.form["path"][idx]
                    self.delete(path)
            elif(group=="plugin"):
                if(QMessageBox.StandardButton.Yes==QMessageBox.question(self, "Confirm uninstall", "Uninstalling PLUGIN <strong>"+name+"</strong>. Continue?")):
                    idx=self.plugin["name"].index(name)
                    path=self.plugin["path"][idx]
                    self.delete(path)
            QMessageBox.information(self, "Restart", "Please restart MedScript for the changes to take effect.")
        else:
            QMessageBox.information(self, "Item protected", "Protected items cannot be deleted.")

    def delete(self, path):
        try:
            os.unlink(path)
        except (IsADirectoryError, PermissionError):
            shutil.rmtree(path)
        except Exception as e:
            QMessageBox.critical(self, "Failed", "Uninstallation failed. Please manually delete package.")
            logging.critical(e)
        self.load()

    def copy(self, path, destination):
        try:
            shutil.copytree(path, destination)
        except NotADirectoryError:
            shutil.copy(path, destination)
        except Exception as e:
            logging.critical(e)
        self.load()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript Package Installer")
        self.setGeometry(200, 200, 600, 400)

        widget=QWidget(self)
        layout=QVBoxLayout(widget)
        self.installed=QListWidget()
        layout.addWidget(self.installed)
        layout2=QHBoxLayout()
        button_install=QPushButton("Install")
        button_install.clicked.connect(self.cmd_install)
        button_uninstall=QPushButton("Uninstall")
        button_uninstall.clicked.connect(self.cmd_uninstall)
        layout2.addWidget(button_install)
        layout2.addWidget(button_uninstall)
        layout.addLayout(layout2)

        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon(os.path.join("resource", "icon_medscript.ico")))

        self.load()

    def load(self, file=None):
        self.preset={"name":[], "path":[]}
        self.template={"name":[], "path":[]}
        self.form={"name":[], "path":[]}
        self.plugin={"name":[], "path":[]}
        self.installed.clear()
        try:
            for i in glob(os.path.join(config["preset_directory"], "*.csv")):
                self.preset["name"].append(os.path.splitext(os.path.basename(i))[0])
                self.preset["path"].append(i)
            for i in glob(os.path.join(config["template_directory"], "*")):
                if(os.path.exists(os.path.join(i, "index.html"))):
                   self.template["name"].append(os.path.basename(i))
                   self.template["path"].append(i)
            for i in glob(os.path.join(config["form_directory"], "*.json")):
                self.form["name"].append(os.path.splitext(os.path.basename(i))[0])
                self.form["path"].append(i)
            for i in glob(os.path.join(config["plugin_directory"], "*")):
                if(os.path.exists(os.path.join(i, "main.py"))):
                   self.plugin["name"].append(os.path.basename(i))
                   self.plugin["path"].append(i)

            for i in self.preset["name"]:
                if i not in self.protected:
                    self.installed.addItem("[preset]\t"+i)
            for i in self.template["name"]:
                if i not in self.protected:
                    self.installed.addItem("[template]\t"+i)
            for i in self.form["name"]:
                if i not in self.protected:
                    self.installed.addItem("[form]\t"+i)
            for i in self.plugin["name"]:
                if i not in self.protected:
                    self.installed.addItem("[plugin]\t"+i)
        except Exception as e:
            logging.exception(e)
