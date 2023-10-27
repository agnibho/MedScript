# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import os, importlib
from PyQt6.QtWidgets import QMessageBox
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
                    msg=i.new(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def open(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "open") and callable(i.open)):
                    msg=i.open(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def save(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "save") and callable(i.save)):
                    msg=i.save(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def refresh(self, prescription):
        for i in self.plugins:
            try:
                if(hasattr(i, "refresh") and callable(i.refresh)):
                    msg=i.refresh(prescription)
                    if(msg):
                        QMessageBox.information(None, "Information", msg)
            except Exception as e:
                print(e)

    def run(self, module, prescription):
        try:
            if(hasattr(module, "run") and callable(module.run)):
                msg=module.run(prescription)
                if(msg):
                    QMessageBox.information(None, "Information", msg)
        except Exception as e:
            print(e)
