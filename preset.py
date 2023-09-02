# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import csv

class Preset():

    file=""
    data={}

    def __init__(self, file):
        self.file=file;
        self.data={}
        self.load();

    def load(self):
        try:
            with open(self.file, "r") as f:
                reader=csv.reader(f)
                next(reader)
                for row in reader:
                    self.data[row[0]]=row[1]
        except FileNotFoundError as e:
            print(e)
