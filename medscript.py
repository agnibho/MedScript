# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, sys, os
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication
from window import MainWindow
from config import config

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO,
            format="[%(asctime)s] (%(module)s / %(funcName)s) %(levelname)s : %(message)s",
            handlers=[RotatingFileHandler(os.path.join(config["log_directory"], "log.txt"), maxBytes=100000, backupCount=9), logging.StreamHandler()],
            force=True
            )
    app=QApplication(sys.argv)
    with open(os.path.join(config["resource"], "style.qss")) as qss:
        app.setStyleSheet(qss.read())
    window=MainWindow()
    sys.exit(app.exec())
