# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import os, importlib, threading, copy
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QFileDialog
from glob import glob
from config import config

class Plugin():

    plugins=[]
    names=[]

    def __init__(self):
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
                print(i, ":", e)

    def get_name(self, mod):
            try:
                return(mod.name)
            except Exception as e:
                return(mod.__name__)

    def background(self, function, prescription):
        prescription_copy=copy.deepcopy(prescription)
        msg=function(prescription_copy)
        if(msg):
            QMessageBox.information(None, "Information", msg)

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
                    msg=i.new(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def open(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "open") and callable(i.open)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    msg=i.open(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def save(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "save") and callable(i.save)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    msg=i.save(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def refresh(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "refresh") and callable(i.refresh)):
                    if(hasattr(i, "input") and callable(i.input)):
                        i.input(self.input())
                    msg=i.refresh(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def run(self, module, prescription):
        try:
            if(hasattr(module, "run") and callable(module.run)):
                if(hasattr(module, "input") and callable(module.input)):
                    module.input(self.input())
                if(hasattr(module, "fileopen") and callable(module.fileopen)):
                    module.fileopen(QFileDialog.getOpenFileName()[0])
                if(hasattr(module, "filesave") and callable(module.filesave)):
                    module.filesave(QFileDialog.getSaveFileName()[0])
                if(module.background):
                    QMessageBox.information(None, "Information", "Module "+module.__name__+" will run in background.")
                    threading.Thread(target=self.background, args=[module.run, prescription]).start()
                else:
                    msg=module.run(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
        except Exception as e:
            print(e)

    def input(self):
        try:
            text, ok=QInputDialog.getText(None, "User input", "Enter text:")
            if text and ok:
                return text
            else:
                return ""
        except Exception as e:
            print(e)
