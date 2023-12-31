# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, argparse, json, os, sys, shutil, copy

default_config_file=os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "data", "config.json"))

real_dir=os.path.dirname(os.path.realpath(sys.argv[0]))

with open(os.path.join(real_dir, "info.json")) as info_file:
    info=json.loads(info_file.read())

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
        "template": "default",
        "preset_directory": "preset",
        "form_directory": "form",
        "enable_form": False,
        "age_default": True,
        "plugin_directory": "plugin",
        "enable_plugin": True,
        "log_directory": "log",
        "preset_newline": True,
        "preset_delimiter": ",",
        "markdown": False,
        "check_update": False,
        "smime": False,
        "root_bundle": "",
        "private_key": "",
        "certificate": ""
        }

try:
    with open(config_file) as conf:
        read = json.loads(conf.read())
    config = default | read
except FileNotFoundError as e:
    logging.critical(e)
    config=default
except Exception as e:
    logging.exception(e)
    config=default

config_orig=copy.deepcopy(config)
config["filename"]=args.filename
config["data_directory"]=os.path.abspath(os.path.join(real_dir, os.path.expanduser(config["data_directory"])))
config["document_directory"]=os.path.join(config["data_directory"], config["document_directory"])
config["preset_directory"]=os.path.join(config["data_directory"], config["preset_directory"])
config["form_directory"]=os.path.join(config["data_directory"], config["form_directory"])
config["plugin_directory"]=os.path.join(config["data_directory"], config["plugin_directory"])
config["template_directory"]=os.path.join(config["data_directory"], config["template_directory"])
config["template"]=os.path.join(config["template_directory"], config["template"])
config["log_directory"]=os.path.join(config["data_directory"], config["log_directory"])
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
        logging.warning("File "+args.prescriber+" not found.")

os.makedirs(config["data_directory"], exist_ok=True)
os.makedirs(config["document_directory"], exist_ok=True)
os.makedirs(config["prescriber_directory"], exist_ok=True)
os.makedirs(config["preset_directory"], exist_ok=True)
os.makedirs(config["form_directory"], exist_ok=True)
os.makedirs(config["plugin_directory"], exist_ok=True)
os.makedirs(config["template_directory"], exist_ok=True)
os.makedirs(config["log_directory"], exist_ok=True)
if not os.path.exists(os.path.join(config["data_directory"], "config.json")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "config.json")), os.path.join(config["data_directory"], "config.json"))
if not os.path.exists(os.path.join(config["prescriber_directory"], "prescriber.json")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "prescriber", "prescriber.json")), os.path.join(config["prescriber_directory"], "prescriber.json"))
if not os.path.exists(os.path.join(config["template_directory"], "default")):
    shutil.copytree(os.path.abspath(os.path.join(real_dir, "data", "template", "default")), os.path.join(config["template_directory"], "default"))
if not os.path.exists(os.path.join(config["template_directory"], "medcert")):
    shutil.copytree(os.path.abspath(os.path.join(real_dir, "data", "template", "medcert")), os.path.join(config["template_directory"], "medcert"))
if not os.path.exists(os.path.join(config["preset_directory"], "certificate.csv")):
    shutil.copyfile(os.path.abspath(os.path.join(real_dir, "data", "preset", "certificate.csv")), os.path.join(config["preset_directory"], "certificate.csv"))
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
