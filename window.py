# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging, os, sys, datetime, dateutil.parser, shutil, json, copy, threading
from PyQt6.QtCore import Qt, QDateTime, QDate, QSize, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMainWindow, QMessageBox, QLabel, QPushButton, QLineEdit, QTextEdit, QDateTimeEdit, QDateEdit, QCalendarWidget, QListWidget, QComboBox, QCheckBox, QRadioButton, QButtonGroup, QVBoxLayout, QHBoxLayout, QFormLayout, QToolBar, QTabWidget, QStatusBar, QFileDialog, QInputDialog, QCompleter, QSizePolicy
from PyQt6.QtGui import QAction, QIcon
from pathlib import Path
from hashlib import md5
from urllib import request
from packaging import version
from functools import partial

from config import config, info, real_dir
from prescription import Prescription, Prescriber
from renderer import Renderer
from filehandler import FileHandler
from renderbox import RenderBox, UnrenderBox
from setting import EditConfiguration, EditPrescriber, SelectPrescriber
from editpreset import EditPreset
from viewbox import ViewBox
from preset import Preset
from index import Index
from customform import CustomForm
from plugin import Plugin
from installer import Installer

class MainWindow(QMainWindow):

    signal_view=pyqtSignal(str)
    signal_update=pyqtSignal(str)

    current_file=FileHandler()
    prescription=Prescription()
    prescriber=Prescriber()
    renderer=Renderer()
    plugin=Plugin()
    save_state=md5("".encode()).hexdigest()
    unchanged_state=False

    def cmd_new(self):
        if(self.confirm_close()):
            self.new_doc()

    def cmd_open(self, file=None):
        if(self.confirm_close()):
            try:
                self.current_file.reset()
                if(file):
                    self.current_file.set_file(file)
                else:
                    self.current_file.set_file(QFileDialog.getOpenFileName(self, "Open File", config["document_directory"], "Prescriptions (*.mpaz);; All Files (*)")[0])
                self.current_file.open()
                self.prescription.read_from(os.path.join(self.current_file.directory.name,"prescription.json"))
                self.plugin.open(self.prescription)
                self.load_interface_from_instance()
                self.update_instance()
                self.save_state=md5(self.prescription.get_json().encode()).hexdigest()
                self.load_attachment(self.current_file.list())
                self.unchanged_state=True
            except FileNotFoundError as e:
                logging.warning(e)
            except Exception as e:
                QMessageBox.warning(self,"Open failed", "Failed to open file.")
                logging.exception(e)

    def cmd_copy(self, data):
        self.cmd_new()
        self.prescription.set_data_from_json(data)
        self.prescription.id=""
        self.prescription.date=None
        self.load_interface_from_instance()
        self.refresh()

    def cmd_save(self, save_as=False):
        self.update_instance()
        self.plugin.save(self.prescription)
        if(self.input_template.currentText()!="<unchanged>"):
            change_template=True
            template=self.input_template.currentText()
        else:
            change_template=False
        self.load_interface_from_instance()
        suggest=self.prescription.id if(self.prescription.id) else self.prescription.name
        suggest=os.path.abspath(os.path.join(config["document_directory"], suggest)+".mpaz")
        if(save_as or not self.unchanged_state or QMessageBox.StandardButton.Yes==QMessageBox.question(self,"Confirm change", "Modify the original file?")):
            try:
                if not os.path.exists(self.current_file.file):
                    filename=QFileDialog.getSaveFileName(self, "Save File", suggest, "Prescriptions (*.mpaz);; All Files (*)")[0]
                    if(len(filename)<=0):
                        return
                    if(not filename.endswith(".mpaz")):
                       filename=filename+".mpaz"
                    self.current_file.set_file(filename)
                for i in range(self.input_attachment.count()):
                    self.current_file.copy(self.input_attachment.item(i).text())
                if(self.prescription.prescriber.get_json()!=self.prescriber.get_json()):
                    if(QMessageBox.StandardButton.Yes==QMessageBox.question(self,"Change Prescriber", "Original Prescriber: "+self.prescription.prescriber.name+"\nCurrent Prescriber: "+self.prescriber.name+"\nReplace original with current?")):
                        self.prescription.prescriber=copy.deepcopy(self.prescriber)
                self.prescription.write_to(os.path.join(self.current_file.directory.name, "prescription.json"))
                if change_template:
                    config["template"]=os.path.join(config["template_directory"], template)
                self.current_file.save(change_template=change_template)
                self.unchanged_state=False
                self.load_interface_from_instance()
                self.save_state=md5(self.prescription.get_json().encode()).hexdigest()
            except Exception as e:
                QMessageBox.warning(self,"Save failed", "Failed to save file.")
                logging.exception(e)

    def cmd_save_as(self):
        suggest=self.prescription.id if(self.prescription.id) else self.prescription.name
        suggest=os.path.abspath(os.path.join(config["document_directory"], suggest)+".mpaz")
        filename=QFileDialog.getSaveFileName(self, "Save File", suggest, "Prescriptions (*.mpaz);; All Files (*)")[0]
        if(len(filename)>0):
            if not filename.endswith(".mpaz"):
                filename=filename+".mpaz"
            self.current_file.set_file(filename)
            Path(self.current_file.file).touch()
            self.cmd_save(save_as=True)

    def cmd_refresh(self):
        self.refresh()

    def cmd_quit(self):
        if(self.confirm_close()):
            sys.exit()

    def cmd_unrender(self):
        self.update_instance()
        self.unrenderbox.show(self.prescription).exec()

    def cmd_render(self):
        self.update_instance()
        if(self.save_state==md5(self.prescription.get_json().encode()).hexdigest()):
            try:
                target=self.renderer.render(self.current_file.directory.name)
                if target is not None:
                    self.signal_view.emit(target)
                    self.renderbox.showMaximized()
                else:
                    QMessageBox.critical(self, "Render failed", "Presciption rendering failed. Please check if prescription file or template is corrupted.")
                    logging.error("Prescription rendering failed.")
            except FileNotFoundError as e:
                logging.warning(e)
                QMessageBox.information(self, "Save first", "Please save the file before rendering.")
        else:
           QMessageBox.information(self, "Save first", "Please save the file before rendering.")

    def cmd_sign(self):
        self.update_instance()
        if(self.save_state==md5(self.prescription.get_json().encode()).hexdigest()):
            ok=True #password, ok=QInputDialog.getText(self, "Enter password", "Private key password", QLineEdit.EchoMode.Password)
            if(ok):
                try:
                    try:
                        self.current_file.sign()
                        #self.current_file.sign(password)
                        self.cmd_save()
                    except FileNotFoundError as e:
                        logging.warning(e)
                        QMessageBox.information(self, "Save first", "Please save the file before signing.")
                    except TypeError as e:
                        logging.warning(e)
                        QMessageBox.information(self, "Configure", "Please add valid key and certificate to the config file.")
                    except EVPError as e:
                        logging.warning(e)
                        QMessageBox.information(self, "Check password", "Failed to load key. Please check if password is correct.")
                    except BIOError as e:
                        logging.warning(e)
                        QMessageBox.information(self, "Not found", "Certifcate and/or key not found.")
                    except SMIME_Error as e:
                        logging.warning(e)
                        QMessageBox.information(self, "Failed to load", "Failed to sign. Please check if certificate and key match.")
                    except Exception as e:
                        logging.exception(e)
                        QMessageBox.information(self, "Failed", "Failed to sign.")
                except Exception as e:
                    logging.exception(e)
        else:
           QMessageBox.information(self, "Save first", "Please save the file before signing.")

    def cmd_unsign(self):
        self.current_file.delete_sign()
        self.cmd_save()
        self.refresh()

    def cmd_verify(self):
        try:
            result=self.current_file.verify()
            if result is False:
                QMessageBox.critical(self, "Verification failed", "Signature is invalid.")
            elif result is None:
                QMessageBox.warning(self, "No Siganture", "No signature was found.")
            else:
                logging.info(result)
                QMessageBox.information(self, "Valid signature", "Valid signature found with the following information:\n"+result)
        except FileNotFoundError as e:
            logging.warning(e)
            QMessageBox.warning(self, "No Siganture", "No signature was found.")
        except Exception as e:
            logging.exception(e)
            QMessageBox.warning(self, "Failed", "Failed to verify.")

    def cmd_index(self):
        self.index.show()

    def cmd_configuration(self):
        self.editConfiguration.exec()

    def cmd_prescriber(self):
        try:
            self.selectPrescriber.load()
            self.selectPrescriber.exec()
        except FileNotFoundError as e:
            logging.warning(e)

    def cmd_preset(self):
        self.editPreset.show()

    def cmd_installer(self):
        self.installer.show()

    def cmd_about(self):
        year=datetime.datetime.now().year
        if(year>2023):
            copy="2023"+"-"+str(year)
        else:
            copy="2023"
        txt="<h1>MedScript</h1>"
        txt=txt+"<p>Version "+info["version"]+"</p>"
        txt=txt+"<p>The Prescription Writing Software</p>"
        txt=txt+"<p><a href='"+info["url"]+"'>Website</a></p>"
        txt=txt+"<p>Copyright © "+copy+" Dr. Agnibho Mondal</p>"
        QMessageBox.about(self, "MedScript", txt)

    def cmd_help(self):
        self.viewbox.md(os.path.join(real_dir, "README"))
        self.viewbox.show()

    def cmd_update(self, silent=False):
        try:
            logging.info("Current version "+info["version"])
            with request.urlopen(info["url"]+"/info.json") as response:
                latest=json.loads(response.read().decode())
            logging.info("Latest version "+latest["version"])
            if(version.parse(info["version"]) < version.parse(latest["version"])):
                self.signal_update.emit("New version <strong>"+latest["version"]+"</strong> available.<br>Visit <a href='"+latest["url"]+"'>"+latest["url"]+"</a> to get the latest version.")
            elif(not silent):
                self.signal_update.emit("No update available. You are using version "+info["version"]+".")
        except Exception as e:
            self.signal_update.emit("Failed to check available update.")
            logging.warning(e)

    def show_update(self, message):
        QMessageBox.information(self, "Check update", message)

    def insert_preset_note(self):
        try:
            self.input_note.insertPlainText(self.preset_note.data[self.input_note_preset.currentText()])
        except KeyError:
            self.input_note.insertPlainText(self.input_note_preset.currentText())
        finally:
            self.input_note_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_note.insertPlainText("\n")

    def insert_preset_report(self):
        try:
            self.input_report.insertPlainText(self.preset_report.data[self.input_report_preset.currentText()])
        except KeyError:
            self.input_report.insertPlainText(self.input_report_preset.currentText())
        finally:
            self.input_report_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_report.insertPlainText("\n")

    def insert_preset_advice(self):
        try:
            self.input_advice.insertPlainText(self.preset_advice.data[self.input_advice_preset.currentText()])
        except KeyError:
            self.input_advice.insertPlainText(self.input_advice_preset.currentText())
        finally:
            self.input_advice_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_advice.insertPlainText("\n")

    def insert_preset_investigation(self):
        try:
            self.input_investigation.insertPlainText(self.preset_investigation.data[self.input_investigation_preset.currentText()])
        except KeyError:
            self.input_investigation.insertPlainText(self.input_investigation_preset.currentText())
        finally:
            self.input_investigation_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_investigation.insertPlainText("\n")

    def insert_preset_medication(self):
        try:
            self.input_medication.insertPlainText(self.preset_medication.data[self.input_medication_preset.currentText()])
        except KeyError:
            self.input_medication.insertPlainText(self.input_medication_preset.currentText())
        finally:
            self.input_medication_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_medication.insertPlainText("\n")

    def insert_preset_additional(self):
        try:
            self.input_additional.insertPlainText(self.preset_additional.data[self.input_additional_preset.currentText()])
        except KeyError:
            self.input_additional.insertPlainText(self.input_additional_preset.currentText())
        finally:
            self.input_additional_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_additional.insertPlainText("\n")

    def insert_preset_certificate(self):
        try:
            self.input_certificate.insertPlainText(self.preset_certificate.data[self.input_certificate_preset.currentText()])
        except KeyError:
            self.input_certificate.insertPlainText(self.input_certificate_preset.currentText())
        finally:
            self.input_certificate_preset.setCurrentIndex(-1)
            if config["preset_newline"]:
                self.input_certificate.insertPlainText("\n")

    def load_interface(self, file="", date=None, id="", pid="", name="", dob="", age="", sex="", address="", contact="", extra="", mode="", daw="", diagnosis="", note="", report="", advice="", investigation="", medication="", additional="", certificate="", custom=None):
        try:
            file_msg=self.current_file.file if self.current_file.file else "New file"
            sign_msg="(signed)" if config["smime"] and self.current_file.is_signed() else ""
            self.statusbar.showMessage(file_msg+" "+sign_msg)
            if date is None:
                d=QDateTime.currentDateTime()
            else:
                try:
                    pdate=dateutil.parser.parse(date)
                    d=QDateTime.fromString(pdate.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
                except Exception as e:
                    QMessageBox.warning(self,"Failed to load", str(e))
                    logging.exception(e)
            self.input_date.setDateTime(d)
            self.input_id.setText(id)
            self.input_pid.setText(pid)
            self.input_name.setText(name)
            try:
                pdate=dateutil.parser.parse(dob)
                d=QDate.fromString(pdate.strftime("%Y-%m-%d"), "yyyy-MM-dd")
                self.input_dob.setDate(d)
            except Exception as e:
                pass
            self.input_age.setText(age)
            if(age):
                self.btnAge.click()
            else:
                self.btnDob.click()
            self.input_sex.setCurrentText(sex)
            self.input_address.setText(address)
            self.input_contact.setText(contact)
            self.input_extra.setText(extra)
            self.input_mode.setCurrentText(mode)
            self.input_daw.setChecked(bool(daw))
            self.input_diagnosis.setText(diagnosis)
            self.input_note.setText(note)
            self.input_report.setText(report)
            self.input_advice.setText(advice)
            self.input_investigation.setText(investigation)
            self.input_medication.setText(medication)
            self.input_additional.setText(additional)
            self.input_certificate.setText(certificate)
            if(config["enable_form"] and custom is not None):
                self.input_custom.setData(custom)
            self.label_prescriber.setText(self.prescriber.name)
        except Exception as e:
            QMessageBox.warning(self,"Failed to load", "Failed to load the data into the application.")
            logging.exception(e)

    def load_interface_from_instance(self):
        if(self.current_file.has_template()):
            if(self.input_template.findText("<unchanged>")==-1):
                self.input_template.addItem("<unchanged>")
            self.input_template.setCurrentText("<unchanged>")
        else:
            self.input_template.removeItem(self.input_template.findText("<unchanged>"))
        self.load_interface(
                file=self.prescription.file,
                date=self.prescription.date,
                id=self.prescription.id,
                pid=self.prescription.pid,
                name=self.prescription.name,
                dob=self.prescription.dob,
                age=self.prescription.age,
                sex=self.prescription.sex,
                address=self.prescription.address,
                contact=self.prescription.contact,
                extra=self.prescription.extra,
                mode=self.prescription.mode,
                daw=self.prescription.daw,
                diagnosis=self.prescription.diagnosis,
                note=self.prescription.note,
                report=self.prescription.report,
                advice=self.prescription.advice,
                investigation=self.prescription.investigation,
                medication=self.prescription.medication,
                additional=self.prescription.additional,
                certificate=self.prescription.certificate,
                custom=self.prescription.custom
                )

    def update_instance(self):
        try:
            self.prescription.set_data(
                    date=self.input_date.dateTime().toString("yyyy-MM-dd hh:mm:ss"),
                    id=self.input_id.text(),
                    pid=self.input_pid.text(),
                    name=self.input_name.text(),
                    dob=self.input_dob.text(),
                    age=self.input_age.text(),
                    sex=self.input_sex.currentText(),
                    address=self.input_address.text(),
                    contact=self.input_contact.text(),
                    extra=self.input_extra.toPlainText(),
                    mode=self.input_mode.currentText(),
                    daw=self.input_daw.isChecked(),
                    diagnosis=self.input_diagnosis.text(),
                    note=self.input_note.toPlainText(),
                    report=self.input_report.toPlainText(),
                    advice=self.input_advice.toPlainText(),
                    investigation=self.input_investigation.toPlainText(),
                    medication=self.input_medication.toPlainText(),
                    additional=self.input_additional.toPlainText(),
                    certificate=self.input_certificate.toPlainText(),
                    custom=self.input_custom.getData()
                    )
        except Exception as e:
            QMessageBox.critical(self,"Failed", "Critical failure happned. Please check console for more info.")
            logging.error(e)

    def new_doc(self):
        self.current_file.reset()
        self.prescription.set_data()
        self.input_attachment.clear()
        self.load_interface()
        self.update_instance()
        self.plugin.new(self.prescription)
        self.load_interface_from_instance()
        if(config["age_default"]):
            self.btnAge.click()
            self.update_instance()
        self.save_state=md5(self.prescription.get_json().encode()).hexdigest()

    def change_prescriber(self, file):
        self.prescription.reload_prescriber(file)
        self.prescriber.read_from(file)
        self.refresh()

    def edit_prescriber(self, file=None):
        self.editPrescriber.load(file)
        self.editPrescriber.exec()

    def refresh(self):
        self.update_instance()
        self.plugin.refresh(self.prescription)
        self.load_interface_from_instance()

    def add_attachment(self):
        try:
            new=QFileDialog.getOpenFileName(self, "Open File", config["document_directory"], "PDF (*.pdf);; Images (*.jpg, *.jpeg, *.png, *.gif);; All Files (*)")[0]
            if new:
                self.input_attachment.addItem(new)
        except Exception as e:
            QMessageBox.warning(self,"Attach failed", "Failed to attach file.")
            logging.exception(e)

    def remove_attachment(self):
        index=self.input_attachment.currentRow()
        if(index>=0):
            self.current_file.delete_attachment(self.input_attachment.item(index).text())
            self.input_attachment.takeItem(index)
        else:
            QMessageBox.warning(self, "Select item", "Please select an attachment to remove.")

    def save_attachment(self):
        try:
            shutil.copyfile(self.input_attachment.currentItem().text(), QFileDialog.getSaveFileName(self, "Save Attachment", os.path.join(config["document_directory"], os.path.basename(self.input_attachment.currentItem().text())))[0])
        except Exception as e:
            logging.exception(e)

    def load_attachment(self, attachments):
        for attach in attachments:
            self.input_attachment.addItem(attach)

    def toggleDobAge(self, active):
        if active=="age":
            self.input_dob.setDate(QDate(0,0,0))
            self.input_dob.setDisplayFormat("yy")
            self.input_dob.setEnabled(False)
            self.input_age.setEnabled(True)
        elif active=="dob":
            self.input_dob.setDisplayFormat("MMMM dd, yyyy")
            self.input_dob.setEnabled(True)
            self.input_age.setText("")
            self.input_age.setEnabled(False)

    def load_presets(self):
        self.preset_note=Preset("note")
        self.preset_report=Preset("report")
        self.preset_advice=Preset("advice")
        self.preset_investigation=Preset("investigation")
        self.preset_medication=Preset("medication", text_as_key=True)
        self.preset_additional=Preset("additional")
        self.preset_certificate=Preset("certificate")

    def reload_presets(self):
        self.load_presets()
        self.input_note_preset.addItems(self.preset_note.data.keys())
        self.input_report_preset.addItems(self.preset_note.data.keys())
        self.input_advice_preset.addItems(self.preset_note.data.keys())
        self.input_investigation_preset.addItems(self.preset_note.data.keys())
        self.input_medication_preset.addItems(self.preset_note.data.keys())
        self.input_additional_preset.addItems(self.preset_note.data.keys())
        self.input_certificate_preset.addItems(self.preset_note.data.keys())

    def confirm_close(self):
        self.update_instance()
        flag=(self.save_state==md5(self.prescription.get_json().encode()).hexdigest() or QMessageBox.StandardButton.Yes==QMessageBox.question(self,"Confirm action", "Unsaved changes may be lost. Continue?"))
        return flag

    def closeEvent(self, event):
        if(self.confirm_close()):
            event.accept()
        else:
            event.ignore()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MedScript")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon(os.path.join(config["resource"], "icon_medscript.ico")))

        icon_index=QIcon(os.path.join(config["resource"], "icon_index.svg"))
        icon_open=QIcon(os.path.join(config["resource"], "icon_open.svg"))
        icon_save=QIcon(os.path.join(config["resource"], "icon_save.svg"))
        icon_render=QIcon(os.path.join(config["resource"], "icon_render.svg"))
        icon_refresh=QIcon(os.path.join(config["resource"], "icon_refresh.svg"))
        icon_view=QIcon(os.path.join(config["resource"], "icon_view.svg"))

        self.load_presets()

        action_new=QAction("New File", self)
        action_new.setShortcut("Ctrl+N")
        action_new.triggered.connect(self.cmd_new)
        action_open=QAction("Open File", self)
        action_open2=QAction(icon_open, "Open", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.cmd_open)
        action_open2.triggered.connect(self.cmd_open)
        action_save=QAction("Save File", self)
        action_save2=QAction(icon_save, "Save", self)
        action_save.setShortcut("Ctrl+S")
        action_save.triggered.connect(self.cmd_save)
        action_save2.triggered.connect(self.cmd_save)
        action_save_as=QAction("Save As", self)
        action_save_as.setShortcut("Ctrl+Shift+S")
        action_save_as.triggered.connect(self.cmd_save_as)
        action_refresh=QAction("Refresh Interface", self)
        action_refresh.setShortcut("F5")
        action_refresh2=QAction(icon_refresh, "Refresh", self)
        action_refresh.triggered.connect(self.cmd_refresh)
        action_refresh2.triggered.connect(self.cmd_refresh)
        action_quit=QAction("Quit MedScript", self)
        action_quit.setShortcut("Ctrl+Q")
        action_quit.triggered.connect(self.cmd_quit)
        action_render=QAction("Render Prescription", self)
        action_render.setShortcut("Ctrl+R")
        action_render2=QAction(icon_render, "Render", self)
        action_render.triggered.connect(self.cmd_render)
        action_render2.triggered.connect(self.cmd_render)
        action_unrender=QAction("Quick Display", self)
        action_unrender.setShortcut("Ctrl+D")
        action_unrender2=QAction(icon_view, "Display", self)
        action_unrender.triggered.connect(self.cmd_unrender)
        action_unrender2.triggered.connect(self.cmd_unrender)
        action_sign=QAction("Sign Prescription", self)
        action_sign.triggered.connect(self.cmd_sign)
        action_unsign=QAction("Delete Signature", self)
        action_unsign.triggered.connect(self.cmd_unsign)
        action_verify=QAction("Verify Signature", self)
        action_verify.triggered.connect(self.cmd_verify)
        action_configuration=QAction("Edit Configuration", self)
        action_configuration.triggered.connect(self.cmd_configuration)
        action_preset=QAction("Edit Presets", self)
        action_preset.triggered.connect(self.cmd_preset)
        action_prescriber=QAction("Select Prescriber", self)
        action_prescriber.triggered.connect(self.cmd_prescriber)
        action_installer=QAction("Package Installer", self)
        action_installer.triggered.connect(self.cmd_installer)
        action_index=QAction("Show Index", self)
        action_index.triggered.connect(self.cmd_index)
        action_index.setShortcut("Ctrl+I")
        action_index2=QAction(icon_index, "Index", self)
        action_index2.triggered.connect(self.cmd_index)
        action_update=QAction("Check Update", self)
        action_update.triggered.connect(self.cmd_update)
        action_about=QAction("About MedScript", self)
        action_about.triggered.connect(self.cmd_about)
        action_help=QAction("Show Help", self)
        action_help.setShortcut("F1")
        action_help.triggered.connect(self.cmd_help)

        menubar=self.menuBar()
        menu_file=menubar.addMenu("File")
        menu_file.addAction(action_index)
        menu_file.addAction(action_new)
        menu_file.addAction(action_open)
        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addAction(action_quit)
        menu_prepare=menubar.addMenu("Process")
        menu_prepare.addAction(action_unrender)
        menu_prepare.addAction(action_render)
        menu_prepare.addAction(action_refresh)
        if(config["smime"]):
            menu_prepare.addAction(action_sign)
            menu_prepare.addAction(action_unsign)
            menu_prepare.addAction(action_verify)
        menu_settings=menubar.addMenu("Settings")
        menu_settings.addAction(action_configuration)
        menu_settings.addAction(action_preset)
        menu_settings.addAction(action_prescriber)
        menu_settings.addAction(action_installer)

        if(config["enable_plugin"]):
            action_plugin=[]
            try:
                for i in self.plugin.commands():
                    action_plugin.append(QAction(i[1], self))
                    action_plugin[-1].triggered.connect(self.update_instance)
                    action_plugin[-1].triggered.connect(partial(self.plugin.run, i[0], self.prescription))
                    action_plugin[-1].triggered.connect(self.load_interface_from_instance)
            except Exception as e:
                logging.exception(e)
            menu_plugin=menubar.addMenu("Plugin")
            for i in action_plugin:
                menu_plugin.addAction(i)

        menu_help=menubar.addMenu("Help")
        menu_help.addAction(action_update)
        menu_help.addAction(action_about)
        menu_help.addAction(action_help)

        toolbar=QToolBar("Main Toolbar", floatable=False, movable=False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.addAction(action_index2)
        toolbar.addAction(action_open2)
        toolbar.addAction(action_save2)
        toolbar.addAction(action_refresh2)
        toolbar.addAction(action_unrender2)
        toolbar.addAction(action_render2)
        toolbar.addSeparator()
        label_template=QLabel("Template:")
        toolbar.addWidget(label_template)
        self.input_template=QComboBox(self)
        self.input_template.setMinimumWidth(200)
        templates=os.listdir(config["template_directory"])
        try:
            templates.remove(os.path.basename(config["template"]))
            templates.insert(0, os.path.basename(config["template"]))
        except Exception as e:
            logging.exception(e)
        self.input_template.addItems(templates)
        toolbar.addWidget(self.input_template)
        spacer=QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        self.label_prescriber=QLabel(self)
        toolbar.addWidget(self.label_prescriber)
        self.addToolBar(toolbar)

        tab_info=QWidget(self)
        layout_info=QFormLayout(tab_info)
        layout_info2=QHBoxLayout()
        self.input_date=QDateTimeEdit(self)
        self.input_date.setDisplayFormat("MMMM dd, yyyy hh:mm a")
        self.input_date.setCalendarPopup(True)
        self.input_date.setCalendarWidget(QCalendarWidget())
        layout_info.addRow("Date", self.input_date)
        self.input_id=QLineEdit(self)
        layout_info.addRow("Prescription ID", self.input_id)
        self.input_pid=QLineEdit(self)
        layout_info.addRow("Patient ID", self.input_pid)
        self.input_name=QLineEdit(self)
        layout_info.addRow("Name", self.input_name)

        self.input_dob=QDateEdit(self)
        self.input_dob.setCalendarPopup(True)
        self.input_dob.setCalendarWidget(QCalendarWidget())
        self.input_dob.setEnabled(False)
        layout_dobAge=QHBoxLayout()
        dobAge=QButtonGroup()
        self.btnDob=QRadioButton("Date of Birth")
        self.btnAge=QRadioButton("Age")
        dobAge.addButton(self.btnDob)
        dobAge.addButton(self.btnAge)
        layout_dobAge.addWidget(self.btnDob)
        layout_dobAge.addWidget(self.btnAge)
        self.btnDob.clicked.connect(lambda: self.toggleDobAge("dob"))
        self.btnAge.clicked.connect(lambda: self.toggleDobAge("age"))
        layout_info.addRow("", layout_dobAge)
        layout_info.addRow("Date of Birth", self.input_dob)
        self.input_age=QLineEdit(self)
        layout_info.addRow("Age", self.input_age)
        self.input_sex=QComboBox(self)

        self.input_sex.addItems(["Male", "Female", "Other"])
        self.input_sex.setEditable(True)
        layout_info.addRow("Sex", self.input_sex)
        self.input_address=QLineEdit(self)
        layout_info.addRow("Address", self.input_address)
        self.input_contact=QLineEdit(self)
        layout_info.addRow("Contact", self.input_contact)
        self.input_diagnosis=QLineEdit(self)
        layout_info.addRow("Diagnosis", self.input_diagnosis)
        self.input_extra=QTextEdit(self)
        input_extra_preset_btn=QPushButton("Insert")
        layout_info.addRow("Extra", self.input_extra)
        self.input_mode=QComboBox(self)
        self.input_mode.addItems(["In-Person", "Tele-Consultation", "Other"])
        self.input_mode.setEditable(True)
        layout_info.addRow("Mode", self.input_mode)
        self.input_daw=QCheckBox("Dispense as written", self)
        layout_info.addRow("DAW", self.input_daw)

        tab_note=QWidget(self)
        layout_note=QVBoxLayout(tab_note)
        layout_note2=QHBoxLayout()
        label_note=QLabel("Clinical Notes")
        label_note.setProperty("class", "info_head")
        self.input_note_preset=QComboBox(self)
        self.input_note_preset.addItems(self.preset_note.data.keys())
        self.input_note_preset.setCurrentIndex(-1)
        self.input_note_preset.setEditable(True)
        self.input_note_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_note_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_note_preset.setPlaceholderText("Select a preset")
        input_note_preset_btn=QPushButton("Insert")
        input_note_preset_btn.clicked.connect(self.insert_preset_note)
        layout_note2.addWidget(self.input_note_preset, 5)
        layout_note2.addWidget(input_note_preset_btn, 1)
        self.input_note=QTextEdit(self)
        layout_note.addWidget(label_note)
        layout_note.addLayout(layout_note2)
        layout_note.addWidget(self.input_note)

        tab_report=QWidget(self)
        layout_report=QVBoxLayout(tab_report)
        layout_report2=QHBoxLayout()
        label_report=QLabel("Available Reports")
        label_report.setProperty("class", "info_head")
        self.input_report_preset=QComboBox(self)
        self.input_report_preset.addItems(self.preset_report.data.keys())
        self.input_report_preset.setCurrentIndex(-1)
        self.input_report_preset.setEditable(True)
        self.input_report_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_report_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_report_preset.setPlaceholderText("Select a preset")
        input_report_preset_btn=QPushButton("Insert")
        input_report_preset_btn.clicked.connect(self.insert_preset_report)
        layout_report2.addWidget(self.input_report_preset, 5)
        layout_report2.addWidget(input_report_preset_btn, 1)
        self.input_report=QTextEdit(self)
        layout_report.addWidget(label_report)
        layout_report.addLayout(layout_report2)
        layout_report.addWidget(self.input_report)

        tab_advice=QWidget(self)
        layout_advice=QVBoxLayout(tab_advice)
        layout_advice2=QHBoxLayout()
        label_advice=QLabel("Advice")
        label_advice.setProperty("class", "info_head")
        self.input_advice_preset=QComboBox(self)
        self.input_advice_preset.addItems(self.preset_advice.data.keys())
        self.input_advice_preset.setCurrentIndex(-1)
        self.input_advice_preset.setEditable(True)
        self.input_advice_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_advice_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_advice_preset.setPlaceholderText("Select a preset")
        input_advice_preset_btn=QPushButton("Insert")
        input_advice_preset_btn.clicked.connect(self.insert_preset_advice)
        layout_advice2.addWidget(self.input_advice_preset, 5)
        layout_advice2.addWidget(input_advice_preset_btn, 1)
        self.input_advice=QTextEdit(self)
        layout_advice.addWidget(label_advice)
        layout_advice.addLayout(layout_advice2)
        layout_advice.addWidget(self.input_advice)

        tab_investigation=QWidget(self)
        layout_investigation=QVBoxLayout(tab_investigation)
        layout_investigation2=QHBoxLayout()
        label_investigation=QLabel("Recommended Investigations")
        label_investigation.setProperty("class", "info_head")
        self.input_investigation_preset=QComboBox(self)
        self.input_investigation_preset.addItems(self.preset_investigation.data.keys())
        self.input_investigation_preset.setCurrentIndex(-1)
        self.input_investigation_preset.setEditable(True)
        self.input_investigation_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_investigation_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_investigation_preset.setPlaceholderText("Select a preset")
        input_investigation_preset_btn=QPushButton("Insert")
        input_investigation_preset_btn.clicked.connect(self.insert_preset_investigation)
        layout_investigation2.addWidget(self.input_investigation_preset, 5)
        layout_investigation2.addWidget(input_investigation_preset_btn, 1)
        self.input_investigation=QTextEdit(self)
        layout_investigation.addWidget(label_investigation)
        layout_investigation.addLayout(layout_investigation2)
        layout_investigation.addWidget(self.input_investigation)

        tab_medication=QWidget(self)
        layout_medication=QVBoxLayout(tab_medication)
        layout_medication2=QHBoxLayout()
        label_medication=QLabel("Medication Advice")
        label_medication.setProperty("class", "info_head")
        self.input_medication_preset=QComboBox(self)
        self.input_medication_preset.addItems(self.preset_medication.data.keys())
        self.input_medication_preset.setCurrentIndex(-1)
        self.input_medication_preset.setEditable(True)
        self.input_medication_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_medication_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_medication_preset.setPlaceholderText("Select a preset")
        input_medication_preset_btn=QPushButton("Insert")
        input_medication_preset_btn.clicked.connect(self.insert_preset_medication)
        layout_medication2.addWidget(self.input_medication_preset, 5)
        layout_medication2.addWidget(input_medication_preset_btn, 1)
        self.input_medication=QTextEdit(self)
        layout_medication.addWidget(label_medication)
        layout_medication.addLayout(layout_medication2)
        layout_medication.addWidget(self.input_medication)

        tab_additional=QWidget(self)
        layout_additional=QVBoxLayout(tab_additional)
        layout_additional2=QHBoxLayout()
        label_additional=QLabel("Additional Advice")
        label_additional.setProperty("class", "info_head")
        self.input_additional_preset=QComboBox(self)
        self.input_additional_preset.addItems(self.preset_additional.data.keys())
        self.input_additional_preset.setCurrentIndex(-1)
        self.input_additional_preset.setEditable(True)
        self.input_additional_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_additional_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_additional_preset.setPlaceholderText("Select a preset")
        input_additional_preset_btn=QPushButton("Insert")
        input_additional_preset_btn.clicked.connect(self.insert_preset_additional)
        layout_additional2.addWidget(self.input_additional_preset, 5)
        layout_additional2.addWidget(input_additional_preset_btn, 1)
        self.input_additional=QTextEdit(self)
        layout_additional.addWidget(label_additional)
        layout_additional.addLayout(layout_additional2)
        layout_additional.addWidget(self.input_additional)

        tab_certificate=QWidget(self)
        layout_certificate=QVBoxLayout(tab_certificate)
        layout_certificate2=QHBoxLayout()
        label_certificate=QLabel("Certificate")
        label_certificate.setProperty("class", "info_head")
        self.input_certificate_preset=QComboBox(self)
        self.input_certificate_preset.addItems(self.preset_certificate.data.keys())
        self.input_certificate_preset.setCurrentIndex(-1)
        self.input_certificate_preset.setEditable(True)
        self.input_certificate_preset.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_certificate_preset.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.input_certificate_preset.setPlaceholderText("Select a preset")
        input_certificate_preset_btn=QPushButton("Insert")
        input_certificate_preset_btn.clicked.connect(self.insert_preset_certificate)
        layout_certificate2.addWidget(self.input_certificate_preset, 5)
        layout_certificate2.addWidget(input_certificate_preset_btn, 1)
        self.input_certificate=QTextEdit(self)
        layout_certificate.addWidget(label_certificate)
        layout_certificate.addLayout(layout_certificate2)
        layout_certificate.addWidget(self.input_certificate)

        tab_attachment=QWidget(self)
        layout_attachment=QVBoxLayout(tab_attachment)
        layout_attachment2=QHBoxLayout()
        label_attachment=QLabel("Attached files")
        label_attachment.setProperty("class", "info_head")
        self.input_attachment=QListWidget(self)
        button_add=QPushButton("Add")
        button_add.clicked.connect(self.add_attachment)
        button_remove=QPushButton("Remove")
        button_remove.clicked.connect(self.remove_attachment)
        button_save=QPushButton("Save")
        button_save.clicked.connect(self.save_attachment)
        layout_attachment.addWidget(label_attachment)
        layout_attachment.addLayout(layout_attachment2)
        layout_attachment.addWidget(self.input_attachment)
        layout_attachment2.addWidget(button_add)
        layout_attachment2.addWidget(button_remove)
        layout_attachment2.addWidget(button_save)

        tab_custom=QWidget(self)
        layout_custom=QVBoxLayout(tab_custom)
        self.input_custom=CustomForm()
        layout_custom.addWidget(self.input_custom)

        tab=QTabWidget(self)
        tab.addTab(tab_info, "Patient")
        tab.addTab(tab_note, "Clinical")
        tab.addTab(tab_report, "Report")
        tab.addTab(tab_advice, "Advice")
        tab.addTab(tab_investigation, "Investigation")
        tab.addTab(tab_medication, "Medication")
        tab.addTab(tab_additional, "Additional")
        tab.addTab(tab_certificate, "Certificate")
        if(config["enable_form"]):
            tab.addTab(tab_custom, "Custom")
        else:
            tab_custom.hide()
        tab.addTab(tab_attachment, "Attachment")

        self.setCentralWidget(tab)

        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)

        self.renderbox=RenderBox()
        self.unrenderbox=UnrenderBox()
        self.signal_view.connect(self.renderbox.update)
        self.editConfiguration=EditConfiguration()
        self.editPrescriber=EditPrescriber()
        self.editPrescriber.signal_save.connect(self.change_prescriber)
        self.selectPrescriber=SelectPrescriber()
        self.selectPrescriber.signal_edit.connect(self.edit_prescriber)
        self.selectPrescriber.signal_select.connect(self.change_prescriber)
        self.viewbox=ViewBox()
        self.index=Index()
        self.editPreset=EditPreset()
        self.editPreset.presetEdited.connect(self.reload_presets)
        self.installer=Installer()
        self.index.signal_open.connect(self.cmd_open)
        self.index.signal_copy.connect(self.cmd_copy)
        self.plugin.update.connect(lambda: self.load_interface_from_instance())
        self.signal_update.connect(self.show_update)

        self.new_doc()
        if(config["filename"]):
            self.cmd_open(config["filename"])

        if(len(self.prescription.prescriber.name.strip())<1):
            self.edit_prescriber()

        if(config["check_update"]):
            threading.Thread(target=self.cmd_update, args=[True]).start()


        self.setWindowIcon(QIcon(os.path.join(config["resource"], "icon_medscript.ico")))
        self.showMaximized()
