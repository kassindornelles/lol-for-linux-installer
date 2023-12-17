#!/usr/bin/env python3
import sys
import os
import signal
import psutil
import logging
import json
import urllib.request
import shutil
import zipfile
import tarfile
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSlider
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, QObject, QUrl, pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtGui import QDesktopServices

module_folder = "/usr/share/lol-for-linux-installer"
sys.path.append(module_folder)

import leagueinstaller_code
import vulkan_layers


class GuiLogHandler(QObject, logging.Handler):
    new_record = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)
        super(logging.Handler).__init__()
        formatter = Formatter("%(levelname)s: %(message)s", "%d/%m/%Y %H:%M:%S")
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        self.new_record.emit(msg)


class Formatter(logging.Formatter):
    def formatException(self, ei):
        result = super(Formatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(Formatter, self).format(record)
        if record.exc_text:
            s = s.replace("\n", "")
        return s


class Installer(QMainWindow):
    def __init__(self):
        super(Installer, self).__init__()
        try:
            loadUi("installer.ui", self)
        except:
            loadUi("/usr/share/lol-for-linux-installer/installer.ui", self)
        self.currentversion = "2.6.4"
        self.aboutversiontext = f"Version: {self.currentversion}"
        self.versionlabelabout.setText(self.aboutversiontext)
        self.versionlabelabout.setAlignment(QtCore.Qt.AlignCenter)
        self.slider_value_changed = False
        self.game_installed_folder = None
        self.game_rpc_folder = None
        self.gamemode_value = None
        self.richpresence_value = None
        self.skiplauncher_value = None
        self.setWindowTitle("lol-for-linux-installer")
        self.install_button.clicked.connect(self.installer_code)
        self.cancelButton.clicked.connect(self.cancel_installation)
        self.install_button.setEnabled(True)
        self.githubButton.clicked.connect(self.open_github)
        self.githubButton2.clicked.connect(self.open_github)
        self.cancelButton.setEnabled(False)
        self.uninstallLeaguebutton.clicked.connect(self.uninstall_game)
        self.applyButton.setEnabled(False)
        self.applyButton.clicked.connect(self.applynewsettings)
        self.tabWidget.setCurrentIndex(0)
        self.Usedriprime.stateChanged.connect(self.toggleapplybutton)
        self.Usenvidiahybrid.stateChanged.connect(self.toggleapplybutton)
        self.obsvkcapturecheck.stateChanged.connect(self.toggleapplybutton)
        self.Richpresence.clicked.connect(self.toggleapplybutton)
        self.Usegamemode.clicked.connect(self.toggleapplybutton)
        self.nextWelcome.clicked.connect(self.regionWidget)
        self.nextRegion.clicked.connect(self.optionsWidget)
        self.launchLeagueinstalled.clicked.connect(self.launchleague)
        self.vkbasaltcheckbox.clicked.connect(self.toggleapplybutton)
        self.donatebutton.clicked.connect(self.donatebuttonaction)
        self.skiplaunchercheck.clicked.connect(self.toggleapplybutton)
        self.read_installed_folder()
        if self.winebuildcombobox.currentText != "...":
            self.winebuildcombobox.currentIndexChanged.connect(self.toggleapplybutton)

        if self.rendererCombobox.currentText != "...":
            self.rendererCombobox.currentIndexChanged.connect(self.toggleapplybutton)

    def read_installed_folder(self):
        json_file_path = os.path.expanduser("~/.config/league_install_path.json")
        try:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)
                self.game_installed_folder = data["game_main_dir"]
                os.chdir(self.game_installed_folder)
                wine_build_dir = "wine/wine-build"
                with open("env_vars.json", "r") as f:
                    env_vars = json.load(f)
                self.load_env_vars(env_vars, self)
                self.download_winebuild_json()
                self.game_rpc_folder = os.path.join(
                    self.game_installed_folder, "league-rpc-linux-main"
                )
                if (
                    os.path.isdir(self.game_rpc_folder) == False
                    and self.Richpresence.isChecked()
                ):
                    self.Richpresence.setChecked(False)
        except FileNotFoundError:
            self.stackedWidget.setCurrentWidget(self.welcome)

        if shutil.which("gamemoderun") is not None:
            try:
                self.Usegamemode.setEnabled(True)
            except subprocess.CalledProcessError:
                print("Error while getting Gamemode info.")
        else:
            self.Usegamemode.setChecked(False)
            self.Usegamemode.setEnabled(False)
        if "VK_LAYER_VKBASALT_post_processing" not in vulkan_layers.LAYERS:
            self.vkbasaltcheckbox.setChecked(False)
            self.vkbasaltcheckbox.setEnabled(False)
            self.vkbasaltslider.setEnabled(False)
        else:
            self.enablevkbasalt_settings()
        if "VK_LAYER_MANGOHUD_overlay" not in vulkan_layers.LAYERS:
            self.Usemangohud.setChecked(False)
            self.Usemangohud.setEnabled(False)
        if "VK_LAYER_OBS_vkcapture_64" not in vulkan_layers.LAYERS:
            self.obsvkcapturecheck.setChecked(False)
            self.obsvkcapturecheck.setEnabled(False)

    def enablevkbasalt_settings(self):
        if self.vkbasaltcheckbox.isChecked():
            self.vkbasaltslider.setEnabled(True)
            self.vkbasaltslider.valueChanged.connect(self.vkbasaltslidercontrol)
        else:
            self.vkbasaltslider.setEnabled(False)
            self.vkbasaltslider.valueChanged.connect(self.vkbasaltslidercontrol)

    def load_env_vars(self, env_vars, installer):
        game_launcher_options = env_vars.get("game_launcher_options", {})

        if all(
            key in game_launcher_options
            for key in [
                "NV_PRIME_RENDER_OFFLOAD",
                "__GLX_VENDOR_LIBRARY_NAME",
                "VK_ICD_FILENAMES",
                "VK_LAYER_NV_optimus",
            ]
        ):
            self.Usenvidiahybrid.setChecked(True)
        else:
            self.Usenvidiahybrid.setChecked(False)

        if all(key in game_launcher_options for key in ["DRI_PRIME"]):
            self.Usedriprime.setChecked(True)
        else:
            self.Usedriprime.setChecked(False)

        if all(key in game_launcher_options for key in ["MANGOHUD"]):
            self.Usemangohud.setChecked(True)
        else:
            self.Usemangohud.setChecked(False)
        self.Usemangohud.stateChanged.connect(self.toggleapplybutton)

        if all(key in game_launcher_options for key in ["OBS_VKCAPTURE"]):
            self.obsvkcapturecheck.setChecked(True)
        else:
            self.obsvkcapturecheck.setChecked(False)

        if all(key in game_launcher_options for key in ["ENABLE_VKBASALT"]):
            config_file = game_launcher_options.get("VKBASALT_CONFIG_FILE")
            casSharpness = self.read_cas_sharpness_from_config(config_file)
            slider_value = self.convert_cas_sharpness_to_slider_value(casSharpness)
            self.vkbasaltcheckbox.setChecked(True)
            self.vkbasaltslider.setValue(slider_value)

        game_settings = env_vars.get("game_settings", {})
        if game_settings.get("Gamemode") == "1":
            self.Usegamemode.setChecked(True)
        else:
            self.Usegamemode.setChecked(False)

        if game_settings.get("Richpresence") == "1":
            self.Richpresence.setChecked(True)
        else:
            self.Richpresence.setChecked(False)
        if game_settings.get("Skiplauncher") == "0":
            self.skiplaunchercheck.setChecked(False)
            self.stackedWidget.setCurrentWidget(self.gamemanager)
        else:
            self.skiplaunchercheck.setChecked(True)
            self.launchleague(installer)

    def read_cas_sharpness_from_config(self, config_file):
        casSharpness = 0.5  # Default value if the file or key doesn't exist

        try:
            with open(config_file, "r") as file:
                for line in file:
                    if line.startswith("casSharpness"):
                        casSharpness = float(line.split("=")[1].strip())
                        break
        except (FileNotFoundError, IOError):
            pass

        return casSharpness

    def convert_cas_sharpness_to_slider_value(self, casSharpness):
        slider_value = int((casSharpness - 0.1) / 0.9 * 9) + 1
        self.sharpeningtext_level.setText(str(slider_value))
        return slider_value

    def toggleapplybutton(self):
        self.vkbasalt_slider_enablement()
        self.applyButton.setEnabled(True)

    def vkbasalt_slider_enablement(self):
        if self.vkbasaltcheckbox.isChecked():
            self.vkbasaltslider.setEnabled(True)
        else:
            self.vkbasaltslider.setEnabled(False)

    def donatebuttonaction(self):
        urlgit = QUrl("https://liberapay.com/kassindornelles/donate")
        QDesktopServices.openUrl(urlgit)

    def vkbasaltslidercontrol(self, value):
        self.sharpeningtext_level.setText(str(value))
        if not self.slider_value_changed:
            self.toggleapplybutton()
        self.slider_value_changed = True

    def applynewsettings(self):
        os.chdir(self.game_installed_folder)
        current_renderer = self.rendererCombobox.currentText()

        with open("env_vars.json", "r") as f:
            env_vars = json.load(f)

        if self.Usedriprime.isChecked():
            env_vars["game_launcher_options"]["DRI_PRIME"] = "1"
        else:
            env_vars["game_launcher_options"].pop("DRI_PRIME", None)

        if self.Richpresence.isChecked() and not os.path.isdir(self.game_rpc_folder):
            self.install_richpresence_code(self.game_installed_folder)

        elif not self.Richpresence.isChecked() and os.path.isdir(self.game_rpc_folder):
            shutil.rmtree(self.game_rpc_folder)

        if self.Usenvidiahybrid.isChecked():
            new_vars = {
                "NV_PRIME_RENDER_OFFLOAD": "1",
                "__GLX_VENDOR_LIBRARY_NAME": "nvidia",
                "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/nvidia_icd.json",
                "VK_LAYER_NV_optimus": "NVIDIA_only",
            }
            env_vars["game_launcher_options"].update(new_vars)
        else:
            vars_to_remove = [
                "NV_PRIME_RENDER_OFFLOAD",
                "__GLX_VENDOR_LIBRARY_NAME",
                "VK_ICD_FILENAMES",
                "VK_LAYER_NV_optimus",
            ]
            for var_name in vars_to_remove:
                env_vars["game_launcher_options"].pop(var_name, None)

        if self.Usemangohud.isChecked():
            env_vars["game_launcher_options"]["MANGOHUD"] = "1"
        else:
            env_vars["game_launcher_options"].pop("MANGOHUD", None)

        if self.obsvkcapturecheck.isChecked():
            env_vars["game_launcher_options"]["OBS_VKCAPTURE"] = "1"
        else:
            env_vars["game_launcher_options"].pop("OBS_VKCAPTURE", None)

        if self.vkbasaltcheckbox.isChecked():
            env_vars["game_launcher_options"]["ENABLE_VKBASALT"] = "1"
            env_vars["game_launcher_options"]["VKBASALT_CONFIG_FILE"] = "vkBasalt.conf"
            filename = "vkBasalt.conf"
            slider_value = self.vkbasaltslider.value()
            casSharpness = (slider_value - 1) / 9.0 * 0.9 + 0.1
            filepath = os.path.join(self.game_installed_folder, filename)
            with open(filename, "w") as file:
                file.write("effects = cas\n")
                file.write("casSharpness = {}\n".format(casSharpness))
                file.write("toggleKey = Home\n")
                file.write("enableOnLaunch = True\n")
            env_vars["game_launcher_options"]["VKBASALT_CONFIG_FILE"] = filepath
        else:
            env_vars["game_launcher_options"].pop("ENABLE_VKBASALT", None)
            env_vars["game_launcher_options"].pop("VKBASALT_CONFIG_FILE", None)

        env_vars["game_settings"]["Gamemode"] = (
            "1" if self.Usegamemode.isChecked() else "0"
        )
        self.gamemode_value = int(env_vars["game_settings"]["Gamemode"])
        env_vars["game_settings"]["Richpresence"] = (
            "1" if self.Richpresence.isChecked() else "0"
        )

        self.richpresence_value = int(env_vars["game_settings"]["Richpresence"])
        env_vars["game_settings"]["Skiplauncher"] = (
            "1" if self.skiplaunchercheck.isChecked() else "0"
        )
        self.skiplauncher_value = int(env_vars["game_settings"]["Skiplauncher"])

        with open("env_vars.json", "w") as f:
            json.dump(env_vars, f, indent=4)

        if self.winebuildcombobox.currentText != "...":
            selected_item = self.winebuildcombobox.currentText()

            json_filename = os.path.join(
                self.game_installed_folder, "wine_builds_available.json"
            )
            with open(json_filename, "r") as file:
                data = json.load(file)
                url = data["winebuilds"].get(selected_item)

            if url:
                file_name = os.path.basename(url)
                file_path = os.path.join(self.game_installed_folder, file_name)
                urllib.request.urlretrieve(url, file_path)

                wine_build_dir = "wine/wine-build"
                self.extract_and_replace_wine_build(
                    file_path, wine_build_dir, wine_build_dir
                )
            self.winebuildcombobox.setCurrentIndex(0)

        if "DXVK" in current_renderer:
            dxvk_version = current_renderer.replace("DXVK ", "")
            self.install_dxvk_code(dxvk_version, self.game_installed_folder)
            self.rendererCombobox.setCurrentIndex(0)

        self.applyButton.setEnabled(False)

    def download_winebuild_json(self):
        json_url = "https://raw.githubusercontent.com/kassindornelles/lol-for-linux-installer-wine-builds/main/wine_builds_available.json"
        json_filename = os.path.join(
            self.game_installed_folder, "wine_builds_available.json"
        )

        if os.path.exists(json_filename):
            os.remove(json_filename)

        with urllib.request.urlopen(json_url) as response, open(
            json_filename, "wb"
        ) as json_file:
            json_file.write(response.read())

        with open(json_filename, "r") as file:
            data = json.load(file)
            self.winebuildcombobox.addItems(data["winebuilds"].keys())

    def extract_and_replace_wine_build(
        self, archive_path_wine, extraction_dir_wine, target_dir_wine
    ):
        if os.path.exists(extraction_dir_wine):
            shutil.rmtree(extraction_dir_wine)

        with tarfile.open(archive_path_wine, "r:xz") as tar:
            tar.extractall(path=extraction_dir_wine)

        extracted_subfolder = os.path.join(
            extraction_dir_wine, os.listdir(extraction_dir_wine)[0]
        )

        for item in os.listdir(extracted_subfolder):
            target_item_path = os.path.join(target_dir_wine, item)

            if os.path.isdir(target_item_path):
                shutil.rmtree(target_item_path)

        for item in os.listdir(extracted_subfolder):
            item_path = os.path.join(extracted_subfolder, item)
            target_item_path = os.path.join(target_dir_wine, item)

            if os.path.isdir(item_path):
                shutil.copytree(item_path, target_item_path)
            else:
                shutil.copy2(item_path, target_item_path)

        shutil.rmtree(extracted_subfolder)

    def install_dxvk_code(self, dxvk_version, game_installed_folder):
        dst_path = os.path.join(
            game_installed_folder, "wine", "prefix", "drive_c", "windows"
        )
        tmp_path = "dxvk-tmp"
        url = "https://github.com/doitsujin/dxvk/releases/download/v{0}/dxvk-{0}.tar.gz".format(
            dxvk_version
        )
        filename = os.path.basename(url)
        urllib.request.urlretrieve(url, filename)

        with tarfile.open(filename, "r:gz") as tar:
            tar.extractall(tmp_path)

        for arch in ["x64", "x32"]:
            src_path = os.path.join(tmp_path, "dxvk-{0}".format(dxvk_version), arch)
            dst_path_arch = os.path.join(
                dst_path, "system32" if arch == "x64" else "syswow64"
            )

            if not os.path.exists(dst_path_arch):
                os.makedirs(dst_path_arch)

            for file_name in os.listdir(src_path):
                if file_name.endswith(".dll"):
                    src_file = os.path.join(src_path, file_name)
                    dst_file = os.path.join(dst_path_arch, file_name)
                    shutil.copy2(src_file, dst_file)

        os.remove(filename)
        shutil.rmtree(tmp_path)

    def install_richpresence_code(self, game_installed_folder):
        rpcUrl = "https://github.com/kassindornelles/league-rpc-linux/archive/refs/heads/main.zip"
        rpcFilename = os.path.basename(rpcUrl)
        urllib.request.urlretrieve(rpcUrl, rpcFilename)

        with zipfile.ZipFile(rpcFilename) as rpcZip:
            rpcZip.extractall()

        os.remove(rpcFilename)
        subprocess.run(
            ["python3", "-m", "venv", os.path.join(self.game_rpc_folder, "venv")]
        )
        subprocess.run(
            [
                os.path.join(self.game_rpc_folder, "venv", "bin", "pip"),
                "install",
                "-r",
                os.path.join(self.game_rpc_folder, "requirements.txt"),
            ]
        )

    def launchleague(self, installer):
        self.launchLeagueinstalled.setEnabled(False)
        self.uninstallLeaguebutton.setEnabled(False)
        self.stackedWidget.setCurrentWidget(self.gamemanager)
        os.chdir(self.game_installed_folder)

        env_vars_file_path = os.path.join(self.game_installed_folder, "env_vars.json")
        with open(env_vars_file_path, "r") as env_vars_file:
            env_vars = json.load(env_vars_file)
            game_settings = env_vars.get("game_settings", {})
            gamemode_value = int(game_settings.get("Gamemode", "0"))
            richpresence_value = int(game_settings.get("Richpresence", "0"))

        if richpresence_value == 1:
            richPresenceLaunch = subprocess.Popen(
                [
                    os.path.join(self.game_rpc_folder, "venv", "bin", "python3"),
                    os.path.join(self.game_rpc_folder, "main.py"),
                ]
            )
            print("Using Rich Presence.")
        else:
            print("Not using Rich Presence.")

        if gamemode_value == 1:
            process = subprocess.Popen(
                [
                    "gamemoderun",
                    "python3",
                    "/usr/share/lol-for-linux-installer/launch-script.py",
                ]
            )
            print("Using gamemode.")
        else:
            process = subprocess.Popen(
                ["python3", "/usr/share/lol-for-linux-installer/launch-script.py"]
            )
            print("Not using gamemode.")

        self.hide()
        process.wait()

        if not self.is_process_running("RiotClientServices.exe"):
            self.launchLeagueinstalled.setEnabled(True)
            self.uninstallLeaguebutton.setEnabled(True)
            self.show()
            pass

    def is_process_running(self, process_name):
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] == process_name:
                return True
        return False

    def regionWidget(self):
        self.stackedWidget.setCurrentWidget(self.region)

    def optionsWidget(self):
        self.stackedWidget.setCurrentWidget(self.options)

    def open_github(self):
        url = "https://github.com/kassindornelles/lol-for-linux-installer/issues"
        QDesktopServices.openUrl(QUrl(url))

    def uninstall_game(self):
        home_dir = os.path.expanduser("~")
        user_local_share = os.path.join(home_dir, ".local/share")
        user_config_folder = os.path.join(home_dir, ".config")
        json_file_path = os.path.join(user_config_folder, "league_install_path.json")

        try:
            # Read the JSON file and get the game_main_dir value
            with open(json_file_path, "r") as infile:
                data = json.load(infile)
                game_main_dir = data["game_main_dir"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to read JSON file: {e}")

        try:
            shutil.rmtree(game_main_dir)
        except FileNotFoundError:
            print(f"Directory {self.game_installed_folder} does not exist")

        try:
            os.remove(json_file_path)
        except FileNotFoundError:
            print(f"File {json_file_path} does not exist")

        QApplication.quit()

    def cancel_installation(self):
        pid = os.getpid()
        children = psutil.Process(pid).children(recursive=True)
        for child in children:
            child.send_signal(signal.SIGTERM)
        os.kill(pid, signal.SIGTERM)

    def addPlainText(self, text: str):
        self.textOuput.appendPlainText(text)

    def setup_logger(self):
        handler = GuiLogHandler(self)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        handler.new_record.connect(self.textOutput.append)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            Formatter("%(levelname)s: %(message)s\n", "%d/%m/%Y %H:%M:%S")
        )
        stream_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(stream_handler)


    def get_installation_directory(self):
        game_main_dir = QFileDialog.getExistingDirectory(
            self, "Where do you want to install the game?"
        )

        if not game_main_dir:
            return None

        game_main_dir = os.path.join(game_main_dir, "league-of-legends")

        if os.path.exists(game_main_dir):
            try:
                shutil.rmtree(game_main_dir)
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"Error: {e}")
                msg.setWindowTitle("Error")
                msg.exec_()
                return None

        try:
            os.makedirs(game_main_dir)
        except PermissionError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Permission Error: {e}")
            msg.setWindowTitle("Permission Error")
            msg.exec_()
            return None

        return game_main_dir

    def installer_code(self):
        self.game_main_dir = self.get_installation_directory()

        if not self.game_main_dir:
            return

        self.setup_ui_for_installation()

        region_map = {
            "BR (BR1) - Brazil": "br",
            "LAN (LA1) - Latin America North": "la1",
            "LAS (LA2) - Latin America South": "la2",
            "NA (NA1) - North America": "na",
            "OCE (OCE/OC1) - Oceania": "oc1",
            "RU (RU1) - Russia": "ru",
            "EUW (EUW1) - Europe West": "euw",
            "EUNE (EUN1) - Europe Nordic & East": "eune",
            "TW (TW2) - Taiwan": "tw2",
            "TR (TR1) - Turkey": "tr",
            "JP (JP1) - Japan": "jp",
            "KR (KR) - Republic of Korea": "kr",
        }

        selected_lang = self.languageComboBox.currentText()
        game_link = "https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.{}.exe"
        region = region_map.get(selected_lang, "na")
        game_region_link = game_link.format(region)

        self.setup_logger()
        self.update_text_output_scrollbar()

        self.copy_env_vars_file()
        self.update_dri_prime_setting()
        self.update_nvidia_hybrid_setting()
        self.start_installation_thread(game_region_link)

    def setup_ui_for_installation(self):
        self.cancelButton.show()
        self.cancelButton.setEnabled(True)
        self.welcomelabel.setText("We are installing the game for you...")
        self.install_button.setEnabled(False)
        self.languageComboBox.setEnabled(False)
        self.regionLabel.setEnabled(False)
        self.checkPrime.setEnabled(False)
        self.stackedWidget.setCurrentWidget(self.installing)

    def update_text_output_scrollbar(self):
        scrollbar = self.textOutput.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def copy_env_vars_file(self):
        try:
            shutil.copy(
                "env_vars.json", os.path.join(self.game_main_dir, "env_vars.json")
            )
            os.chdir(self.game_main_dir)
        except:
            shutil.copy(
                "/usr/share/lol-for-linux-installer/env_vars.json",
                os.path.join(self.game_main_dir, "env_vars.json"),
            )
            os.chdir(self.game_main_dir)

    def update_dri_prime_setting(self):
        with open("env_vars.json", "r") as f:
            data = json.load(f)

        game_launcher_options = data.get("game_launcher_options", {})

        if self.checkPrime.isChecked():
            game_launcher_options["DRI_PRIME"] = "1"
        else:
            game_launcher_options.pop("DRI_PRIME", None)

        data["game_launcher_options"] = game_launcher_options

        with open("env_vars.json", "w") as f:
            json.dump(data, f, indent=4)

    def update_nvidia_hybrid_setting(self):
        with open("env_vars.json", "r") as f:
            data = json.load(f)

        game_launcher_options = data.get("game_launcher_options", {})

        if self.Checknvidiahybrid.isChecked():
            new_vars = {
                "NV_PRIME_RENDER_OFFLOAD": "1",
                "__GLX_VENDOR_LIBRARY_NAME": "nvidia",
                "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/nvidia_icd.json",
                "VK_LAYER_NV_optimus": "NVIDIA_only",
            }

            game_launcher_options.update(new_vars)
        else:
            vars_to_remove = [
                "NV_PRIME_RENDER_OFFLOAD",
                "__GLX_VENDOR_LIBRARY_NAME",
                "VK_ICD_FILENAMES",
                "VK_LAYER_NV_optimus",
            ]

            for var_name in vars_to_remove:
                game_launcher_options.pop(var_name, None)

        data["game_launcher_options"] = game_launcher_options

        with open("env_vars.json", "w") as f:
            json.dump(data, f, indent=4)

    def start_installation_thread(self, game_region_link):
        self.thread = QThread()
        self.worker = Worker(self.game_main_dir, game_region_link)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.finish_installation)
        self.thread.start()
        self.thread.quit()

    def finish_installation(self):
        self.read_installed_folder()
        self.stackedWidget.setCurrentWidget(self.gamemanager)
        installer.hide()
        QApplication.quit()



class Worker(QObject):
    def __init__(self, game_main_dir, game_region_link):
        super().__init__()
        self.game_main_dir = game_main_dir
        self.game_region_link = game_region_link

    def run(self):
        leagueinstaller_code.league_install_code(
            self.game_main_dir, self.game_region_link
        )


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName("lolforlinuxinstaller")
    if os.getuid() == 0:
        msg_box = QMessageBox()
        msg_box.setText("Don't run this as sudo user")
        msg_box.exec_()
        sys.exit(1)

    installer = Installer()
    installer.show()
    sys.exit(app.exec_())
