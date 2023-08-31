# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import json
from config import config

class Prescriber:
    def __init__(self):
        self.read_from(config["prescriber"])

    def set_data(self, name="", qualification="", registration="", address="", contact="", extra=""):
        self.name = name
        self.qualification = qualification
        self.registration = registration
        self.address = address
        self.contact = contact
        self.extra = extra

    def set_data_from_json(self, data):
        self.name = data["name"]
        self.qualification = data["qualification"]
        self.registration = data["registration"]
        self.address = data["address"]
        self.contact = data["contact"]
        self.extra = data["extra"]

    def read_from(self, file):
        with open(file, "r") as f:
            self.set_data_from_json(json.loads(f.read()))

class Prescription:

    file=""

    def __init__(self, date="", id="", name="", age="", sex="", address="", contact="", extra="", mode="", daw="", note="", report="", investigation="", medication="", advice="", prescriber=None):
        self.set_data(date, name, age, sex, address, contact, extra, mode, daw, note, report, investigation, medication, advice)
        if prescriber is None:
            self.prescriber = Prescriber()
        else:
            self.prescriber = prescriber

    def set_data(self, date="", id="", name="", age="", sex="", address="", contact="", extra="", mode="", daw="", note="", report="", investigation="", medication="", advice=""):
        self.date = date
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex
        self.address = address
        self.contact = contact
        self.extra = extra
        self.mode = mode
        self.daw = daw
        self.note = note
        self.report = report
        self.investigation = investigation
        self.medication = medication
        self.advice = advice

    def set_data_from_json(self, data):
        self.prescriber.set_data_from_json(data["prescriber"])
        self.date = data["date"]
        self.id = data["id"]
        self.name = data["name"]
        self.age = data["age"]
        self.sex = data["sex"]
        self.address = data["address"]
        self.contact = data["contact"]
        self.extra = data["extra"]
        self.mode = data["mode"]
        self.daw = data["daw"]
        self.note = data["note"]
        self.report = data["report"]
        self.investigation = data["investigation"]
        self.medication = data["medication"]
        self.advice = data["advice"]

    def get_json(self):
        return(json.dumps(self, default=lambda o: o.__dict__, indent=4))

    def write_to(self, file):
        with open(file, "w") as f:
            f.write(self.get_json())
        self.file=file

    def read_from(self, file):
        with open(file, "r") as f:
            self.set_data_from_json(json.loads(f.read()))
        self.file=file
