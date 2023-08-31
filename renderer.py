# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import os, shutil, tempfile, json, datetime
from jinja2 import Template
from config import config

class Renderer:

    tempdir=None

    def render(self, data_directory):
        source=os.path.join(data_directory, "prescription.json")
        target=os.path.join(data_directory, "template", "output.html")
        template=os.path.join(data_directory, "template", "index.html")
        if not os.path.exists(template):
            shutil.copytree(config["template"], os.path.join(data_directory, "template"), dirs_exist_ok=True)
        with open(source, "r") as source_file, open(target, "w") as target_file:
            with open(template) as template_file:
                template_data = Template(template_file.read())
                data=json.loads(source_file.read())
                try:
                    data["date"]=datetime.datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(e)
                output=template_data.render(data)
                target_file.write(output)
        return(target)
