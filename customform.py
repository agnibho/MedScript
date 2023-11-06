# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QDateTimeEdit, QCalendarWidget
from PyQt6.QtCore import QDateTime
from glob import glob
import os, json, sys, dateutil.parser
from config import config

class CustomForm(QWidget):

    forms=[]
    custom=[]
    inputs=[]

    def load(self):
        for i in glob(os.path.join(config["form_directory"], "*")):
            with open(i) as f:
                try:
                    self.forms.append(json.loads(f.read()))
                except Exception as e:
                    print(e)
        for i in self.forms:
            try:
                for j in i["form"]:
                    self.custom.append({j["name"]: ""})
                    if("type" in j and j["type"]=="text"):
                        self.inputs.append([j["description"], QTextEdit()])
                    elif("type" in j and j["type"]=="date"):
                        d=QDateTimeEdit()
                        d.setDisplayFormat("MMMM dd, yyyy hh:mm a")
                        d.setCalendarPopup(True)
                        d.setCalendarWidget(QCalendarWidget())
                        self.inputs.append([j["description"], d])
                    elif("type" in j and j["type"]=="check"):
                        self.inputs.append([j["description"], QCheckBox()])
                    else:
                        self.inputs.append([j["description"], QLineEdit()])
            except Exception as e:
                raise(e)

    def getData(self):
        try:
            for index, item in enumerate(self.custom):
                if(isinstance(self.inputs[index][1], QLineEdit)):
                    self.custom[index][list(item)[0]]=self.inputs[index][1].text()
                elif(isinstance(self.inputs[index][1], QTextEdit)):
                    self.custom[index][list(item)[0]]=self.inputs[index][1].toPlainText()
                elif(isinstance(self.inputs[index][1], QCheckBox)):
                    self.custom[index][list(item)[0]]=self.inputs[index][1].isChecked()
                elif(isinstance(self.inputs[index][1], QDateTimeEdit)):
                    self.custom[index][list(item)[0]]=self.inputs[index][1].text()
        except Exception as e:
            print(e)
        return(self.custom)

    def setData(self, custom=False):
        try:
            if(custom):
                self.custom=custom
            for index, item in enumerate(self.custom):
                if(isinstance(self.inputs[index][1], QLineEdit)):
                    self.inputs[index][1].setText(self.custom[index][list(item)[0]])
                elif(isinstance(self.inputs[index][1], QTextEdit)):
                    self.inputs[index][1].setText(self.custom[index][list(item)[0]])
                elif(isinstance(self.inputs[index][1], QCheckBox)):
                    self.inputs[index][1].setChecked(bool(self.custom[index][list(item)[0]]))
                elif(isinstance(self.inputs[index][1], QDateTimeEdit)):
                    pdate=dateutil.parser.parse(self.custom[index][list(item)[0]])
                    d=QDateTime.fromString(pdate.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
                    self.inputs[index][1].setDateTime(d)
        except Exception as e:
            print(e)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if(config["enable_form"]):
            self.load()

        layout=QFormLayout(self)
        for i in self.inputs:
            layout.addRow(i[0], i[1])
