# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, json
from config import config

class Prescriber:
    def __init__(self, file=None):
        if file is None:
            self.read_from(config["prescriber"])
        else:
            self.read_from(file)

    def set_data(self, name="", qualification="", registration="", address="", contact="", extra="", properties={}):
        self.name = name
        self.qualification = qualification
        self.registration = registration
        self.address = address
        self.contact = contact
        self.extra = extra
        self.properties = properties

    def get_json(self):
        return(json.dumps(self, default=lambda o: o.__dict__, indent=4))

    def set_data_from_json(self, data):
        try:
            self.name = data["name"]
            self.qualification = data["qualification"]
            self.registration = data["registration"]
            self.address = data["address"]
            self.contact = data["contact"]
            self.extra = data["extra"]
            if("properties" in data and type(properties) is dict):
                self.properties = data["properties"]
            else:
                self.properties = {}
        except Exception as e:
            logging.exception(e)

    def read_from(self, file):
        try:
            with open(file, "r") as f:
                self.set_data_from_json(json.loads(f.read()))
        except Exception as e:
            self.name = ""
            self.qualification = ""
            self.registration = ""
            self.address = ""
            self.contact = ""
            self.extra = ""
            self.properties = {}

class Prescription:

    file=""

    def __init__(self, date="", id="", pid="", name="", dob="", age="", sex="", address="", contact="", extra="", mode="", daw="", diagnosis="", note="", report="", advice="", investigation="", medication="", additional="", certificate="", custom=None, properties={}, prescriber=None):
        self.set_data(date, name, dob, age, sex, address, contact, extra, mode, daw, diagnosis, note, report, advice, investigation, medication, additional, certificate, custom, properties)
        if prescriber is None:
            self.prescriber = Prescriber()
        else:
            self.prescriber = prescriber

    def set_data(self, date="", id="", pid="", name="", dob="", age="", sex="", address="", contact="", extra="", mode="", daw="", diagnosis="", note="", report="", advice="", investigation="", medication="", additional="", certificate="", custom=None, properties={}):
        self.date = date
        self.id = id
        self.pid = pid
        self.name = name
        if(age):
            self.dob = ""
            self.age = age
        else:
            self.dob = dob
            self.age = ""
        self.sex = sex
        self.address = address
        self.contact = contact
        self.extra = extra
        self.mode = mode
        self.daw = daw
        self.diagnosis = diagnosis
        self.note = note
        self.report = report
        self.advice = advice
        self.investigation = investigation
        self.medication = medication
        self.additional = additional
        self.certificate = certificate
        self.custom = custom
        self.properties = properties

    def set_data_from_json(self, data):
        try:
            self.prescriber.set_data_from_json(data.get("prescriber"))
            self.date = data.get("date")
            self.id = data.get("id")
            self.pid = data.get("pid")
            self.name = data.get("name")
            self.dob = data.get("dob")
            self.age = data.get("age")
            self.sex = data.get("sex")
            self.address = data.get("address")
            self.contact = data.get("contact")
            self.extra = data.get("extra")
            self.mode = data.get("mode")
            self.daw = data.get("daw")
            self.diagnosis = data.get("diagnosis")
            self.note = data.get("note")
            self.report = data.get("report")
            self.advice = data.get("advice")
            self.investigation = data.get("investigation")
            self.medication = data.get("medication")
            self.additional = data.get("additional")
            self.certificate = data.get("certificate")
            self.custom = data.get("custom")
            if("properties" in data):
                self.properties = data["properties"]
            else:
                self.properties = {}
        except Exception as e:
            logging.exception(e)

    def set_data_from_copy(self, prescription_copy):
        try:
            self.date = prescription_copy.date
            self.id = prescription_copy.id
            self.pid = prescription_copy.pid
            self.name = prescription_copy.name
            self.dob = prescription_copy.dob
            self.age = prescription_copy.age
            self.sex = prescription_copy.sex
            self.address = prescription_copy.address
            self.contact = prescription_copy.contact
            self.extra = prescription_copy.extra
            self.mode = prescription_copy.mode
            self.daw = prescription_copy.daw
            self.diagnosis = prescription_copy.diagnosis
            self.note = prescription_copy.note
            self.report = prescription_copy.report
            self.advice = prescription_copy.advice
            self.investigation = prescription_copy.investigation
            self.medication = prescription_copy.medication
            self.additional = prescription_copy.additional
            self.certificate = prescription_copy.certificate
            self.custom = prescription_copy.custom
            if(type(prescription_copy.properties) is dict):
                self.properties = prescription_copy.properties
            else:
                self.properties = {}
            self.prescriber = prescription_copy.prescriber
        except Exception as e:
            logging.exception(e)


    def get_json(self):
        return(json.dumps(self, default=lambda o: o.__dict__, indent=4))

    def write_to(self, file):
        with open(file, "w") as f:
            try:
                del self.file
            except AttributeError as e:
                pass
            except Exception as e:
                logging.exception(e)
            f.write(self.get_json())
        self.file=file

    def read_from(self, file):
        with open(file, "r") as f:
            self.set_data_from_json(json.loads(f.read()))
        self.file=file

    def reload_prescriber(self, file=None):
        self.prescriber=Prescriber(file)
