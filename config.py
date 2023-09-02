# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import argparse, json, os

parser = argparse.ArgumentParser()
parser.add_argument("filename", nargs="?")
parser.add_argument("-c", "--config")
parser.add_argument("-p", "--prescriber")
args = parser.parse_args()

if(args.config is None):
    config_file=os.path.join("config", "config.json")
else:
    config_file=args.config

default = {
        "data_directory": "data",
        "config_directory": "config",
        "template_directory": "template",
        "template": "default",
        "preset_directory": "preset",
        "preset_newline": "True",
        "prescriber": "prescriber.json"
        }

with open(config_file) as conf:
    read = json.loads(conf.read())

config = default | read
config["filename"]=args.filename
config["template"]=os.path.join(config["template_directory"], config["template"])
if(args.prescriber is None):
    config["prescriber"]=os.path.join(config["config_directory"], config["prescriber"])
else:
    if(not os.path.isabs(args.prescriber)):
        args.prescriber=os.path.join(config["config_directory"], args.prescriber)
    if(os.path.isfile(args.prescriber)):
        config["prescriber"]=args.prescriber
    else:
        config["prescriber"]=os.path.join(config["config_directory"], config["prescriber"])
        print("File "+args.prescriber+" not found.")
