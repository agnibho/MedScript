# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import argparse, json, os

default_config_file=os.path.abspath(os.path.join("config", "config.json"))

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
        "config_directory": "config",
        "data_directory": "data",
        "document_directory": "document",
        "prescriber_directory": "prescriber",
        "prescriber": "prescriber",
        "template_directory": "template",
        "template": "default",
        "preset_directory": "preset",
        "preset_newline": "True"
        }

with open(config_file) as conf:
    read = json.loads(conf.read())

config = default | read
config["filename"]=args.filename
config["data_directory"]=os.path.abspath(config["data_directory"])
config["document_directory"]=os.path.join(config["data_directory"], config["document_directory"])
config["template_directory"]=os.path.join(config["data_directory"], config["template_directory"])
config["template"]=os.path.join(config["template_directory"], config["template"])
if(args.prescriber is None):
    config["prescriber_directory"]=os.path.join(config["data_directory"], config["prescriber_directory"])
    config["prescriber"]=os.path.join(config["prescriber_directory"], config["prescriber"])
    if (not config["prescriber"].endswith(".json")): config["prescriber"]=config["prescriber"]+".json"
else:
    if(not os.path.isabs(args.prescriber)):
        args.prescriber=os.path.join(config["config_directory"], args.prescriber)
    if(os.path.isfile(args.prescriber)):
        config["prescriber"]=args.prescriber
    else:
        config["prescriber"]=os.path.join(config["config_directory"], config["prescriber"])
        print("File "+args.prescriber+" not found.")
