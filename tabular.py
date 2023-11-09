# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from config import config
from glob import glob
from zipfile import ZipFile
import logging, os, json, csv

class Tabular():

    def export(filename):
        try:
            files=glob(os.path.join(config["document_directory"], "**", "*.mpaz"), recursive=True)
            with open(filename, "w", newline="") as ss:
                writer=csv.writer(ss, delimiter=config["preset_delimiter"], quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["pid", "id", "date", "name", "dob", "age", "sex", "address", "contact", "extra", "mode", "daw", "diagnosis", "note", "report", "advice", "investigation", "medication", "additional", "certificate", "prescriber"])
                for file in files:
                    try:
                        with ZipFile(file) as zf:
                            with zf.open("prescription.json") as pf:
                                pres=json.loads(pf.read())
                                writer.writerow([pres["pid"], pres["id"], pres["date"], pres["name"], pres["dob"], pres["age"], pres["sex"], pres["address"], pres["contact"], pres["extra"], pres["mode"], pres["daw"], pres["diagnosis"], pres["note"], pres["report"], pres["advice"], pres["investigation"], pres["medication"], pres["additional"], pres["certificate"], pres["prescriber"]["name"]])
                    except Exception as e:
                        logging.exception(e)
        except FileNotFoundError as e:
            logging.warning(e)
        except Exception as e:
            logging.exception(e)
