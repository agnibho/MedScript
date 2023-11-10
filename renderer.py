# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, os, shutil, tempfile, json, datetime, re
from markdown import markdown
from jinja2 import Template
from config import config

class Renderer:

    tempdir=None

    def render(self, data_directory):
        try:
            source=os.path.join(data_directory, "prescription.json")
            target=os.path.join(data_directory, "template", "output.html")
            template=os.path.join(data_directory, "template", "index.html")
            if not os.path.exists(template):
                shutil.copytree(config["template"], os.path.join(data_directory, "template"), dirs_exist_ok=True)
            with open(source, "r") as source_file, open(target, "w") as target_file:
                with open(template) as template_file:
                    template_data = Template(template_file.read())
                    data=self.process_medication(self.process_diagnosis(json.loads(source_file.read())))
                    if config["markdown"]:
                        data=self.render_markdown(data)
                    try:
                        data["date"]=datetime.datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        logging.exception(e)
                    output=template_data.render(data)
                    target_file.write(output)
            return(target)
        except Exception as e:
            logging.exception(e)

    def process_diagnosis(self, data):
        diagnosis_list=[]
        for d in data["diagnosis"].split(";"):
            diagnosis_list.append(d.strip())
        data["diagnosis_list"]=diagnosis_list
        return data

    def process_medication(self, data):
        medication_list=[]
        pattern=re.compile(r".*?\[(.*)\].*")
        for line in data["medication"].splitlines():
            if(line):
                try:
                    f2=re.search(pattern, line).group(1)
                    f1=line.replace("["+f2+"]", "")
                    medication_list.append([f1, f2])
                except AttributeError:
                    medication_list.append([line, ""])
        data["medication_list"]=medication_list
        return data

    def render_markdown(self, data):
        data["extra"]=markdown(data["extra"])
        data["note"]=markdown(data["note"])
        data["report"]=markdown(data["report"])
        data["advice"]=markdown(data["advice"])
        data["investigation"]=markdown(data["investigation"])
        data["additional"]=markdown(data["additional"])
        return data
