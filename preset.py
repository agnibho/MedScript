# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, os, csv
from glob import glob
from config import config

class Preset():

    target=""
    data={}

    def __init__(self, target, skip_first=True, text_as_key=False):
        self.target=target
        self.data={}
        self.load(skip_first, text_as_key);

    def load(self, skip_first=True, text_as_key=False):
        try:
            buf={}
            for file in glob(os.path.join(config["preset_directory"], self.target+"*"+".csv")):
                with open(file, "r") as f:
                    reader=csv.reader(f, delimiter=config["preset_delimiter"])
                    if skip_first:
                        next(reader)
                    for row in reader:
                        try:
                            self.data[row[0]]=row[1]
                            if text_as_key:
                                buf[row[1].strip()]=row[1]
                        except IndexError as e:
                            logging.warning(e)
            self.data = buf | self.data
        except FileNotFoundError as e:
            logging.warning(e)
        except IndexError as e:
            logging.warning(e)
        except StopIteration as e:
            logging.warning(e)
        except Exception as e:
            logging.exception(e)
