# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import argparse, json, os, sys, shutil

default_config_file=os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "data", "config.json"))

real_dir=os.path.dirname(os.path.realpath(sys.argv[0]))

parser = argparse.ArgumentParser()
parser.add_argument("filename", nargs="?")
parser.add_argument("-c", "--config")
parser.add_argument("-p", "--prescriber")
args = parser.parse_args()

if(args.config is None):
    config_file=default_config_file
else:
    config_file=args.config

default = {
        "data_directory": "data",
        "document_directory": "document",
        "prescriber_directory": "prescriber",
        "prescriber": "prescriber",
        "template_directory": "template",
        "template": "default_prescription",
        "preset_directory": "preset",
        "preset_newline": "True",
        "preset_delimiter": ",",
        "markdown": "False",
        "smime": "False",
        "root_bundle": "",
        "private_key": "",
        "certificate": ""
        }

try:
    with open(config_file) as conf:
        read = json.loads(conf.read())
    config = default | read
except Exception as e:
    print(e)
    config=default

config["filename"]=args.filename
config["data_directory"]=os.path.abspath(os.path.join(real_dir, os.path.expanduser(config["data_directory"])))
config["document_directory"]=os.path.join(config["data_directory"], config["document_directory"])
config["preset_directory"]=os.path.join(config["data_directory"], config["preset_directory"])
config["template_directory"]=os.path.join(config["data_directory"], config["template_directory"])
config["template"]=os.path.join(config["template_directory"], config["template"])
config["resource"]=os.path.abspath(os.path.join(real_dir, "resource"))
if(args.prescriber is None):
    config["prescriber_directory"]=os.path.join(config["data_directory"], config["prescriber_directory"])
    config["prescriber"]=os.path.join(config["prescriber_directory"], config["prescriber"])
    if (not config["prescriber"].endswith(".json")): config["prescriber"]=config["prescriber"]+".json"
else:
    if(not os.path.isabs(args.prescriber)):
        args.prescriber=os.path.join(config["prescriber_directory"], args.prescriber)
    if(os.path.isfile(args.prescriber)):
        config["prescriber"]=args.prescriber
    else:
        config["prescriber"]=os.path.join(config["prescriber_directory"], config["prescriber"])
        print("File "+args.prescriber+" not found.")

os.makedirs(config["data_directory"], exist_ok=True)
os.makedirs(config["document_directory"], exist_ok=True)
os.makedirs(config["prescriber_directory"], exist_ok=True)
os.makedirs(config["preset_directory"], exist_ok=True)
os.makedirs(config["template_directory"], exist_ok=True)
if not os.path.exists(os.path.join(config["data_directory"], "config.json")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "config.json")), os.path.join(config["data_directory"], "config.json"))
if not os.path.exists(os.path.join(config["prescriber_directory"], "prescriber.json")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "prescriber", "prescriber.json")), os.path.join(config["prescriber_directory"], "prescriber.json"))
if not os.path.exists(os.path.join(config["template_directory"], "default")):
    shutil.copytree(os.path.abspath(os.path.join(real_dir, "data", "template", "default")), os.path.join(config["template_directory"], "default"))
if not os.path.exists(os.path.join(config["template_directory"], "medcert")):
    shutil.copytree(os.path.abspath(os.path.join(real_dir, "data", "template", "medcert")), os.path.join(config["template_directory"], "medcert"))
if not os.path.exists(os.path.join(config["preset_directory"], "certify.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "certify.csv")), os.path.join(config["preset_directory"], "certify.csv"))
if not os.path.exists(os.path.join(config["preset_directory"], "note.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "note.csv")), os.path.join(config["preset_directory"], "note.csv"))
if not os.path.exists(os.path.join(config["preset_directory"], "report.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "report.csv")), os.path.join(config["preset_directory"], "report.csv"))
if not os.path.exists(os.path.join(config["preset_directory"], "investigation.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "investigation.csv")), os.path.join(config["preset_directory"], "investigation.csv"))
if not os.path.exists(os.path.join(config["preset_directory"], "advice.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "advice.csv")), os.path.join(config["preset_directory"], "advice.csv"))
if not os.path.exists(os.path.join(config["preset_directory"], "medication.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "medication.csv")), os.path.join(config["preset_directory"], "medication.csv"))
if not os.path.exists(os.path.join(config["preset_directory"], "additional.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "additional.csv")), os.path.join(config["preset_directory"], "additional.csv"))
