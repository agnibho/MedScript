# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import os, shutil, glob, tempfile, json
from zipfile import ZipFile
from config import config
from signature import Signature

class FileHandler():

    meta={"type":"MedScript", "version":"0.2"}

    file=""
    directory=""

    def __init__(self, file=""):
        self.reset(file)

    def reset(self, file=""):
        self.file=file
        self.directory=tempfile.TemporaryDirectory()

    def set_file(self, file):
        self.file=file

    def copy(self, file, category="attachment"):
        dirname=os.path.join(self.directory.name, category)
        os.makedirs(dirname, exist_ok=True)
        try:
            shutil.copyfile(file, os.path.join(dirname, os.path.basename(file)))
        except shutil.SameFileError as e:
            print(e)

    def list(self, category="attachment"):
        items=[]
        dirname=os.path.join(self.directory.name, category)
        for f in glob.glob(os.path.join(dirname,"*"), recursive=True):
            items.append(f)
        return(items)

    def save(self, file=None):
        if file is not None:
            self.file=file
        with open(os.path.join(self.directory.name, "meta.json"), "w") as f:
            f.write(json.dumps(self.meta))
        template=os.path.join(self.directory.name, "template")
        os.makedirs(template, exist_ok=True)
        shutil.copytree(config["template"], template, dirs_exist_ok=True)

        with ZipFile(self.file, "w", strict_timestamps=False) as target:
            for f in glob.glob(os.path.join(self.directory.name, "**" ,"*"), recursive=True):
                target.write(f, os.path.relpath(f, self.directory.name))

    def open(self, file=None):
        if file is not None:
            self.file=file
        with ZipFile(self.file, "r", strict_timestamps=False) as source:
            source.extractall(self.directory.name)

    def sign(self, password=""):
        with open(os.path.join(self.directory.name, "prescription.json"), "r") as file:
            data=file.read()
        signature=Signature.sign(data, certificate=config["certificate"], privkey=config["private_key"], password=password)
        with open(os.path.join(self.directory.name, "signature"), "wb") as file:
            file.write(signature)
        shutil.copyfile(config["certificate"], os.path.join(self.directory.name, "certificate.pem"))

    def verify(self):
        with open(os.path.join(self.directory.name, "prescription.json"), "r") as file:
            data=file.read()
        try:
            with open(os.path.join(self.directory.name, "certificate.pem"), "r") as file:
                certificate=file.read()
            with open(os.path.join(self.directory.name, "signature"), "rb") as file:
                signature=file.read()
            return Signature.verify(data, certificate=os.path.join(self.directory.name, "certificate.pem"), signature=signature)
        except FileNotFoundError as e:
            print(e)

    def delete_attachment(self, item):
        try:
            os.unlink(os.path.join(self.directory.name, "attachment", os.path.basename(item)))
        except Exception as e:
            print(e)

    def delete_sign(self):
        try:
            os.unlink(os.path.join(self.directory.name, "certificate.pem"))
            os.unlink(os.path.join(self.directory.name, "signature"))
        except Exception as e:
            print(e)

    def is_signed(self):
        return(os.path.exists(os.path.join(self.directory.name, "certificate.pem")) and (os.path.exists(os.path.join(self.directory.name, "signature.p7m"))))
